#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/point_cloud2.hpp>
#include <pcl_conversions/pcl_conversions.h>
#include <pcl/filters/passthrough.h>
#include <pcl/point_types.h>
#include <pcl/point_cloud.h>

class RadarPassthroughFilter : public rclcpp::Node
{
public:
    RadarPassthroughFilter() : Node("radar_passthrough_filter")
    {
        // Parameters for radar (long range, wide FOV)
        this->declare_parameter("min_x", 0.0);
        this->declare_parameter("max_x", 200.0);
        this->declare_parameter("min_y", -5.0);
        this->declare_parameter("max_y", 5.0);
        this->declare_parameter("min_z", -2.0);
        this->declare_parameter("max_z", 5.0);
        
        this->declare_parameter("input_topic", "/pdk/ars548/id_114/rdi");
        this->declare_parameter("output_topic", "/radar_filtered");
        
        min_x_ = this->get_parameter("min_x").as_double();
        max_x_ = this->get_parameter("max_x").as_double();
        min_y_ = this->get_parameter("min_y").as_double();
        max_y_ = this->get_parameter("max_y").as_double();
        min_z_ = this->get_parameter("min_z").as_double();
        max_z_ = this->get_parameter("max_z").as_double();
        input_topic_ = this->get_parameter("input_topic").as_string();
        output_topic_ = this->get_parameter("output_topic").as_string();
        
        auto qos = rclcpp::SensorDataQoS();
        
        subscription_ = this->create_subscription<sensor_msgs::msg::PointCloud2>(
            input_topic_, qos,
            std::bind(&RadarPassthroughFilter::cloud_callback, this, std::placeholders::_1));
        
        publisher_ = this->create_publisher<sensor_msgs::msg::PointCloud2>(output_topic_, 10);
        
        RCLCPP_INFO(this->get_logger(), "Radar Passthrough Filter Started");
    }

private:
    void cloud_callback(const sensor_msgs::msg::PointCloud2::SharedPtr msg)
    {
        try {
            pcl::PointCloud<pcl::PointXYZ>::Ptr cloud(new pcl::PointCloud<pcl::PointXYZ>);
            pcl::fromROSMsg(*msg, *cloud);
            
            if (cloud->empty()) return;
            
            // Remove NaN points
            pcl::PointCloud<pcl::PointXYZ>::Ptr valid(new pcl::PointCloud<pcl::PointXYZ>);
            for (const auto& p : *cloud) {
                if (!std::isnan(p.x) && !std::isnan(p.y) && !std::isnan(p.z)) {
                    valid->push_back(p);
                }
            }
            
            // Apply passthrough filters
            pcl::PointCloud<pcl::PointXYZ>::Ptr temp(new pcl::PointCloud<pcl::PointXYZ>);
            pcl::PassThrough<pcl::PointXYZ> pass;
            
            pass.setInputCloud(valid);
            pass.setFilterFieldName("x");
            pass.setFilterLimits(min_x_, max_x_);
            pass.filter(*temp);
            
            pass.setInputCloud(temp);
            pass.setFilterFieldName("y");
            pass.setFilterLimits(min_y_, max_y_);
            pass.filter(*temp);
            
            pass.setInputCloud(temp);
            pass.setFilterFieldName("z");
            pass.setFilterLimits(min_z_, max_z_);
            pass.filter(*temp);
            
            sensor_msgs::msg::PointCloud2 out;
            pcl::toROSMsg(*temp, out);
            out.header = msg->header;
            out.header.stamp = this->now();
            publisher_->publish(out);
            
            RCLCPP_INFO(this->get_logger(), "Radar: %zu -> %zu points", valid->size(), temp->size());
            
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
    rclcpp::spin(std::make_shared<RadarPassthroughFilter>());
    rclcpp::shutdown();
    return 0;
}