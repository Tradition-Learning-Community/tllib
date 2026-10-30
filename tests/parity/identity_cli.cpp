#include <tllib/core/identity.hpp>
#include <iostream>
#include <string>
#include <string_view>

int main(int argc,char** argv){
  if(argc!=3)return 2;
  const std::string_view kind(argv[1]),input(argv[2]);
  if(kind=="feature"){
    auto result=tllib::core::FeatureId::parse(input);
    if(!result){std::cout<<"ERROR\tINVALID_IDENTIFIER\n";return 0;}
    std::cout<<"OK\t"<<result.value_if()->str()<<"\n";return 0;
  }
  if(kind=="domain"){
    auto result=tllib::core::DomainId::parse(input);
    if(!result){std::cout<<"ERROR\tINVALID_IDENTIFIER\n";return 0;}
    std::cout<<"OK\t"<<result.value_if()->str()<<"\n";return 0;
  }
  if(kind=="execution_status"){
    auto result=tllib::core::parse_execution_status(input);
    if(!result){std::cout<<"ERROR\tINVALID_ARGUMENT\n";return 0;}
    std::cout<<"OK\t"<<input<<"\n";return 0;
  }
  return 2;
}
