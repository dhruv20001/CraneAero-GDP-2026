# 🚁 CraneAero GDP 2026 — Simulation Environment

> **Location in repo:** `CraneAero-GDP-2026/simulation/`  
> This folder is a self-contained simulation stack. It lives as a subdirectory of the main project repo.

---

## 📐 Overview

This simulation environment integrates four components that must all run simultaneously:

| Component | Role |
|---|---|
| **Gazebo Harmonic** | 3D physics simulation & rendering |
| **ArduPilot SITL** | Flight dynamics & autopilot firmware |
| **ROS 2 (Humble)** | Middleware, MAVROS bridge, mission logic |
| **Custom assets** | Worlds, models, SDF, URDF, meshes |

---

## 📁 Folder Structure

```
simulation/
│
├── README.md                    ← You are here
│
├── ros2_ws/
│   └── src/
│       ├── crane_control/       ← ROS 2 control nodes
│       ├── crane_description/   ← URDF, meshes, textures
│       ├── crane_gazebo/        ← Worlds, models, SDF, plugins
│       │   ├── worlds/
│       │   │   └── iris_crane_world.sdf
│       │   └── models/
│       └── crane_mission/       ← Mission logic, waypoints
│
├── sitl/
│   ├── launch/                  ← ArduPilot launch configs
│   ├── params/                  ← Flight parameter files (.param)
│   └── scripts/                 ← Helper scripts
│
├── external/
│   └── ardupilot/               ← Git submodule (ArduPilot source)
│
├── config/
│   └── env.sh                   ← Environment variables (GZ_SIM_RESOURCE_PATH etc.)
│
└── run_simulation.sh            ← 🚀 One-command launch script
```

---

## ⚙️ Prerequisites

Make sure the following are installed before proceeding:

- **Ubuntu 22.04** (recommended)
- **ROS 2 Humble** — [Install guide](https://docs.ros.org/en/humble/Installation.html)
- **Gazebo Harmonic** — [Install guide](https://gazebosim.org/docs/harmonic/install)
- **ArduPilot + SITL** — [Install guide](https://ardupilot.org/dev/docs/setting-up-sitl-on-linux.html)
- **MAVROS** (ROS 2 version):
  ```bash
  sudo apt install ros-humble-mavros ros-humble-mavros-extras
  ros2 run mavros install_geographiclib_datasets.sh
  ```
- **gnome-terminal** (used by the launch script):
  ```bash
  sudo apt install gnome-terminal
  ```

---

## 🏗️ Building the Repo Structure

Run this once to scaffold the entire simulation directory from scratch:

```bash
#!/bin/bash
# Run from inside: CraneAero-GDP-2026/
# Creates the full simulation/ subdirectory structure

set -e

BASE="simulation"

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
```

Save the above as `setup_simulation.sh` at the root of your repo, then:

```bash
chmod +x setup_simulation.sh
./setup_simulation.sh
```

---

## 🔧 First-Time Setup (After Cloning)

```bash
# 1. Clone the main repo
git clone https://github.com/your-org/CraneAero-GDP-2026.git
cd CraneAero-GDP-2026

# 2. Init ArduPilot submodule
git submodule update --init --recursive

# 3. Set up ArduPilot SITL tools
cd simulation/external/ardupilot
Tools/environment_install/install-prereqs-ubuntu.sh -y
. ~/.profile
cd ../../..

# 4. Build ROS 2 workspace
cd simulation/ros2_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
cd ../..
```

---

## 🚀 Launching the Simulation

### Quick launch (all 3 components at once)

```bash
./simulation/run_simulation.sh
```

This opens **3 separate terminals** automatically:

| Terminal | Title | What it runs |
|---|---|---|
| 1 | `[SIM] Gazebo Harmonic` | `gz sim -v4 -r iris_crane_world.sdf` |
| 2 | `[SIM] ArduPilot SITL` | `sim_vehicle.py -v ArduCopter -f gazebo-iris --model JSON --map --console` |
| 3 | `[SIM] MAVROS` | `ros2 launch mavros apm.launch fcu_url:=udp://localhost:14550@` |

### Manual launch (step by step)

If you want full control, open 3 terminals manually:

**Terminal 1 — Gazebo**
```bash
source simulation/config/env.sh
gz sim -v4 -r iris_crane_world.sdf
```

**Terminal 2 — ArduPilot SITL** *(wait ~5s after Gazebo starts)*
```bash
sim_vehicle.py -v ArduCopter -f gazebo-iris --model JSON --map --console
```

**Terminal 3 — ROS 2 + MAVROS** *(wait ~5s after SITL starts)*
```bash
source /opt/ros/humble/setup.bash
source simulation/ros2_ws/install/setup.bash
ros2 launch mavros apm.launch fcu_url:=udp://localhost:14550@
```

---

## 🌍 Environment Variables

Always set these before launching Gazebo (handled automatically by `run_simulation.sh`):

```bash
source simulation/config/env.sh
```

Or manually:

```bash
export GZ_SIM_RESOURCE_PATH=$GZ_SIM_RESOURCE_PATH:/path/to/simulation/ros2_ws/src/crane_gazebo/worlds
export GZ_SIM_RESOURCE_PATH=$GZ_SIM_RESOURCE_PATH:/path/to/simulation/ros2_ws/src/crane_gazebo/models
```

This ensures Gazebo finds all custom worlds and models **without touching system files** in `/usr/share/gazebo/`.

---

## 🐛 Troubleshooting

**Gazebo can't find the world file**
→ Check that `GZ_SIM_RESOURCE_PATH` includes the `worlds/` folder. Run `source simulation/config/env.sh` first.

**MAVROS can't connect to SITL**
→ Make sure ArduPilot SITL is fully started (look for `APM: EKF3 IMU0 is using GPS` in the SITL console) before launching MAVROS.

**`sim_vehicle.py` not found**
→ Run `. ~/.profile` or add ArduPilot tools to your PATH:
```bash
export PATH=$PATH:$HOME/CraneAero-GDP-2026/simulation/external/ardupilot/Tools/autotest
```

**colcon build fails**
→ Make sure all ROS 2 dependencies are installed: `rosdep install --from-paths src --ignore-src -r -y`

---

## 📌 Port Reference

| Port | Protocol | Used by |
|---|---|---|
| `14550` | UDP | MAVLink — SITL ↔ MAVROS |
| `14551` | UDP | MAVLink — SITL ↔ GCS (MAVProxy/QGC) |
| `9002` | UDP | Gazebo ↔ ArduPilot JSON plugin |

---

## 👥 Contributors

CraneAero GDP 2026 team — Cranfield University