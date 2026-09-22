# CraneAero Perception & Guidance System (Go AERO 2026)

## Overview
Real-time sensor fusion pipeline for autonomous UAS obstacle detection and situational awareness. 
Integrates radar (long-range) and stereo camera (dense depth) into unified 3D occupancy mapping 
for collision avoidance in GPS-denied environments.

**Competition:** Go AERO Emergency Response Challenge 2026  
**Platform:** NVIDIA Jetson TX2 | ROS2 | Gazebo  
**Team:** Cranfield UIAS (6 members, 3 sub-teams)

## System Architecture

- **Sensor Fusion:** Amuio radar + stereo camera → point cloud alignment (TF, ROS2)
- **Processing Pipeline:** PassThrough → Decimation → Voxel Grid (sub-5ms latency)
- **Occupancy Mapping:** PCL OctoMap for 3D environment representation
- **Integration:** Pub-sub ROS2 architecture on embedded Jetson hardware

## File Structure

| Directory | Purpose |
|-----------|---------|
| `Team_sensors/` | Radar/camera driver integration, sensor calibration |
| `Team_voxel_map/` | Point cloud processing, occupancy grid generation |
| `Team_path_planning/` | Collision avoidance algorithms, path planning |
| `Simulation/` | Gazebo models & worlds for SITL testing |

## Key Results

- **End-to-end latency:** <5 ms (enables real-time obstacle avoidance)
- **Sensor coverage:** 360° situational awareness with radar + camera complementarity
- **Robustness:** Tested against static and dynamic obstacles in simulation
- **Hardware:** Runs on constrained Jetson TX2 (4GB RAM) without frame drops

## Running the System

```bash
# Build the ROS2 workspace
colcon build

# Launch the full perception pipeline
ros2 launch ... perception_full.launch

# Visualize in RViz
rviz2 -d config/perception.rviz
```

## Limitations & Future Work

- Simulation-only validation (field testing pending)
- Radar odometry not yet fused (GPS only)
- Weather robustness (rain/snow) untested

---
