#!/usr/bin/env python3

# ------------ Personal Notes ---------------
'''
-----How to run-----
cd /workspaces/MEM571/catkin_ws
catkin_make clean
catkin_make
source devel/setup.bash
roslaunch lab1 controller.launch


-----RViz------
Make sure fixed frame is set to odom
'''
#--------------------------------------------------

import rospy
import math
from geometry_msgs.msg import Twist, Pose, PoseStamped
from nav_msgs.msg import Odometry

class myTurtle():    
    def __init__(self) -> None:
        # Initialize the controller node
        rospy.init_node('turtlebot3_controller', anonymous=True)
        # Publisher Node
        self.vel_pub = rospy.Publisher('/cmd_vel', Twist, queue_size = 10)
        # Subscriber node - odometry
        self.odom_sub = rospy.Subscriber('/odom', Odometry, self.odom_cb)

        # Subscribe to Rviz
        self.goal_sub = rospy.Subscriber('/move_base_simple/goal', PoseStamped, self.goal_cb)

        # Beginning Pose
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_theta = 0.0

        # Publish Rate
        self.rate = rospy.Rate(10)
        # Wait for publisher/subscriber nodes
        rospy.sleep(1.0)
        pass 
    
    # Drive turtlebot forward a given distance
    def drive_straight(self, dist: float, vel: float)->None:
        twist = Twist()
        # Get current position (not pose)
        start_x = self.current_x
        start_y = self.current_y

        # Set direction (forward (+) or backward (-))
        if dist >= 0:
            twist.linear.x = vel
        else:
            twist.linear.x = -vel
        
        # Drive until distance is reached
        while not rospy.is_shutdown():
            # Calculate distance
            moved = math.sqrt((self.current_x - start_x)**2
                              + (self.current_y - start_y)**2)
            # Check if distance reached
            if moved >= abs(dist):
                break
            self.vel_pub.publish(twist)
            self.rate.sleep()
        self.stop()
        pass

    # Rotate the robot
    # Input angle in radians
    def rotate(self, angle):
        twist = Twist()
        omega = 0.5
        # Determine direction
        if angle >= 0:
            twist.angular.z = omega
        else:
            twist.angular.z = -omega

        # Get current angle
        start_theta = self.current_theta
        total_angle = 0.0
        previous_theta = start_theta

        # Begin rotating
        while not rospy.is_shutdown():
            delta = self.current_theta - previous_theta
            # Big maths - normalize delta
            delta = (delta + math.pi) % (2*math.pi) - math.pi
            # how much robot has turned
            total_angle += abs(delta)
            previous_theta = self.current_theta

            if total_angle >= abs(angle):
                break
            self.vel_pub.publish(twist)
            self.rate.sleep()
        self.stop()
        pass
    
    # Spin wheels
    def spin_wheels(self, u1, u2, time):
        # Turtlebot 3 parameters
        wheel_base = 0.16
        wheel_r = 0.033

        # convert wheel speeds
        linear_x = wheel_r*(u2+u1)/2
        angular_z = wheel_r*(u2-u1)/wheel_base

        twist = Twist()
        twist.linear.x = linear_x
        twist.angular.z = angular_z

        # Get current time
        start_time = rospy.Time.now()
        while not rospy.is_shutdown():
            time_passed = (rospy.Time.now() - start_time).to_sec()
            if time_passed >= time:
                break
            self.vel_pub.publish(twist)
            self.rate.sleep()
        self.stop()
        pass

    # Stop the bot
    def stop(self)->None:
        # zero twist
        self.vel_pub.publish(Twist())
        rospy.sleep(0.5)
        pass

    # Navigate to pose
    def nav_to_pose(self, goal):
        # type: (PoseStamped) -> None
        """
        This is a callback function. It should extract data from goal, drive in a striaght line to reach the goal and
        then spin to match the goal orientation.
        :param goal: PoseStamped
        :return:
        """
        x_goal = goal.position.x
        y_goal = goal.position.y

        #convert to theta
        q = goal.orientation
        theta_goal = self.convert_to_euler(q.x, q.y, q.z, q.w)

        # Rotate towards target coordinates
        angle_to_target = math.atan2(y_goal - self.current_y,
                                     x_goal - self.current_x)
        # Get difference between position theta and current theta
        angle_diff = angle_to_target - self.current_theta
        # Take shortest turn to angle 
        min_angle_diff = (angle_diff + math.pi) % (2*math.pi) - math.pi
        # Go for it
        self.rotate(min_angle_diff)

        # Get the distance and drive that thang
        distance = math.sqrt((x_goal-self.current_x)**2 + (y_goal-self.current_y)**2)
        self.drive_straight(distance, 0.22)

        # Get difference between current and desired theta
        end_angle_diff = theta_goal - self.current_theta
        # shortest turn
        end_min_angle_diff = (end_angle_diff + math.pi) % (2*math.pi) - math.pi
        # do the twist
        self.rotate(end_min_angle_diff)
        pass

    def odom_cb(self,msg:Odometry) ->None:
        # Get current pose
        position = msg.pose.pose.position
        orientation = msg.pose.pose.orientation

        # Set pose
        self.current_x = position.x
        self.current_y = position.y

        # Get orientation
        self.current_theta = self.convert_to_euler(
            orientation.x, orientation.y, 
            orientation.z, orientation.w)
        pass
    
    # function for converting quaternation to angle
    def convert_to_euler(self, x,y,z,w):
        siny_cosp = 2.0*(w*z + x*y)
        cosy_cosp = 1.0 - 2.0*(y*y + z*z)
        return math.atan2(siny_cosp, cosy_cosp)    

    # Move the robot in a circle based on input radius
    def drive_circle(self, radius: float) -> None:
        speed = 0.2
        omega = speed/radius # w = v/r

        # get circumference
        circumference = 2*math.pi*abs(radius)
        duration = circumference/speed

        twist = Twist()
        twist.linear.x = speed
        if radius > 0:
            twist.angular.z = omega
        else:
            twist.angular.z = -omega

        start_time = rospy.Time.now()
        while not rospy.is_shutdown():
            elapsed = (rospy.Time.now() - start_time).to_sec()
            if elapsed >= duration:
                break
            self.vel_pub.publish(twist)
            self.rate.sleep()  
    
    # call when a 2d navgoal is set in rviz
    def goal_cb(self,msg: PoseStamped) -> None:
        rospy.loginfo(f"Goal pose created: x={msg.pose.position.x:.2f}, y={msg.pose.position.y:.2f}")
        self.nav_to_pose(msg.pose)

