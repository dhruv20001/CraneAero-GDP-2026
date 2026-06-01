# Isaac ROS NVBlox — Native Setup on Jetson Orin Nano

> ROS2 Humble · JetPack 6 · Intel RealSense D435i · RPLIDAR A2M12 · NVBlox · cuVSLAM

A complete native (non-Docker) setup guide for 3D voxel mapping on a UAV using NVIDIA Isaac ROS NVBlox, built from the ground up through troubleshooting a real Jetson Orin Nano deployment.

---

## System Configuration

| Component | Details |
|-----------|---------|
| Platform | NVIDIA Jetson Orin Nano |
| JetPack | 6.x |
| ROS Distribution | ROS2 Humble |
| Depth Camera | Intel RealSense D435i |
| LiDAR | RPLIDAR A2M12 |
| Mapping | NVBlox (Isaac ROS) |
| SLAM | Isaac ROS Visual SLAM (cuVSLAM) |
| Workspace | `~/mnt/nova_ssd/workspaces/isaac_ros-dev` |

---

## Table of Contents

1. [Environment Setup](#1-environment-setup)
2. [librealsense Source Build](#2-librealsense-source-build)
3. [realsense-ros Build from Source](#3-realsense-ros-build-from-source)
4. [RealSense Camera Launch](#4-realsense-camera-launch)
5. [Isaac ROS NVBlox Setup](#5-isaac-ros-nvblox-setup)
6. [Launch NVBlox with RealSense](#6-launch-nvblox-with-realsense)
7. [Known Issues & Solutions](#7-known-issues--solutions)
8. [Key File Paths](#8-key-file-paths)

---

## 1. Environment Setup

### 1.1 Workspace Variable

```bash
export ISAAC_ROS_WS=~/mnt/nova_ssd/workspaces/isaac_ros-dev
echo 'export ISAAC_ROS_WS=~/mnt/nova_ssd/workspaces/isaac_ros-dev' >> ~/.bashrc
source ~/.bashrc
```

### 1.2 Add CUDA to PATH

NVBlox requires `nvcc` at build time. JetPack 6 installs CUDA to `/usr/local/cuda/bin`:

```bash
export CUDACXX=/usr/local/cuda/bin/nvcc
export PATH=/usr/local/cuda/bin:$PATH
echo 'export CUDACXX=/usr/local/cuda/bin/nvcc' >> ~/.bashrc
echo 'export PATH=/usr/local/cuda/bin:$PATH' >> ~/.bashrc
```

---

## 2. librealsense Source Build

The apt version of librealsense on arm64/JetPack does not include the USB backend needed for the D435i. Build from source instead.

### 2.1 Install Build Dependencies

```bash
sudo apt-get install -y git libssl-dev libusb-1.0-0-dev libudev-dev pkg-config \
  libgtk-3-dev cmake build-essential libglfw3-dev libgl1-mesa-dev libglu1-mesa-dev
```

### 2.2 Clone and Build librealsense 2.57.6

```bash
cd ~
git clone https://github.com/IntelRealSense/librealsense.git
cd librealsense
git checkout v2.57.6

mkdir build && cd build
cmake .. \
  -DCMAKE_BUILD_TYPE=Release \
  -DFORCE_RSUSB_BACKEND=ON \
  -DBUILD_PYTHON_BINDINGS=OFF \
  -DBUILD_EXAMPLES=OFF

make -j$(nproc)
sudo make install
sudo ldconfig
```

### 2.3 Install udev Rules

```bash
sudo cp ../config/99-realsense-libusb.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules && sudo udevadm trigger
```

### 2.4 Verify

```bash
rs-enumerate-devices
```

> Expected: Intel RealSense D435I listed with serial number and firmware version.

---

## 3. realsense-ros Build from Source

The `ros2-master` branch requires librealsense 2.57+ API features (safety streams, occupancy grids) not present in the apt headers. Use tag `4.54.1` which is compatible with both 2.56.x and 2.57.x.

### 3.1 Clone Compatible Branch

```bash
cd $ISAAC_ROS_WS/src
git clone https://github.com/IntelRealSense/realsense-ros.git \
  -b 4.54.1 --depth 1
```

### 3.2 Build

Use `CMAKE_PREFIX_PATH` to prioritize the source-built librealsense over any apt-installed version:

```bash
cd $ISAAC_ROS_WS
colcon build --symlink-install \
  --packages-select realsense2_camera realsense2_camera_msgs realsense2_description \
  --cmake-args \
    -DCMAKE_PREFIX_PATH="/usr/local;/opt/ros/humble"

source $ISAAC_ROS_WS/install/setup.bash
```

> **Note:** The CMake warning about `realsense2_DIR` being unused is harmless — the library is found via `CMAKE_PREFIX_PATH`.

> **Note:** The runtime warning `Built with LibRealSense v2.56.4, Running with v2.57.6` is also harmless — minor version difference, API compatible.

---

## 4. RealSense Camera Launch

### 4.1 Basic Test Launch

```bash
source /opt/ros/humble/setup.bash
source $ISAAC_ROS_WS/install/setup.bash

ros2 launch realsense2_camera rs_launch.py
```

### 4.2 Full Launch with NVBlox Parameters

Enables aligned depth, pointcloud, and IMU — all required by NVBlox:

```bash
ros2 run realsense2_camera realsense2_camera_node \
  --ros-args \
  -r __ns:=/camera \
  -r __node:=camera \
  -p enable_color:=true \
  -p enable_depth:=true \
  -p enable_gyro:=true \
  -p enable_accel:=true \
  -p unite_imu_method:=1 \
  -p align_depth.enable:=true \
  -p pointcloud.enable:=true \
  -p depth_module.profile:=848x480x30 \
  -p rgb_camera.profile:=848x480x30 \
  -p publish_tf:=true
```

### 4.3 Verify Topics

```bash
ros2 topic list | grep -E "points|aligned|color|depth"
ros2 topic hz /camera/color/image_raw
ros2 topic hz /camera/depth/image_rect_raw
```

Expected topics for NVBlox:

```
/camera/color/image_raw
/camera/color/camera_info
/camera/depth/image_rect_raw
/camera/aligned_depth_to_color/image_raw
/camera/points
/camera/imu
```

---

## 5. Isaac ROS NVBlox Setup

### 5.1 Install Isaac ROS apt Packages

```bash
sudo apt-get install -y \
  ros-humble-isaac-ros-realsense \
  ros-humble-isaac-ros-visual-slam
```

### 5.2 Clone isaac_ros_nvblox Source

The `realsense_splitter` node is not included in the apt package — must build from source:

```bash
cd $ISAAC_ROS_WS/src
git clone https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_nvblox.git --depth 1
```

### 5.3 Enable realsense_splitter

The splitter is disabled by default in the source tree via a `COLCON_IGNORE` file. Remove it:

```bash
rm $ISAAC_ROS_WS/src/isaac_ros_nvblox/nvblox_examples/realsense_splitter/COLCON_IGNORE
```

### 5.4 Install Build Dependencies

```bash
sudo apt-get install -y nlohmann-json3-dev ros-humble-cv-bridge

cd $ISAAC_ROS_WS
rosdep install -i --from-path src/isaac_ros_nvblox --rosdistro humble -y \
  --skip-keys "isaac_ros_test isaac_ros_test_cmake"
```

### 5.5 Initialize Git Submodules

`nvblox_ros` depends on `nvblox_core` which is a git submodule and is not cloned by default:

```bash
cd $ISAAC_ROS_WS/src/isaac_ros_nvblox
git submodule update --init --recursive

# Verify
ls nvblox_ros/nvblox_core/
```

### 5.6 Remove Conflicting apt Packages

The apt nvblox packages are version 3.x while the source repo is 4.x — they conflict:

```bash
sudo apt-get remove -y \
  ros-humble-nvblox-examples-bringup \
  ros-humble-nvblox-msgs \
  ros-humble-isaac-ros-nvblox \
  ros-humble-nvblox-ros-python-utils
```

### 5.7 Remove All COLCON_IGNORE Files

```bash
find $ISAAC_ROS_WS/src/isaac_ros_nvblox -name "COLCON_IGNORE" -delete
```

### 5.8 Build NVBlox Packages in Order

```bash
cd $ISAAC_ROS_WS

colcon build --symlink-install \
  --packages-select \
    nvblox_msgs \
    nvblox_ros_python_utils \
    realsense_splitter \
    nvblox_ros_common \
    nvblox_rviz_plugin \
    nvblox_ros \
    semantic_label_conversion \
    nvblox_examples_bringup \
  --cmake-args \
    -DCMAKE_PREFIX_PATH="/usr/local;/opt/ros/humble" \
    -DCMAKE_CUDA_COMPILER=/usr/local/cuda/bin/nvcc

source $ISAAC_ROS_WS/install/setup.bash
```

### 5.9 Verify

```bash
ros2 pkg list | grep nvblox
ros2 pkg list | grep splitter
```

---

## 6. Launch NVBlox with RealSense

> **Important:** Do NOT launch the RealSense camera node separately. `nvblox_examples_bringup` launches the camera, cuVSLAM, and RViz internally. Running them in parallel causes USB conflicts.

### 6.1 Kill Any Running Processes

```bash
sudo pkill -f realsense2_camera
sudo pkill -f visual_slam
sleep 3
```

### 6.2 Launch

```bash
source /opt/ros/humble/setup.bash
source $ISAAC_ROS_WS/install/setup.bash

ros2 launch nvblox_examples_bringup realsense_example.launch.py
```

### 6.3 Verify All Nodes Running

In a second terminal:

```bash
source /opt/ros/humble/setup.bash
source $ISAAC_ROS_WS/install/setup.bash

ros2 node list
ros2 topic hz /nvblox_node/mesh
ros2 topic hz /visual_slam/tracking/odometry
ros2 topic hz /camera0/realsense_splitter_node/output/infra_1
```

Expected nodes:

| Node | Role |
|------|------|
| `/camera0/camera` | RealSense driver |
| `/camera0/realsense_splitter_node` | IR frame splitter for cuVSLAM |
| `/visual_slam_node` | cuVSLAM pose estimation |
| `/nvblox_node` | 3D voxel map builder |
| `/rviz` | Visualization |

### 6.4 Debug: TF Frame Issues

If nvblox reports `Lookup transform failed for frame camera0_link`, cuVSLAM is not publishing odometry. The splitter must be running and feeding IR frames to cuVSLAM:

```bash
# Confirm splitter is publishing IR frames
ros2 topic hz /camera0/realsense_splitter_node/output/infra_1
ros2 topic hz /camera0/realsense_splitter_node/output/infra_2

# Check cuVSLAM tracking status
ros2 topic echo /visual_slam/status --once

# View full TF tree
ros2 run tf2_tools view_frames
```

---

## 7. Known Issues & Solutions

| Issue | Solution |
|-------|----------|
| `RS2_USB_STATUS_BUSY` at launch | Kill all realsense processes: `sudo pkill -f realsense`, then relaunch |
| `control_transfer` warnings | Benign — USB backend polling for hardware metadata. Does not affect streaming |
| Version mismatch warning (2.56.4 vs 2.57.6) | Harmless — minor version difference, API compatible |
| `No CMAKE_CUDA_COMPILER` | `export CUDACXX=/usr/local/cuda/bin/nvcc` before building |
| `realsense_splitter` not found by colcon | `COLCON_IGNORE` file present — delete it and rebuild |
| `nvblox_core` submodule missing | Run `git submodule update --init --recursive` inside `isaac_ros_nvblox` |
| Two `/visual_slam_node` instances | Do not run `isaac_ros_visual_slam.launch.py` separately — it is included in `nvblox_examples_bringup` |
| `odom` frame does not exist | cuVSLAM not tracking. Confirm splitter IR topics are publishing |
| colcon silently ignores `realsense_splitter` | `COLCON_IGNORE` file present — delete it |
| apt nvblox v3.x conflicts with source v4.x | Remove apt packages before building from source |
| `nvblox_examples_bringup` fails to find `nvblox_ros` | Build `nvblox_ros` first, then `nvblox_examples_bringup` |
| `realsense_splitter` fails to load in container | Version mismatch between splitter and bringup — ensure both are from the same source tag |

---

## 8. Key File Paths

```
# Workspace
$ISAAC_ROS_WS = ~/mnt/nova_ssd/workspaces/isaac_ros-dev

# Source-built librealsense
/usr/local/lib/librealsense2.so.2.57.6
/usr/local/lib/cmake/realsense2/

# udev rules
/etc/udev/rules.d/99-realsense-libusb.rules

# NVBlox launch files
$(ros2 pkg prefix nvblox_examples_bringup)/share/nvblox_examples_bringup/launch/

# NVBlox RealSense emitter config
$(ros2 pkg prefix nvblox_examples_bringup)/share/nvblox_examples_bringup/config/sensors/realsense_emitter_flashing.yaml

# realsense_splitter source
$ISAAC_ROS_WS/src/isaac_ros_nvblox/nvblox_examples/realsense_splitter/

# CUDA compiler
/usr/local/cuda/bin/nvcc

# Isaac ROS apt repo
/etc/apt/sources.list.d/nvidia-isaac-ros.list
```

---

## Architecture Overview

```
RealSense D435i
    │
    ├── /camera0/color/image_raw          ──► nvblox_node (color fusion)
    ├── /camera0/depth/image_rect_raw     ──► nvblox_node (depth integration)
    ├── /camera0/infra1/image_rect_raw ─┐
    └── /camera0/infra2/image_rect_raw ─┤
                                         │
                              realsense_splitter_node
                              (emitter flash sync)
                                         │
                    ┌────────────────────┴──────────────────┐
                    │                                       │
          infra_1 (IR, no projector)           infra_2 (IR, no projector)
                    │                                       │
                    └──────────► visual_slam_node ◄─────────┘
                                 (cuVSLAM stereo)
                                        │
                                   /tf odom
                                        │
                                  nvblox_node
                                  (3D voxel map)
                                        │
                                  /nvblox_node/mesh
                                        │
                                      RViz2
```

The `realsense_splitter_node` is critical — it synchronizes with the IR projector flash cycle so that cuVSLAM receives clean stereo IR frames without structured light interference.

---

*ROS2 Humble · JetPack 6 · Jetson Orin Nano*
