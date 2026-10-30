#pragma once
#include <tllib/core/result.hpp>
#include <array>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <span>

namespace tllib::core {
// CPU-only, non-owning 1D/2D numeric view; never retains memory or allocates data.
// The caller must own the complete allocation for the entire lifetime of this view.
enum class DType { int32, float64 };
enum class Layout { row_major, column_major, strided };
class ArrayView final {
 public:
  static Result<ArrayView> create(std::span<const std::byte> allocation,
      std::size_t origin, DType dtype, std::span<const std::size_t> shape,
      std::span<const std::ptrdiff_t> strides) {
    return make(allocation, nullptr, origin, dtype, shape, strides);
  }
  static Result<ArrayView> create_mutable(std::span<std::byte> allocation,
      std::size_t origin, DType dtype, std::span<const std::size_t> shape,
      std::span<const std::ptrdiff_t> strides) {
    return make(allocation, allocation.data(), origin, dtype, shape, strides);
  }
  [[nodiscard]] std::size_t rank() const noexcept { return rank_; }
  [[nodiscard]] std::span<const std::size_t> shape() const noexcept { return {shape_.data(),rank_}; }
  [[nodiscard]] std::span<const std::ptrdiff_t> strides() const noexcept { return {strides_.data(),rank_}; }
  [[nodiscard]] DType dtype() const noexcept {return dtype_;}
  [[nodiscard]] Layout layout() const noexcept {return layout_;}
  [[nodiscard]] bool writable() const noexcept {return writable_ != nullptr;}
  [[nodiscard]] bool empty() const noexcept {return empty_;}
  [[nodiscard]] std::size_t itemsize() const noexcept {return dtype_==DType::int32 ? sizeof(std::int32_t):sizeof(double);}
  [[nodiscard]] const std::byte* data() const noexcept {return allocation_.empty() ? nullptr : allocation_.data()+origin_;}
  [[nodiscard]] Result<std::byte*> mutable_data() const {
    if (!writable_)return Error{ErrorCode::invalid_argument,"View is read only",{},{},{},"READ_ONLY_BUFFER"};
    return writable_+origin_;
  }
  [[nodiscard]] Result<std::size_t> byte_offset(std::span<const std::size_t> indices) const {
    if(indices.size()!=rank_ || empty_)
      return Error{ErrorCode::out_of_range,"Invalid index rank or empty view",{},{},{},"BUFFER_OUT_OF_RANGE"};
    std::size_t pos=origin_, neg=0;
    for(std::size_t i=0;i<rank_;++i) {
      if(indices[i]>=shape_[i])return Error{ErrorCode::out_of_range,"Index outside shape",{},{},{},"BUFFER_OUT_OF_RANGE"};
      const auto step=indices[i]*magnitude(strides_[i]); // checked during construction
      if(strides_[i]<0)neg+=step;
      else pos+=step;
    }
    return pos-neg;
  }
 private:
  ArrayView(std::span<const std::byte> allocation,std::byte* writable,std::size_t origin,DType dtype,
            std::size_t rank,std::array<std::size_t,2> shape,
            std::array<std::ptrdiff_t,2> strides, Layout layout,bool empty):
      allocation_(allocation),writable_(writable),origin_(origin),dtype_(dtype),
      rank_(rank),shape_(shape),strides_(strides),layout_(layout),empty_(empty){}
  static std::size_t magnitude(std::ptrdiff_t n) noexcept {
    return n<0 ? static_cast<std::size_t>(-(n+1))+1 : static_cast<std::size_t>(n);
  }
  static Result<ArrayView> make(std::span<const std::byte> alloc,std::byte* writable,
      std::size_t origin,DType dtype,std::span<const std::size_t> shape,
      std::span<const std::ptrdiff_t> strides) {
    auto fail=[](const char* message,const char* code)->Result<ArrayView> {
      return Error{ErrorCode::invalid_shape,message,{},{},{},code};
    };
    if(shape.empty() || shape.size()>2 || shape.size()!=strides.size())
      return fail("Only rank 1 or 2 with matching strides is supported","INVALID_SHAPE");
    if(origin>alloc.size())return fail("Origin outside allocation","BUFFER_OUT_OF_RANGE");
    const std::size_t itemsize=dtype==DType::int32 ? sizeof(std::int32_t) : sizeof(double);
    const std::size_t alignment=dtype==DType::int32 ? alignof(std::int32_t) : alignof(double);
    std::array<std::size_t,2> dimensions{};
    std::array<std::ptrdiff_t,2> steps{};
    bool empty=false;
    std::size_t count=1,forward=0,backward=0;
    for(std::size_t i=0;i<shape.size();++i) {
      dimensions[i]=shape[i];steps[i]=strides[i];
      if(shape[i]==0)empty=true;
      if(shape[i]>0 && count>std::numeric_limits<std::size_t>::max()/shape[i])
        return fail("Shape product overflow","SHAPE_OVERFLOW");
      count*=shape[i];
      const auto mag=magnitude(strides[i]);
      if(mag % alignment!=0)return fail("Misaligned stride","BUFFER_ALIGNMENT");
      if(shape[i]>0 && shape[i]-1>std::numeric_limits<std::size_t>::max()/ (mag==0?1:mag))
        return fail("Stride span overflow","SHAPE_OVERFLOW");
      const auto displacement=shape[i]==0 ? 0 : (shape[i]-1)*mag;
      auto& sum=strides[i]<0 ? backward:forward;
      if(displacement>std::numeric_limits<std::size_t>::max()-sum)
        return fail("Offset overflow","SHAPE_OVERFLOW");
      sum+=displacement;
    }
    if(!empty) {
      if(!alloc.data())return fail("Missing data","INVALID_BUFFER");
      if(origin<backward || forward>alloc.size()-origin || itemsize>alloc.size()-origin-forward)
        return fail("View exceeds allocation","BUFFER_OUT_OF_RANGE");
      if((reinterpret_cast<std::uintptr_t>(alloc.data())+origin)%alignment!=0)
        return fail("Misaligned data","BUFFER_ALIGNMENT");
    }
    Layout layout=Layout::strided;
    const auto row=[&] {
      if(shape.size()==1)return magnitude(steps[0])==itemsize;
      return magnitude(steps[1])==itemsize &&
             dimensions[1]<=std::numeric_limits<std::size_t>::max()/itemsize &&
             magnitude(steps[0])==dimensions[1]*itemsize;
    }();
    const auto column=shape.size()==2 && magnitude(steps[0])==itemsize &&
             dimensions[0]<=std::numeric_limits<std::size_t>::max()/itemsize &&
             magnitude(steps[1])==dimensions[0]*itemsize;
    if(row && steps[0]>=0 && (shape.size()==1 || steps[1]>=0))layout=Layout::row_major;
    else if(column && steps[0]>=0 && steps[1]>=0)layout=Layout::column_major;
    if(writable && !empty && layout==Layout::strided)
      return fail("Mutable strided/overlapping buffers are not supported","BUFFER_ALIASING");
    return ArrayView(alloc,writable,origin,dtype,shape.size(),dimensions,steps,layout,empty);
  }
  std::span<const std::byte> allocation_;
  std::byte* writable_;
  std::size_t origin_;
  DType dtype_;
  std::size_t rank_;
  std::array<std::size_t,2> shape_;
  std::array<std::ptrdiff_t,2> strides_;
  Layout layout_;
  bool empty_;
};
} // namespace tllib::core