def main():
    bot = myTurtle()

    # Part 5 - Drive in a 0.5m circle
    # bot.drive_circle(0.5)
    # bot.stop()

    # Part 6 - Drive in a 0.5m/side square
    # bot.drive_straight(0.5, 0.15)
    # rospy.sleep(0.25)
    # bot.rotate(1.5)
    # rospy.sleep(0.25)
    # bot.drive_straight(0.5, 0.15)
    # rospy.sleep(0.25)
    # bot.rotate(1.5)
    # rospy.sleep(0.25)
    # bot.drive_straight(0.5, 0.15)
    # rospy.sleep(0.25)
    # bot.rotate(1.5)
    # rospy.sleep(0.25)
    # bot.drive_straight(0.5, 0.15)
    # rospy.sleep(0.25)
    # bot.rotate(1.5)

    # Part 7 - (this is a bash - need to run from a new terminal)
    # check the /scripts/ folder for the bash file

    # Part 8 - Do a little dance
    bot.rotate(1.5)
    rospy.sleep(0.25)
    bot.rotate(-1.5)
    rospy.sleep(0.25)
    bot.rotate(-1.5)
    rospy.sleep(0.25)
    bot.drive_straight(-0.5,0.2)
    rospy.sleep(0.25)
    bot.drive_straight(0.5,0.2)

    def convert_to_euler(x,y,z,w):
        siny_cosp = 2.0*(w*z + x*y)
        cosy_cosp = 1.0 - 2.0*(y*y + z*z)
        return math.atan2(siny_cosp, cosy_cosp)
    
    # Keep the node alive for rviz nav goals
    # rospy.spin() 


if __name__ == '__main__':
    main()   