# Install
Download and install PDK files for given system. Either pdk-base_1.1.0-5fcdd66_arm64.tar or pdk-base_1.1.0-5fcdd66_arm64.tar depending on your system architecture.
Extract file into desired location on your home drive 
1. eCal
```bash
sudo apt install <File Location>/pdk-base_1.1.0-5fcdd66_amd64/eCAL-5.12.1-Linux.deb
```
2.codemeter
```bash
sudo apt install <File Location>/pdk-base_1.1.0-5fcdd66_amd64/codemeter-lite_7.40.4990.500_amd64.deb
```
3.pdk-base
```bash
sudo apt install <File Location>/pdk-base_1.1.0-5fcdd66_amd64/pdk-base_1.1.0-5fcdd66_amd64.deb
```
4.pdk-mon - Choose relevant Mon for your version of Ubuntu
```bash
sudo apt install <File Location>/pdk-base_1.1.0-5fcdd66_amd64/pdk-mon_1.1.0-5fcdd66_jammy-amd64.deb
```
# Configure 
## 1. Navigate to the pdk_config.json file

```bash
cd /opt/pdk/etc

ls
```
#### Expected Output

### Expect Output - pdk_config.json should be seen
90-pdk-pcan-x6.rules		   mediaGatewayConfig_svc216.cfg  pdk_ptp4l.service
ecal.ini			   pdk_config.json		  vsomeip_srr630_config.json
mediaGatewayConfig_ars548only.cfg  pdk_phc2sys.service
mediaGatewayConfig_default.cfg	   pdk_ptp4l.conf


## 2. Edit the pdk_config file to match the PDK_config in this branch, or replace the file in /opt/pdk/etc with the one from this repo. All unused sensors need to be removed from the config.

```bash
sudo nano pdk_config.json
```

## 3. Open Wireshark: Monitor IP Adress
1. Find the name of the ethernet port the Radar is connected to.
```bash
sudo wireshark
```

## 4. Edit the Netplan config (01-network-manager-all.yaml)

1. Navigate to the NETPLAN Config file
```bash
cd /etc/netplan/
ls
```
Confirm the 01-network-manager-all.yaml is in the directory

2. Edit 01-network-manager-all.yaml
``` bash
sudo nano 01-network-manager-all.yaml
```
3. Apply the Network config changes in accordance with image below
Change renderer to networkd
add ethernet link name under ethernets along with dhcp4:false
under vlan.19
   -add link name after link:
   change addresses to 10.13.1.166/24
``` bash
------------------------------------------------------------------------------------
network:
  version: 2
  renderer: networkd
  ethernets:
    enp44s0:  ## <----- Change to the name of your NIC interface (eno0/eno1/enpxxxx)
      dhcp4: false ## <----- Add this line
    lo:
      dhcp4: no
      addresses: [ 127.0.0.1/32] # declare localhost for local route
      routes: # declare local route for internal pdk communication
        - to: 239.0.0.0/8
          via: 127.0.0.1
  vlans:
    # ARS548
    ARS548.19:
      id: 19
      link: enp44s0 ## <----- Change to the name of your NIC interface (eno0/eno1/enpxxxx)
      dhcp4: no
      addresses: [ 10.13.1.166/24] ## <----- Change this IP to whjat is shown here
-------------------------------------------------------------------------
```

Apply netplan

```bash
sudo netplan apply
```

## 5. Reboot the PC

# 6. Open the PDK Monitoring Tool
1.
```bash
cd /opt/pdk/bin/
./pdk_start.sh
```

