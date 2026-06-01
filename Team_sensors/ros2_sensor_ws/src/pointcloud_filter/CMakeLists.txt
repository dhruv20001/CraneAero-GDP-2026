cmake_minimum_required(VERSION 3.8)
project(pointcloud_filter)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(pcl_conversions REQUIRED)
find_package(pcl_ros REQUIRED)
find_package(PCL REQUIRED)  # ADD THIS

include_directories(include ${PCL_INCLUDE_DIRS})  # ADD THIS
link_directories(${PCL_LIBRARY_DIRS})  # ADD THIS
add_definitions(${PCL_DEFINITIONS})  # ADD THIS

# ADD YOUR EXECUTABLE HERE (BEFORE ament_package)
add_executable(passthrough_filter_node src/passthrough_filter_node.cpp)
ament_target_dependencies(passthrough_filter_node
  rclcpp
  sensor_msgs
  pcl_conversions
)
target_link_libraries(passthrough_filter_node ${PCL_LIBRARIES})

install(TARGETS
  passthrough_filter_node
  DESTINATION lib/${PROJECT_NAME}
)

# Voxel Grid Filter node
add_executable(voxel_grid_filter_node src/voxel_grid_filter_node.cpp)
ament_target_dependencies(voxel_grid_filter_node
  rclcpp
  sensor_msgs
  pcl_conversions
)
target_link_libraries(voxel_grid_filter_node ${PCL_LIBRARIES})

install(TARGETS
  passthrough_filter_node
  voxel_grid_filter_node  # Add this
  DESTINATION lib/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
