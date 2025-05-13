#!/usr/bin/env python3
"""
Demo IoT Application

This application demonstrates interaction with an IoT device based on ATLAS DDL-IOT Builder.
It sends JSON-formatted API calls to interact with various IoT services and handles the responses.

Services used:
- CheckFlameStatus: checks whether a flame has been detected
- ActivateBuzzer: activates the alarm buzzer
- ReadDHT: reads data from the DHT11 environmental sensor
- ActivateFan: activates a cooling fan
"""

import json
import socket
import time
import argparse
from typing import Dict, Any, Optional


class DemoIoTApplication:
    """Demo application to interact with IoT services via JSON API."""

    def __init__(self, thing_ip: str, thing_port: int, thing_id: str, space_id: str):
        """
        Initialize the demo IoT application.

        Args:
            thing_ip: IP address of the IoT device
            thing_port: Port of the IoT device (default: 6668)
            thing_id: ID of the device as defined in the IoT-DDL
            space_id: ID of the space as defined in the IoT-DDL
        """
        self.thing_ip = thing_ip
        self.thing_port = thing_port
        self.thing_id = thing_id
        self.space_id = space_id

    def build_api_call(self, service_name: str, service_inputs: str) -> str:
        """
        Builds a JSON-formatted API call.

        Args:
            service_name: Name of the service to call
            service_inputs: Input parameters for the service (string format)

        Returns:
            JSON-formatted API call string
        """
        api_call = {
            "Tweet Type": "Service call",
            "Thing ID": self.thing_id,
            "Space ID": self.space_id,
            "Service Name": service_name,
            "Service Inputs": service_inputs
        }
        return json.dumps(api_call)

    def send_api_call(self, api_call: str) -> Optional[Dict[str, Any]]:
        """
        Sends an API call to the IoT device and returns the response.

        Args:
            api_call: JSON string of the API call to send

        Returns:
            Dictionary with the JSON response or None if an error occurred
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((self.thing_ip, self.thing_port))

                print(f"Sending request: {api_call}")
                sock.sendall(api_call.encode('utf-8'))

                response = sock.recv(1024).decode('utf-8')
                print(f"Response received: {response}")

                if response:
                    return json.loads(response)
                return None

        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            return None
        except socket.error as e:
            print(f"Connection error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None

    def check_flame_status(self) -> Optional[Dict[str, Any]]:
        """ Checks the status of the flame sensor.

        Returns:
        Dictionary with the response or None if an error occurred
        """
        print("\n[SERVICE] Checking flame sensor...")
        api_call = self.build_api_call("CheckFlameStatus", "()")
        response = self.send_api_call(api_call)

        if response:
            if "Status" in response and response["Status"] == "Successful":
                if "Service Result" in response:
                    flame_status = response["Service Result"]
                    if flame_status == "0":
                        print("⚠️ ALERT: Flame detected! Activating buzzer...")
                        self.activate_buzzer()
                    else:
                        print("✓ No flame detected.")
                else:
                    print("❌ Error: Service Result field missing in response")
        else:
            print(f"❌ Error: Service call failed - {response.get('Status Description', 'Unknown error')}")

        return response

    def activate_buzzer(self) -> Optional[Dict[str, Any]]:
        """
        Activates the alarm buzzer.

        Returns:
            Dictionary with the response or None if an error occurred
        """
        print("\n[SERVICE] Activating alarm buzzer...")
        api_call = self.build_api_call("ActivateBuzzer", "()")
        response = self.send_api_call(api_call)

        if response:
            print("🔊 Buzzer activated!")

        return response

    def read_dht(self) -> Optional[Dict[str, Any]]:
        """
        Reads data from the DHT11 sensor (temperature or humidity based on user selection).

        Returns:
            Dictionary with the response or None if an error occurred
        """
        print("\n[SERVICE] DHT11 sensor reading service")
        print("Please select what to read:")
        print("0 - Temperature")
        print("1 - Humidity")

        try:
            mode = int(input("Enter your choice (0/1): "))
            if mode not in [0, 1]:
                print("Invalid selection. Please enter 0 for temperature or 1 for humidity.")
                return None

            sensor_type = "Temperature" if mode == 0 else "Humidity"
            print(f"\n[SERVICE] Reading DHT11 sensor for {sensor_type}...")
            
            # Build API call with the selection parameter
            api_call = self.build_api_call("ReadDHT", f"({mode})")
            response = self.send_api_call(api_call)

            if response:
                if "Status" in response and response["Status"] == "Successful":
                    if "Service Result" in response:
                        value = response["Service Result"]
                        
                        # Check if the value indicates an error
                        if value == -1:
                            print("❌ Error: Sensor reading failed")
                            return response
                        elif value == -2:
                            print("❌ Error: Invalid parameter")
                            return response
                        
                        # Process successful reading
                        if mode == 0:  # Temperature
                            print(f"🌡️ Temperature: {value}°C")
                            if int(value) > 30:
                                print("⚠️ High temperature detected! Activating fan...")
                                self.activate_fan()
                        else:  # Humidity
                            print(f"💧 Humidity: {value}%")
                            if int(value) > 60:
                                print("⚠️ High humidity detected! Activating fan...")
                                self.activate_fan()
                    else:
                        print("❌ Error: Service Result field missing in response")
                else:
                    print(f"❌ Error: Service call failed - {response.get('Status Description', 'Unknown error')}")
            else:
                print("❌ Error: No response from API")
            
            return response
            
        except ValueError:
            print("❌ Error: Invalid input. Please enter a number (0 or 1).")
            return None

    def activate_fan(self) -> Optional[Dict[str, Any]]:
        """
        Activates the cooling fan.

        Returns:
            Dictionary with the response or None if an error occurred
        """
        print("\n[SERVICE] Activating cooling fan...")
        api_call = self.build_api_call("ActivateFan", "()")
        response = self.send_api_call(api_call)

        if response:
            if "Status" in response and response["Status"] == "Successful":
             print("✓ Fan successfully activated.")
            else:
             print("✗ Failed to activate fan.")
             if "Status Description" in response:
                print(f"Reason: {response['Status Description']}")
        return response
    def run_demo(self, cycles: int = 5, interval: int = 5):
        """
        Runs a cyclic demonstration of services based on user choice.

        Args:
            cycles: Number of demo cycles to execute
            interval: Time between cycles in seconds
        """
        print("\n" + "="*50)
        print("DEMO IoT APPLICATION STARTED")
        print(f"Connecting to {self.thing_id} at {self.thing_ip}:{self.thing_port}")
        print("="*50 + "\n")
        
        print("Please select environment to test:")
        print("0 - Full test (flame sensor, buzzer, DHT sensor, fan)")
        print("1 - Flame sensor and buzzer")
        print("2 - DHT sensor and fan")

        try:
            choice = int(input("Enter your choice (1/2): "))
            if choice not in [1, 2]:
                print("Invalid selection. Default to full test.")
                choice = 0
        except ValueError:
            print("Invalid input. Default to full test.")
            choice = 0

        for i in range(cycles):
            print(f"\n{'='*20} DEMO CYCLE {i+1}/{cycles} {'='*20}\n")
            
            if choice == 0:  # Full test (fallback)
               # self.activate_buzzer()
                self.check_flame_status()
                self.read_dht()
                self.activate_fan()
            elif choice == 1:  # Flame sensor and buzzer
                print("Running flame sensor and buzzer test...")
                self.check_flame_status()
                #self.activate_buzzer()
            elif choice == 2:  # DHT sensor and fan
                print("Running DHT sensor and fan test...")
                self.read_dht()
                self.activate_fan()

            if i < cycles - 1:
                print(f"\nWaiting {interval} seconds before next cycle...\n")
                time.sleep(interval)

        print("\n" + "="*50)
        print("DEMO COMPLETED")
        print("="*50 + "\n")

def main():
    """Main function to start the demo application."""
    parser = argparse.ArgumentParser(description='Demo IoT Application')
    parser.add_argument('--ip', type=str, default='192.168.8.201',
                        help='IP address of the IoT device (default: 192.168.8.201)')
    parser.add_argument('--port', type=int, default=6668,
                        help='Port of the IoT device (default: 6668)')
    parser.add_argument('--thing-id', type=str, default='MySmartThing01',
                        help='ID of the IoT device (default: MySmartThing01)')
    parser.add_argument('--space-id', type=str, default='MySmartSpace',
                        help='ID of the smart space (default: MySmartSpace)')
    parser.add_argument('--cycles', type=int, default=2,
                        help='Number of demo cycles (default: 2)')
    parser.add_argument('--interval', type=int, default=5,
                        help='Interval between cycles in seconds (default: 5)')

    args = parser.parse_args()

    demo = DemoIoTApplication(
        thing_ip=args.ip,
        thing_port=args.port,
        thing_id=args.thing_id,
        space_id=args.space_id
    )

    try:
        demo.run_demo(cycles=args.cycles, interval=args.interval)
    except KeyboardInterrupt:
        print("\nDemo interrupted by user.")
    except Exception as e:
        print(f"Error during demo execution: {e}")


if __name__ == "__main__":
    main()
