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
Simulation_all/
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



## 🔧 First-Time Setup (After Cloning)

```bash
# 1. Clone the main repo
git clone https://github.com/ethandoestech/CraneAero-GDP-2026.git
cd CraneAero-GDP-2026

# 2. Init ArduPilot submodule
git submodule update --init --recursive

# 3. Set up ArduPilot SITL tools
cd Simulation_all/external/ardupilot
Tools/environment_install/install-prereqs-ubuntu.sh -y
. ~/.profile
cd ../../..

# 4. Build ROS 2 workspace
cd Simulation_all/ros2_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
cd ../..
```

---
## 🌍 Environment Variables

Always set these before launching Gazebo (handled automatically by `run_simulation.sh`):

```bash
source Simulation_all/config/env.sh
```

Or manually:

```bash
export GZ_SIM_RESOURCE_PATH=$GZ_SIM_RESOURCE_PATH:/path/to/Simulation_all/ros2_ws/src/crane_gazebo/worlds
export GZ_SIM_RESOURCE_PATH=$GZ_SIM_RESOURCE_PATH:/path/to/Simulation_all/ros2_ws/src/crane_gazebo/models
```

This ensures Gazebo finds all custom worlds and models **without touching system files** in `/usr/share/gazebo/`.

---

## 🚀 Launching the Simulation

### Quick launch in your terminal (all 3 components at once)

```bash
./Simulation_all/run_simulation.sh
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
source Simulation_all/config/env.sh
gz sim -v4 -r iris_crane_world.sdf
```

**Terminal 2 — ArduPilot SITL** *(wait ~5s after Gazebo starts)*
```bash
sim_vehicle.py -v ArduCopter -f gazebo-iris --model JSON --map --console
```

**Terminal 3 — ROS 2 + MAVROS** *(wait ~5s after SITL starts)*
```bash
source /opt/ros/humble/setup.bash
source Simulation_all/ros2_ws/install/setup.bash
ros2 launch mavros apm.launch fcu_url:=udp://localhost:14550@
```

---



## 🐛 Troubleshooting

**Gazebo can't find the world file**
→ Check that `GZ_SIM_RESOURCE_PATH` includes the `worlds/` folder. Run `source Simulation_all/config/env.sh` first.

**MAVROS can't connect to SITL**
→ Make sure ArduPilot SITL is fully started (look for `APM: EKF3 IMU0 is using GPS` in the SITL console) before launching MAVROS.

**`sim_vehicle.py` not found**
→ Run `. ~/.profile` or add ArduPilot tools to your PATH:
```bash
export PATH=$PATH:$HOME/CraneAero-GDP-2026/Simulation_all/external/ardupilot/Tools/autotest
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
Last contributor : Praox