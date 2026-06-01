


# ROS2 Sensor Fusion (RPLIDAR A2M12 + RealSense D435i)

This project runs LiDAR and Intel RealSense depth camera together in
ROS2 Humble, converts LiDAR scans to point clouds, and fuses both
sensors into a single point cloud for visualization in RViz2.

--------- FOllow The Package-----
RPLidar A2M12: https://github.com/Slamtec/sllidar_ros2

------------------------------------------------------------------------

## Requirements

-   Ubuntu 22.04\
-   ROS2 Humble\
-   rplidar_ros package\
-   realsense2_camera package\
-   Custom package: sensor_fusion_pkg

------------------------------------------------------------------------


# Run the whole systems
``` bash
cd ~/ros2_sensor_ws
colcon build --packages-select sensor_fusion_pkg
source install/setup.bash
ros2 launch sensor_fusion_pkg full_system.launch.py
```



## Running Seperate Nodes for individual testing

## 1️⃣ Start LiDAR

Terminal 1:
With Rviz
``` bash
source /opt/ros/humble/setup.bash
ros2 launch rplidar_ros view_rplidar_a2m12_launch.py
```

Without Rviz
``` bash
ros2 launch rplidar_ros rplidar_a2m12_launch.py
```

Expected: - LiDAR motor starts - `/scan` topic becomes active

Check:

``` bash
ros2 topic list | grep scan
```

------------------------------------------------------------------------

## 2️⃣ Start RealSense Camera

Terminal 2:

``` bash
source /opt/ros/humble/setup.bash
ros2 launch realsense2_camera rs_launch.py pointcloud.enable:=true
```

Expected: - Camera node starts - `/camera/camera/depth/color/points`
topic is active

------------------------------------------------------------------------

## 3️⃣ Static Transform (Sensor Integration)

Terminal 3:

``` bash
source /opt/ros/humble/setup.bash
ros2 run tf2_ros static_transform_publisher 0 0 0 0 0 0 camera_link laser
```

Note: Replace `laser` if your LiDAR frame name is different.

------------------------------------------------------------------------

## 4️⃣ Open RViz2 (Optional)

Terminal 4:

``` bash
source /opt/ros/humble/setup.bash
rviz2
```

In RViz: - Set Fixed Frame → `camera_link` - Add → `PointCloud2` -
Select topic → `/fused_cloud`

------------------------------------------------------------------------

# Build and Run Custom Nodes

## Run Lidar to Point Cloud node

``` bash
cd ~/ros2_sensor_ws
source /opt/ros/humble/setup.bash
colcon build
source install/setup.bash
ros2 run sensor_fusion_pkg lidar_to_pointcloud
```

------------------------------------------------------------------------

Converts:

    /scan  →  /lidar_points

------------------------------------------------------------------------

## Run Fusion Node

In a new terminal:

``` bash
cd ~/ros2_sensor_ws
colcon build --packages-select sensor_fusion_pkg
source install/setup.bash
ros2 run sensor_fusion_pkg fusion
```
To Run Again: 
``` bash
source install/setup.bash
ros2 run sensor_fusion_pkg fusion
```
------------------------------------------------------------------------

## Run PassThrough Filter
``` bash
cd ~/ros2_sensor_ws
colcon build --packages-select pointcloud_filter
source install/setup.bash
ros2 run pointcloud_filter passthrough_filter_node
```
------------------------------------------------------------------------

## Run Voxel Filter
``` bash
cd ~/ros2_sensor_ws
colcon build --packages-select pointcloud_filter
source install/setup.bash
ros2 run pointcloud_filter voxel_grid_filter_node
```


# Verify Topics

``` bash
ros2 topic list
```

You should see:

    /scan
    /lidar_points
    /camera/camera/depth/color/points
    /fused_cloud
    /filtered_cloud
------------------------------------------------------------------------

# System Architecture

    RPLIDAR → /scan → lidar_to_pointcloud → /lidar_points
    RealSense → /camera/.../points
    Fusion Node → /fused_cloud → /filtered_cloud → RViz2

------------------------------------------------------------------------

## Author

Dhruv Prajapati\
MSc Autonomous Vehicle Dynamics and Control
