#!/bin/bash
# Run from inside: CraneAero-GDP-2026/
# Creates the full simulation/ subdirectory structure

set -e

BASE="Simulation_all"

# --- ROS 2 workspace ---
mkdir -p $BASE/ros2_ws/src/crane_control
mkdir -p $BASE/ros2_ws/src/crane_description/{urdf,meshes,textures}
mkdir -p $BASE/ros2_ws/src/crane_gazebo/{worlds,models,plugins,launch}
mkdir -p $BASE/ros2_ws/src/crane_mission

# --- SITL ---
mkdir -p $BASE/sitl/{launch,params,scripts}

# --- ArduPilot submodule placeholder ---
mkdir -p $BASE/external/ardupilot

# --- Config ---
mkdir -p $BASE/config

# --- Environment config file ---
cat > $BASE/config/env.sh << 'EOF'
#!/bin/bash
# Source this file before launching the simulation
# source simulation/config/env.sh

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SIM_ROOT="$REPO_ROOT/simulation"

export GZ_SIM_RESOURCE_PATH=$GZ_SIM_RESOURCE_PATH:$SIM_ROOT/ros2_ws/src/crane_gazebo/worlds
export GZ_SIM_RESOURCE_PATH=$GZ_SIM_RESOURCE_PATH:$SIM_ROOT/ros2_ws/src/crane_gazebo/models

echo "[env] GZ_SIM_RESOURCE_PATH set to:"
echo "  $GZ_SIM_RESOURCE_PATH"
EOF
chmod +x $BASE/config/env.sh

# --- Main launch script ---
cat > $BASE/run_simulation.sh << 'EOF'
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
EOF
chmod +x $BASE/run_simulation.sh

# --- Placeholder README files in each package ---
for pkg in crane_control crane_description crane_gazebo crane_mission; do
  echo "# $pkg" > $BASE/ros2_ws/src/$pkg/README.md
done

echo ""
echo "✅ Simulation folder structure created under: $BASE/"
echo ""
echo "Next steps:"
echo "  1. Add ArduPilot as a git submodule:"
echo "     git submodule add https://github.com/ArduPilot/ardupilot simulation/external/ardupilot"
echo "  2. Build the ROS 2 workspace:"
echo "     cd simulation/ros2_ws && colcon build"
echo "  3. Launch the simulation:"
echo "     ./simulation/run_simulation.sh"