Expected Output 
   -----------------------------------------------------------------
   Starting ptp daemon check
   Warning: PTP is not running.
   Warning: This might result in a degraded performance of pdk_occupancy_grid_processing and pdk_dynamic_object_tracking.
   -----------------------------------------------------------------
   -----------------------------------------------------------------
   Starting check of network route.
   Please add the ecal route, e.g. "sudo ip route add 239.0.0.0/8 dev lo" 
   -----------------------------------------------------------------
   -----------------------------------------------------------------
   Starting PDK configuration check for Sensor ARS430DI
   Checking IP 192.168.15.101
   Desired IP 192.168.15.101 is not set to any interface. 
   -----------------------------------------------------------------
   -----------------------------------------------------------------
   Starting PDK configuration check for Sensor ARS548
   Checking IP 10.13.1.166
   Checking VLAN ID 19
   Desired IP 10.13.1.166 is set to interface ARS548.19. 
   Desired VLAN ID 19 is setsudo nano 01-network-manager-all-yaml to interface ARS548.19 
   -----------------------------------------------------------------
   -----------------------------------------------------------------
   Starting check for CAN Interfaces
   No CAN interface(s) found.
   -----------------------------------------------------------------
   Using already sourced ROS 2 humble.
   Starting pdk_ethernet_radar_handler
   Loading config from from: /opt/pdk/etc/pdk_config.json
   [pdk_ethernet_radar_handler] Warning: no cameras configured
   [pdk_ethernet_radar_handler] Configured sensor types:
   [pdk_ethernet_radar_handler]     ars430di, Expected ip on host: 192.168.15.101
   [pdk_ethernet_radar_handler]     ars540, Expected ip on host: 10.13.1.166
   [pdk_ethernet_radar_handler] Starting License Check for ARS548
   [pdk_ethernet_radar_handler] Checked out license from dongle with serial number 3-6088386
   [pdk_ethernet_radar_handler] License check succeeded.
   [pdk_ethernet_radar_handler] Subscribed to radar detection data from sensor ID: 114
   [pdk_ethernet_radar_handler] Start SOME/IP sensor gateway...
   [pdk_ethernet_radar_handler] No SOME/IP-SD sensor configured.
   Starting pdk_canfd_radar_handler
   [pdk_canfd_radar_handler] Warning: no cameras configured
Starting License Check
[pdk_canfd_radar_handler] Checked out license from dongle with serial number 3-6088386
License Check succeeded
[pdk_canfd_radar_handler] No interfaces or sensors specified - shutting down
Starting Mounting parameters publisher
Starting pdk_monitoring_tool
Starting pdk_imu_handler
Starting Camera Handler
Launching ROS2 Node
[pdk_imu_handler] Warning: no cameras configured
[pdk_mounting_parameters] Warning: no cameras configured
[customer_interface_library] Warning: no cameras configured
Running.
[pdk_camera_handler] Checked out license from dongle with serial number 3-6088386
[pdk_camera_handler] Warning: no cameras configured
[pdk_camera_handler] Config seems to contain no sensors of correct type
terminate called after throwing an instance of 'std::runtime_error'
  what():  Config seems to contain no sensors of correct type
[pdk_imu_handler] Checked out license from dongle with serial number 3-6088386
[pdk_imu_handler] No interface specified - shutting down
[pdk_monitoring_tool] Warning: no cameras configured
Warning: Ignoring XDG_SESSION_TYPE=wayland on Gnome. Use QT_QPA_PLATFORM=wayland to run on Wayland anyway.
Package 'pdk_bridge' not found: "package 'pdk_bridge' not found, searching: ['/home/dhruv/ros2_ws/install/rplidar_ros', '/home/dhruv/ros2_ws/install/point_cloud_filter', '/home/dhruv/ros2_sensor_ws/install/sensor_fusion_pkg', '/home/dhruv/ros2_sensor_ws/install/pointcloud_filter', '/opt/ros/humble']"
[pdk_ethernet_radar_handler] [Sensor 114] Skip incoming Status Message. Could not get lock
./pdk_start.sh: line 149: 10886 Aborted                 (core dumped) ${pdk_install_path}/bin/pdk_camera_handler -c "${pdk_config_file}" 2>&1



