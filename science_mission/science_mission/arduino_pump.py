#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from science_mission_interfaces.msg import PumpCommand
'''
You can test the node with:
ros2 run science_mission arduino_pump
ros2 topic pub /pump_command science_mission_interfaces/PumpCommand "{pump_number: 1, time_duration: 500}"
'''
import serial

# Maybe these should be params for the node
PORT = '/dev/ttyUSB0'
BAUD = 9600


class ArduinoPump(Node):
    def __init__(self):
        super().__init__('pump_controller')
        self.subscription = self.create_subscription(
            PumpCommand,
            'pump_command',
            self.pump_command_callback,
            10
        )
        self.subscription

        try:
            self.serial_port = serial.Serial(PORT, BAUD, timeout=1)
        except serial.SerialException as e:
            self.get_logger().error(f"Error opening serial port: {e}")
            self.serial_port = None

    def pump_command_callback(self, msg: PumpCommand):
        pump_number = msg.pump_number
        time_duration = msg.time_duration
        self.get_logger().info(
            f"Pump: {pump_number}, Duration: {time_duration}")

        command_str = f"{pump_number},{time_duration}\n"
        self.get_logger().info(f"Sending: {command_str.strip()}")

        if self.serial_port and self.serial_port.is_open:
            self.serial_port.write(command_str.encode('utf-8'))
        else:
            self.get_logger().error("Serial port not available")


def main(args=None):
    rclpy.init(args=args)
    node = ArduinoPump()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down pump_controller")
    finally:
        if node.serial_port and node.serial_port.is_open:
            node.serial_port.close()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
