#!/usr/bin/env python3
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from unmanned_systems_ros2_pkg import quaternion_tools

class TurtleBotNode(Node):
    def __init__(self, node_name, ns='' ):
        super().__init__(node_name)
        
        if ns != '':
            self.ns = ns
        else:
            self.ns = ns
                
        #create vel and odom pub and subscribers
        self.vel_publisher = self.create_publisher(
            Twist, self.ns+ "/cmd_vel" ,  10) 
        
        self.odom_subscriber = self.create_subscription(
            Odometry, self.ns +"/odom", self.odom_callback, 10)
        
        self.lidar_subscriber = self.create_subscription(
             LaserScan, self.ns+"/scan", self.lidar_track_cb, 10)
        
        self.current_position = [0,0]
        self.orientation_quat = [0,0,0,0] #x,y,z,w
        self.orientation_euler = [0,0,0] #roll, pitch, yaw
        
        self.detected_range_list = [] #depth detected
        self.detected_heading_angle_list = [] #heading detected

    def odom_callback(self,msg:Odometry):
        """subscribe to odometry"""
        self.current_position[0] = msg.pose.pose.position.x
        self.current_position[1] = msg.pose.pose.position.y
        
        qx = msg.pose.pose.orientation.x
        qy = msg.pose.pose.orientation.y
        qz = msg.pose.pose.orientation.z
        qw = msg.pose.pose.orientation.w
        
        roll,pitch,yaw = quaternion_tools.euler_from_quaternion(qx, qy, qz, qw)
        
        self.orientation_euler[0] = roll
        self.orientation_euler[1] = pitch 
        self.orientation_euler[2] = yaw
        
        
    def move_turtle(self, linear_vel:float, angular_vel:float):
        """Moves turtlebot"""
        twist = Twist()
        twist.linear.x = linear_vel
        twist.angular.z = angular_vel
        self.vel_publisher.publish(twist)
    
    def lidar_track_cb(self, msg:LaserScan):
        """lidar information remember the msg is an array of 0-> 359"""
        self.detected_range_list = []
        self.detected_heading_angle_list = []
        inf = float('inf')
        
        lidar_vals = msg.ranges
        
        #append detections if values not infinity or 0.0 
        for i, val in enumerate(lidar_vals):
            if val != inf:
                self.detected_heading_angle_list.append(i)
                self.detected_range_list.append(val)