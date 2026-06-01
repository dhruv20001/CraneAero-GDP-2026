#!/bin/bash
# Source this file before launching the simulation
# source simulation/config/env.sh

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SIM_ROOT="$REPO_ROOT/Simulation_all"

export GZ_SIM_RESOURCE_PATH=$GZ_SIM_RESOURCE_PATH:$SIM_ROOT/ros2_ws/src/crane_gazebo/worlds
export GZ_SIM_RESOURCE_PATH=$GZ_SIM_RESOURCE_PATH:$SIM_ROOT/ros2_ws/src/crane_gazebo/models

echo "[env] GZ_SIM_RESOURCE_PATH set to:"
echo "  $GZ_SIM_RESOURCE_PATH"
