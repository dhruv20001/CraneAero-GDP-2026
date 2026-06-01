insatll first :
sudo apt-get install ros-humble-octomap ros-humble-octomap-mapping ros-humble-octomap-server



Run basic octomap :


-----------New terminal 

launch camera :


    ros2 launch realsense2_camera rs_launch.py

-----------New terminal  
If pointcloud still does not publish:

    ros2 param set /camera/camera pointcloud__neon_.enable true
    
or in pc

    ros2 param set /camera/camera pointcloud.enable true

Down the cloudpoint
Enable:

    ros2 param set /camera/camera decimation_filter.enable true

Tune:

    ros2 param set /camera/camera decimation_filter.filter_magnitude 8
    
 -----------New terminal    
 
 run the octomap:
 
 ros2 run octomap_server octomap_server_node   --ros-args   -r cloud_in:=/camera/camera/depth/color/points   -p resolution:=0.1

  
 -----------New terminal    
 
 run the map visual i got the impresion this redifines what's showed no the previous one:
 
 
ros2 run octomap_server octomap_server_node --ros-args -r cloud_in:=/camera/camera/depth/color/points -p frame_id:=camera_depth_optical_frame

or :

ros2 run octomap_server octomap_server_node \
  --ros-args \
  -r cloud_in:=/camera/camera/depth/color/points \
  -p frame_id:=camera_depth_optical_frame \
  -p resolution:=0.2 \
  -p publish_frequency:=10.0 \
  -p max_range:=4.0 \
  -p pointcloud_min_z:=0.1 \
  -p pointcloud_max_z:=3.0 \
  -p filter_speckles:=true

last test jeton :
ros2 run octomap_server octomap_server_node --ros-args -r cloud_in:=/camera/camera/depth/color/points -p frame_id:=camera_depth_optical_frame -p resolution:=0.1 -p publish_frequency:=10.0 

Run with filter on:
ros2 run octomap_server octomap_server_node --ros-args -r cloud_in:=/voxel_filtered -p frame_id:=camera_link -p resolution:=0.1 -p publish_frequency:=10.0 
