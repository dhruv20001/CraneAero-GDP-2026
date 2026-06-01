#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/point_cloud2.hpp>
#include <pcl_conversions/pcl_conversions.h>
#include <pcl/filters/voxel_grid.h>
#include <pcl/point_types.h>
#include <pcl/point_cloud.h>

class VoxelGridFilter : public rclcpp::Node
{
public:
    VoxelGridFilter() : Node("voxel_grid_filter")
    {
        this->declare_parameter("voxel_size", 0.05);
        this->declare_parameter("input_topic", "/fused_cloud");
        this->declare_parameter("output_topic", "/voxel_filtered");
        
        voxel_size_ = this->get_parameter("voxel_size").as_double();
        input_topic_ = this->get_parameter("input_topic").as_string();
        output_topic_ = this->get_parameter("output_topic").as_string();
        
        auto qos = rclcpp::QoS(rclcpp::KeepLast(5)).best_effort();
        
        subscription_ = this->create_subscription<sensor_msgs::msg::PointCloud2>(
            input_topic_, qos,
            std::bind(&VoxelGridFilter::cloud_callback, this, std::placeholders::_1));
        
        publisher_ = this->create_publisher<sensor_msgs::msg::PointCloud2>(output_topic_, 10);
        
        RCLCPP_INFO(this->get_logger(), "Voxel Grid Filter Started | Size: %.3fm", voxel_size_);
    }

private:
    void cloud_callback(const sensor_msgs::msg::PointCloud2::SharedPtr msg)
    {
        try {
            pcl::PointCloud<pcl::PointXYZ>::Ptr cloud(new pcl::PointCloud<pcl::PointXYZ>);
            pcl::fromROSMsg(*msg, *cloud);
            
            if (cloud->empty()) return;
            
            // Remove NaN points and convert to unorganized
            pcl::PointCloud<pcl::PointXYZ>::Ptr valid(new pcl::PointCloud<pcl::PointXYZ>);
            for (const auto& p : *cloud) {
                if (!std::isnan(p.x) && !std::isnan(p.y) && !std::isnan(p.z)) {
                    valid->push_back(p);
                }
            }
            
            // Apply voxel grid filter
            pcl::PointCloud<pcl::PointXYZ>::Ptr filtered(new pcl::PointCloud<pcl::PointXYZ>);
            pcl::VoxelGrid<pcl::PointXYZ> vg;
            vg.setInputCloud(valid);
            vg.setLeafSize(voxel_size_, voxel_size_, voxel_size_);
            vg.filter(*filtered);
            
            sensor_msgs::msg::PointCloud2 out;
            pcl::toROSMsg(*filtered, out);
            out.header = msg->header;
            out.header.stamp = this->now();
            publisher_->publish(out);
            
            double percent = (filtered->size() * 100.0) / valid->size();
            RCLCPP_INFO(this->get_logger(), "Voxel: %zu -> %zu (%.1f%% kept)", valid->size(), filtered->size(), percent);
            
        } catch (const std::exception& e) {
            RCLCPP_ERROR(this->get_logger(), "Error: %s", e.what());
        }
    }
    
    double voxel_size_;
    std::string input_topic_, output_topic_;
    rclcpp::Subscription<sensor_msgs::msg::PointCloud2>::SharedPtr subscription_;
    rclcpp::Publisher<sensor_msgs::msg::PointCloud2>::SharedPtr publisher_;
};

int main(int argc, char** argv)
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<VoxelGridFilter>());
    rclcpp::shutdown();
    return 0;
}