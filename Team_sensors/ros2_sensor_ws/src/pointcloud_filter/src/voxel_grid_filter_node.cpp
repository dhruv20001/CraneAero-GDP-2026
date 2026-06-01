#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/point_cloud2.hpp>
#include <pcl_conversions/pcl_conversions.h>
#include <pcl/filters/voxel_grid.h>
#include <pcl/point_types.h>
#include <pcl/point_cloud.h>
#include <chrono>
#include <deque>

class VoxelGridFilterNode : public rclcpp::Node
{
public:
    VoxelGridFilterNode() : Node("voxel_grid_filter")
    {
        // Declare parameters
        this->declare_parameter("voxel_size", 0.05);
        this->declare_parameter("input_topic", "/filtered_cloud_cpp");
        this->declare_parameter("output_topic", "/voxel_filtered");
        this->declare_parameter("enable_stats", true);
        
        // Get parameters
        voxel_size_ = this->get_parameter("voxel_size").as_double();
        input_topic_ = this->get_parameter("input_topic").as_string();
        output_topic_ = this->get_parameter("output_topic").as_string();
        enable_stats_ = this->get_parameter("enable_stats").as_bool();
        
        // QoS
        auto qos = rclcpp::QoS(rclcpp::KeepLast(5)).best_effort();
        
        subscription_ = this->create_subscription<sensor_msgs::msg::PointCloud2>(
            input_topic_, qos,
            std::bind(&VoxelGridFilterNode::cloud_callback, this, std::placeholders::_1));
        
        publisher_ = this->create_publisher<sensor_msgs::msg::PointCloud2>(
            output_topic_, 10);
        
        // Stats timer (every 5 seconds)
        stats_timer_ = this->create_wall_timer(
            std::chrono::seconds(5),
            std::bind(&VoxelGridFilterNode::print_stats, this));
        
        RCLCPP_INFO(this->get_logger(), 
            "Voxel Grid Filter Started | Size: %.3fm", voxel_size_);
    }

private:
    void cloud_callback(const sensor_msgs::msg::PointCloud2::SharedPtr msg)
    {
        auto start = std::chrono::high_resolution_clock::now();
        
        try {
            // Convert ROS to PCL
            pcl::PointCloud<pcl::PointXYZ>::Ptr cloud(new pcl::PointCloud<pcl::PointXYZ>);
            pcl::fromROSMsg(*msg, *cloud);
            
            if (cloud->empty()) return;
            
            // Apply Voxel Grid Filter
            pcl::PointCloud<pcl::PointXYZ>::Ptr cloud_filtered(new pcl::PointCloud<pcl::PointXYZ>);
            pcl::VoxelGrid<pcl::PointXYZ> voxel;
            voxel.setInputCloud(cloud);
            voxel.setLeafSize(voxel_size_, voxel_size_, voxel_size_);
            voxel.filter(*cloud_filtered);
            
            // Convert back to ROS
            sensor_msgs::msg::PointCloud2 output;
            pcl::toROSMsg(*cloud_filtered, output);
            output.header = msg->header;
            output.header.stamp = this->now();
            publisher_->publish(output);
            
            // Performance logging
            auto end = std::chrono::high_resolution_clock::now();
            auto elapsed = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
            double elapsed_ms = elapsed.count() / 1000.0;
            
            // Update stats
            total_points_in_ += cloud->size();
            total_points_out_ += cloud_filtered->size();
            total_time_ += elapsed_ms;
            frame_count_++;
            
            // Store in history
            times_.push_back(elapsed_ms);
            if (times_.size() > 100) times_.pop_front();
            
            // Calculate instantaneous reduction
            double reduction = 100.0 * (1.0 - (double)cloud_filtered->size() / (double)cloud->size());
            
            RCLCPP_INFO(this->get_logger(), 
                "📊 Voxel: %zu → %zu (%.1f%% kept) | ⏱️  %.2fms | 📦 %.3fm | 📈 %zu pts",
                cloud->size(), cloud_filtered->size(), 100.0 - reduction,
                elapsed_ms, voxel_size_, cloud_filtered->size());
            
        } catch (const std::exception& e) {
            RCLCPP_ERROR(this->get_logger(), "Error: %s", e.what());
        }
    }
    
    void print_stats()
    {
        if (frame_count_ == 0) return;
        
        // Calculate averages
        double avg_time = total_time_ / frame_count_;
        double avg_points_in = total_points_in_ / frame_count_;
        double avg_points_out = total_points_out_ / frame_count_;
        double avg_reduction = 100.0 * (1.0 - avg_points_out / avg_points_in);
        
        // Calculate min/max time
        double min_time = *std::min_element(times_.begin(), times_.end());
        double max_time = *std::max_element(times_.begin(), times_.end());
        
        RCLCPP_INFO(this->get_logger(), 
            "\n═══════════════════════════════════════\n"
            "📈 **PERFORMANCE STATISTICS (last %d frames)**\n"
            "═══════════════════════════════════════\n"
            "  Average time:    %.2f ms\n"
            "  Min/Max time:    %.2f / %.2f ms\n"
            "  Avg points in:   %.0f\n"
            "  Avg points out:  %.0f\n"
            "  Avg reduction:   %.1f%%\n"
            "  Effective rate:  %.1f Hz\n"
            "═══════════════════════════════════════",
            frame_count_, avg_time, min_time, max_time, 
            avg_points_in, avg_points_out, avg_reduction,
            1000.0 / avg_time);
        
        // Reset counters
        total_points_in_ = 0;
        total_points_out_ = 0;
        total_time_ = 0;
        frame_count_ = 0;
    }
    
    // Parameters
    double voxel_size_;
    std::string input_topic_, output_topic_;
    bool enable_stats_;
    
    // ROS
    rclcpp::Subscription<sensor_msgs::msg::PointCloud2>::SharedPtr subscription_;
    rclcpp::Publisher<sensor_msgs::msg::PointCloud2>::SharedPtr publisher_;
    rclcpp::TimerBase::SharedPtr stats_timer_;
    
    // Statistics
    size_t total_points_in_ = 0;
    size_t total_points_out_ = 0;
    double total_time_ = 0;
    int frame_count_ = 0;
    std::deque<double> times_;
};

int main(int argc, char** argv)
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<VoxelGridFilterNode>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}