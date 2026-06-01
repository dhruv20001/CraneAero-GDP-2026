#!/bin/bash
# ============================================================
#  CraneAero GDP 2026 — Simulation Launcher
#  Starts Gazebo, ArduPilot SITL, and MAVROS in 3 terminals
# ============================================================

set -e

# Load environment variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config/env.sh"

WORLD_FILE="iris_crane_world.sdf"
ROS2_WS="$SCRIPT_DIR/ros2_ws"

echo "============================================"
echo "  CraneAero Simulation Launcher"
echo "============================================"
echo ""
echo "  World  : $WORLD_FILE"
echo "  ROS2 WS: $ROS2_WS"
echo ""

# --- Terminal 1: Gazebo Harmonic ---
echo "[1/3] Launching Gazebo Harmonic..."
gnome-terminal \
  --title="[SIM] Gazebo Harmonic" \
  -- bash -c "
    source $SCRIPT_DIR/config/env.sh
    echo '>> Starting Gazebo Harmonic...'
    gz sim -v4 -r $WORLD_FILE
    exec bash
  "

sleep 3

# --- Terminal 2: ArduPilot SITL ---
echo "[2/3] Launching ArduPilot SITL..."
gnome-terminal \
  --title="[SIM] ArduPilot SITL" \
  -- bash -c "
    echo '>> Starting ArduPilot SITL (ArduCopter / gazebo-iris)...'
    sim_vehicle.py -v ArduCopter -f gazebo-iris --model JSON --map --console
    exec bash
  "

sleep 3

# --- Terminal 3: ROS 2 + MAVROS ---
echo "[3/3] Launching ROS 2 + MAVROS..."
gnome-terminal \
  --title="[SIM] MAVROS" \
  -- bash -c "
    source /opt/ros/humble/setup.bash
    source $ROS2_WS/install/setup.bash
    echo '>> Starting MAVROS (connecting to SITL on UDP 14550)...'
    ros2 launch mavros apm.launch fcu_url:=udp://localhost:14550@
    exec bash
  "

echo ""
echo "✅ All 3 simulation components launched."
echo "   Close all gnome-terminal windows to stop the simulation."
