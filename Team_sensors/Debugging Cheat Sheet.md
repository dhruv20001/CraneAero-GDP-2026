# 📋 Debugging Cheat Sheet
## 1. Check What's Running
```bash

# See all nodes

ros2 node list

# See all topics
ros2 topic list

# See all services
ros2 service list

# see camera data only
ros2 topic list | grep -E "accel|gyro|imu"u"


```

## 2. Check Node Connections
```bash

# Get detailed info about a specific node
ros2 node info /node_name

# Example for your EKF
ros2 node info /ekf_filter_node
```

## 3. Check Topic Data Flow
```bash

# Check publishing frequency
ros2 topic hz /topic_name

# Check bandwidth usage
ros2 topic bw /topic_name

# View live data
ros2 topic echo /topic_name

# View just one message
ros2 topic echo /topic_name --once

# See topic type and info
ros2 topic info /topic_name
```
## 4. Check Parameters
```bash

# List all parameters for a node
ros2 param list /node_name

# Get a specific parameter value
ros2 param get /node_name parameter_name

# Set a parameter (for testing)
ros2 param set /node_name parameter_name value
```
## 5. Check TF Transforms
```bash

# View entire TF tree
ros2 run tf2_tools view_frames
evince frames.pdf

# Echo specific transform
ros2 run tf2_ros tf2_echo source_frame target_frame
```

## 6. Check Logs
```bash

# View recent log messages
ros2 log list

# View logs for specific node
ros2 log dump /node_name

# Check log files
ls -la ~/.ros/log/latest/
```

## 7. Visual Debugging
```bash

# Graph of node connections
rqt_graph

# Plot topic data
rqt_plot

# Console for log messages
rqt_console
```

## 8. Test Individual Components
```bash

# Run a node alone to see errors
```bash
ros2 run package_name node_name --ros-args --log-level debug
```

## Example for EKF
```bash
ros2 run robot_localization ekf_node --ros-args --log-level debug

```

## 🎯 Your Current Debugging Checklist:

Step	Command	What to Check

1	ros2 node list | grep ekf	Is EKF running?
2	ros2 node info /ekf_filter_node	What is it subscribed to?
3	ros2 topic hz /voxel_filtered	Is data flowing to EKF?
4	ros2 param get /ekf_filter_node odom0	Is config loaded?
5	ros2 topic echo /odometry/filtered --once	Is EKF publishing?

🔧 Pro Tips:

    Pipe to grep to filter: ros2 topic list | grep imu

    Use --once to avoid flooding terminal

    Check logs at ~/.ros/log/latest/ for detailed errors

    Run with --log-level debug for verbose output

ackage_name/msg/MessageName

# Example
ros2 interface show nav_msgs/msg/Odometry

# List all interfaces
ros2 interface list

🎯 Debugging Checklist
Step	Command	What to Check
1	ros2 node list	Is your node running?
2	ros2 topic list	Are topics being published?
3	ros2 topic hz /topic	Is data flowing at expected rate?
4	ros2 node info /node	Is node subscribed to correct topics?
5	ros2 param get /node param	Are parameters loaded correctly?
6	ros2 run tf2_tools view_frames	Is TF tree complete?
7	rqt_graph	Are nodes connected properly?
8	ros2 topic echo /topic --once	Does data look valid?

🔧 Common Debugging Scenarios
    Pipe to grep to filter: ros2 topic list | grep imu

    Use --once to avoid flooding terminal

    Check logs at ~/.ros/log/latest/ for detailed errors

    Run with --log-level debug for verbose output

This systematic approach will help you pinpoint exactly where things break! 🚀


