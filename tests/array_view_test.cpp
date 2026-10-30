#include <tllib/core/array_view.hpp>
#include <array>
#include <cassert>
#include <limits>
#include <cstddef>
using tllib::core::ArrayView;
using tllib::core::DType;
using tllib::core::Layout;
int main(){
  std::array<double,6> matrix{};
  std::span<std::byte> bytes{reinterpret_cast<std::byte*>(matrix.data()),sizeof(matrix)};
  const std::array<std::size_t,2> shape{2,3};
  const std::array<std::ptrdiff_t,2> row{24,8},column{8,16};
  auto a=ArrayView::create_mutable(bytes,0,DType::float64,shape,row);
  assert(a && a.value_if()->layout()==Layout::row_major && a.value_if()->writable());
  const std::array<std::size_t,2> idx{1,2};
  const auto off=a.value_if()->byte_offset(idx);
  assert(off && *off.value_if()==40);
  auto b=ArrayView::create(bytes,0,DType::float64,shape,column);
  assert(b && b.value_if()->layout()==Layout::column_major && !b.value_if()->mutable_data());
  assert(*b.value_if()->byte_offset(idx).value_if()==40);
  auto c=ArrayView::create_mutable(bytes,0,DType::float64,shape,column);
  assert(c && c.value_if()->writable());
  const std::array<std::ptrdiff_t,2> stride{8,8};
  assert(!ArrayView::create_mutable(bytes,0,DType::float64,shape,stride));
  assert(ArrayView::create(bytes,0,DType::float64,shape,stride));
  const std::array<std::ptrdiff_t,2> reverse{-24,-8};
  auto d=ArrayView::create(bytes,40,DType::float64,shape,reverse);
  assert(d && *d.value_if()->byte_offset(idx).value_if()==0);
  assert(!ArrayView::create(bytes,0,DType::float64,shape,reverse));
  const std::array<std::size_t,2> badidx{2,0};
  assert(!a.value_if()->byte_offset(badidx));
  const std::array<std::size_t,2> huge{std::numeric_limits<std::size_t>::max(),2};
  assert(!ArrayView::create(bytes,0,DType::float64,huge,row));
  const std::array<std::size_t,2> badshape{3,3};
  assert(!ArrayView::create(bytes,0,DType::float64,badshape,row));
  const std::array<std::size_t,1> one{6};
  const std::array<std::ptrdiff_t,1> step{8};
  assert(ArrayView::create(bytes,0,DType::float64,one,step));
  assert(!ArrayView::create(bytes,1,DType::float64,one,step));
  const std::array<std::size_t,1> empty{0};
  assert(ArrayView::create(bytes,0,DType::float64,empty,step));
  return 0;
}
