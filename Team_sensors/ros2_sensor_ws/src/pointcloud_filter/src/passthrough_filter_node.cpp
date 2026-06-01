#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/point_cloud2.hpp>
#include <pcl_conversions/pcl_conversions.h>
#include <pcl/filters/passthrough.h>
#include <pcl/point_types.h>
#include <pcl/point_cloud.h>
#include <chrono>
#include <memory>

class PassthroughFilterNode : public rclcpp::Node
{
public:
    PassthroughFilterNode() : Node("passthrough_filter_cpp")
    {
        // Declare parameters
        this->declare_parameter("min_x", -5.0);
        this->declare_parameter("max_x", 5.0);
        this->declare_parameter("min_y", -5.0);
        this->declare_parameter("max_y", 5.0);
        this->declare_parameter("min_z", 0.0);
        this->declare_parameter("max_z", 3.0);
        this->declare_parameter("input_topic", "/fused_cloud");
        this->declare_parameter("output_topic", "/filtered_cloud_cpp");
        
        // Get parameters
        min_x_ = this->get_parameter("min_x").as_double();
        max_x_ = this->get_parameter("max_x").as_double();
        min_y_ = this->get_parameter("min_y").as_double();
        max_y_ = this->get_parameter("max_y").as_double();
        min_z_ = this->get_parameter("min_z").as_double();
        max_z_ = this->get_parameter("max_z").as_double();
        input_topic_ = this->get_parameter("input_topic").as_string();
        output_topic_ = this->get_parameter("output_topic").as_string();
        
        // QoS
        auto qos = rclcpp::QoS(rclcpp::KeepLast(5)).best_effort().durability_volatile();
        
        subscription_ = this->create_subscription<sensor_msgs::msg::PointCloud2>(
            input_topic_, qos,
            std::bind(&PassthroughFilterNode::cloud_callback, this, std::placeholders::_1));
        
        publisher_ = this->create_publisher<sensor_msgs::msg::PointCloud2>(
            output_topic_, 10);
        
        RCLCPP_INFO(this->get_logger(), "C++ Passthrough Filter Started");
    }

private:
    void cloud_callback(const sensor_msgs::msg::PointCloud2::SharedPtr msg)
    {
        auto start = std::chrono::high_resolution_clock::now();
        
        try {
            pcl::PointCloud<pcl::PointXYZ>::Ptr cloud(new pcl::PointCloud<pcl::PointXYZ>);
            pcl::fromROSMsg(*msg, *cloud);
            
            if (cloud->empty()) return;
            
            // Filter X
            pcl::PointCloud<pcl::PointXYZ>::Ptr cloud_x(new pcl::PointCloud<pcl::PointXYZ>);
            pcl::PassThrough<pcl::PointXYZ> pass;
            pass.setInputCloud(cloud);
            pass.setFilterFieldName("x");
            pass.setFilterLimits(min_x_, max_x_);
            pass.filter(*cloud_x);
            
            // Filter Y
            pcl::PointCloud<pcl::PointXYZ>::Ptr cloud_xy(new pcl::PointCloud<pcl::PointXYZ>);
            pass.setInputCloud(cloud_x);
            pass.setFilterFieldName("y");
            pass.setFilterLimits(min_y_, max_y_);
            pass.filter(*cloud_xy);
            
            // Filter Z
            pcl::PointCloud<pcl::PointXYZ>::Ptr cloud_xyz(new pcl::PointCloud<pcl::PointXYZ>);
            pass.setInputCloud(cloud_xy);
            pass.setFilterFieldName("z");
            pass.setFilterLimits(min_z_, max_z_);
            pass.filter(*cloud_xyz);
            
            // Publish
            sensor_msgs::msg::PointCloud2 output;
            pcl::toROSMsg(*cloud_xyz, output);
            output.header = msg->header;
            output.header.stamp = this->now();
            publisher_->publish(output);
            
            auto end = std::chrono::high_resolution_clock::now();
            auto elapsed = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
            
            RCLCPP_INFO(this->get_logger(), 
                "Filtered: %zu -> %zu points, time: %.2fms",
                cloud->size(), cloud_xyz->size(), elapsed.count() / 1000.0);
            
        } catch (const std::exception& e) {
            RCLCPP_ERROR(this->get_logger(), "Error: %s", e.what());
        }
    }
    
    double min_x_, max_x_, min_y_, max_y_, min_z_, max_z_;
    std::string input_topic_, output_topic_;
    rclcpp::Subscription<sensor_msgs::msg::PointCloud2>::SharedPtr subscription_;
    rclcpp::Publisher<sensor_msgs::msg::PointCloud2>::SharedPtr publisher_;
};

int main(int argc, char** argv)
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<PassthroughFilterNode>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}
