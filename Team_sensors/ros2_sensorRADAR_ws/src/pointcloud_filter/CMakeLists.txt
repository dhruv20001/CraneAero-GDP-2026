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
find_package(PCL REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(tf2_sensor_msgs REQUIRED)

# PCL includes
include_directories(${PCL_INCLUDE_DIRS})
link_directories(${PCL_LIBRARY_DIRS})
add_definitions(${PCL_DEFINITIONS})

# Camera pass-through filter
add_executable(camera_passthrough_filter src/camera_passthrough_filter.cpp)
ament_target_dependencies(camera_passthrough_filter
  rclcpp sensor_msgs pcl_conversions pcl_ros
)
target_link_libraries(camera_passthrough_filter ${PCL_LIBRARIES})

# Radar pass-through filter
add_executable(radar_passthrough_filter src/radar_passthrough_filter.cpp)
ament_target_dependencies(radar_passthrough_filter
  rclcpp sensor_msgs pcl_conversions pcl_ros
)
target_link_libraries(radar_passthrough_filter ${PCL_LIBRARIES})

# Voxel grid filter
add_executable(voxel_grid_filter src/voxel_grid_filter.cpp)
ament_target_dependencies(voxel_grid_filter
  rclcpp sensor_msgs pcl_conversions pcl_ros
)
target_link_libraries(voxel_grid_filter ${PCL_LIBRARIES})

install(TARGETS
  camera_passthrough_filter
  radar_passthrough_filter
  voxel_grid_filter
  DESTINATION lib/${PROJECT_NAME}
)

#added this
install(DIRECTORY launch DESTINATION share/${PROJECT_NAME})

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
