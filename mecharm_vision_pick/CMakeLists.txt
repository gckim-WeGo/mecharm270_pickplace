cmake_minimum_required(VERSION 3.8)
project(mecharm_vision_pick)

find_package(ament_cmake_python REQUIRED)
find_package(rosidl_default_generators REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/Tag.msg"
  "msg/TagArray.msg"
  "action/RobotCommand.action"
)

ament_package()