# gui/tabs/app_executor.py
import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
import re
import json
import threading
import queue
import time
from datetime import datetime
from service_discover.api_caller import invoke_iot_app


class AppExecutor:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.terminal_window = None
        self.terminal_text = None
        self.terminal_input = None
        self.terminal_queue = queue.Queue()
        self.user_input_queue = queue.Queue()
        self.waiting_for_input = False

    def create_terminal_window(self):
        """Create a separate terminal window"""
        if self.terminal_window and self.terminal_window.winfo_exists():
            self.terminal_window.lift()
            return
        
        self.terminal_window = Toplevel(self.parent_frame)
        self.terminal_window.title("App Execution Terminal")
        self.terminal_window.geometry("800x600")
        self.terminal_window.configure(bg="black")
        
        # Terminal text area
        terminal_frame = tk.Frame(self.terminal_window, bg="black")
        terminal_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.terminal_text = tk.Text(terminal_frame, bg="black", fg="green", 
                                   font=("Consolas", 10), relief=tk.FLAT, 
                                   state=tk.DISABLED, wrap=tk.WORD)
        terminal_scroll = ttk.Scrollbar(terminal_frame, command=self.terminal_text.yview)
        self.terminal_text.config(yscrollcommand=terminal_scroll.set)
        self.terminal_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        terminal_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Input frame
        input_frame = tk.Frame(self.terminal_window, bg="black")
        input_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0, 10))
        
        tk.Label(input_frame, text=">", bg="black", fg="green", 
                font=("Consolas", 10)).pack(side=tk.LEFT)
        self.terminal_input = tk.Entry(input_frame, bg="black", fg="green", 
                                     font=("Consolas", 10), insertbackground="green", 
                                     relief=tk.FLAT)
        self.terminal_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # Bind input events
        self.terminal_input.bind("<Return>", self.handle_terminal_input)
        
        # Clear terminal button
        clear_button = tk.Button(input_frame, text="Clear", bg="gray20", fg="white",
                               command=self.clear_terminal, relief=tk.FLAT)
        clear_button.pack(side=tk.RIGHT, padx=(10, 0))

    def write_to_terminal(self, message, color="green"):
        """Thread-safe function to write to terminal"""
        if not self.terminal_text:
            return
            
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        def write():
            self.terminal_text.config(state=tk.NORMAL)
            if color == "red":
                self.terminal_text.insert(tk.END, f"[{timestamp}] ❌ {message}\n")
            elif color == "yellow":
                self.terminal_text.insert(tk.END, f"[{timestamp}] ⚠️  {message}\n")
            elif color == "blue":
                self.terminal_text.insert(tk.END, f"[{timestamp}] ℹ️  {message}\n")
            else:
                self.terminal_text.insert(tk.END, f"[{timestamp}] {message}\n")
            self.terminal_text.config(state=tk.DISABLED)
            self.terminal_text.see(tk.END)
        
        # Schedule the write operation on the main thread
        self.terminal_window.after(0, write)

    def clear_terminal(self):
        """Clear terminal content"""
        if self.terminal_text:
            self.terminal_text.config(state=tk.NORMAL)
            self.terminal_text.delete(1.0, tk.END)
            self.terminal_text.config(state=tk.DISABLED)

    def get_user_input_from_terminal(self, prompt):
        """Get user input through terminal interface"""
        self.write_to_terminal(prompt, "yellow")
        self.waiting_for_input = True
        
        if self.terminal_input:
            self.terminal_input.focus_set()
        
        # Wait for user input
        while self.waiting_for_input:
            try:
                result = self.user_input_queue.get_nowait()
                self.waiting_for_input = False
                return result
            except queue.Empty:
                time.sleep(0.1)
                if self.terminal_window and self.terminal_window.winfo_exists():
                    self.terminal_window.update()
                else:
                    break
        
        return ""

    def handle_terminal_input(self, event):
        """Handle terminal input submission"""
        if self.waiting_for_input and self.terminal_input:
            user_input = self.terminal_input.get()
            self.terminal_input.delete(0, tk.END)
            self.write_to_terminal(f"> {user_input}")
            self.user_input_queue.put(user_input)
        return "break"

    def parse_api_string(self, api_str, input_names, input_types):
        """Parse API string and extract components"""
        # Regex to find the main parts
        match = re.match(r'^(\w+):\[(.*?)\]:\((.*?)\)$', api_str.strip())
        if not match:
            raise ValueError("Invalid format")

        endpoint = match.group(1)
        input_str = match.group(2)
        output_str = match.group(3)

        # Clear input lists
        input_names.clear()
        input_types.clear()

        # Parsing input
        if input_str.strip():  # Check if input string is not empty
            for param in input_str.split('|'):
                parts = param.strip().strip('"').split(',')
                if len(parts) >= 2:
                    input_names.append(parts[0].strip().strip('"'))
                    input_types.append(parts[1].strip())

        # Parsing output
        output_parts = output_str.strip().strip('"').split(',')
        if len(output_parts) >= 2:
            output_name = output_parts[0].strip()
            output_type = output_parts[1].strip()
            output = (output_name, output_type)
        else:
            output = (None, None)

        return endpoint, output

    def build_call(self, thing_id, space_id, service_name, service_inputs):
        """Build the service call string"""
        call_data = {
            "Tweet Type": "Service call",
            "Thing ID": thing_id,
            "Space ID": space_id,
            "Service Name": service_name,
            "Service Inputs": service_inputs if service_inputs else "()"
        }
        return json.dumps(call_data, indent=2)

    def execute_service_call(self, call_data):
        """Execute the actual service call"""
        self.write_to_terminal(f"🔄 Executing service call: {call_data['Service Name']}")
        self.write_to_terminal(f"📋 Thing ID: {call_data['Thing ID']}", "blue")
        self.write_to_terminal(f"🏠 Space ID: {call_data['Space ID']}", "blue")
        self.write_to_terminal(f"📥 Inputs: {call_data['Service Inputs']}", "blue")
        
        try:
            # Here you would make the actual API call
            # For now, simulate with a delay and mock response
            self.write_to_terminal("⏳ Processing request...")
            time.sleep(1.5)  # Simulate API call delay
            
            # Mock successful response
            self.write_to_terminal(f"✅ Service '{call_data['Service Name']}' executed successfully")
            self.write_to_terminal("📤 Response: Operation completed", "blue")
            return True
            
        except Exception as e:
            self.write_to_terminal(f"❌ Error executing service: {str(e)}", "red")
            return False

    def execute_app(self, app):
        """Main execution function for the selected app"""
        # Create and show terminal window
        self.create_terminal_window()
        self.clear_terminal()
        
        # Start execution in a separate thread
        def run_app():
            self.write_to_terminal(f"🚀 Starting execution of app: {app.name}")
            self.write_to_terminal("=" * 60)
            
            try:
                # Check if app has services attribute
                if hasattr(app, 'services') and app.services:
                    self.write_to_terminal(f"📋 Found {len(app.services)} service(s) to execute")
                    
                    for i, service in enumerate(app.services, 1):
                        self.write_to_terminal(f"\n🔧 Processing service {i}/{len(app.services)}: {service.get('name', 'Unknown')}")
                        
                        # Parse API string
                        api_str = service.get('api_string', '')
                        if not api_str:
                            self.write_to_terminal("⚠️  No API string found for this service", "yellow")
                            continue
                        
                        input_names = []
                        input_types = []
                        
                        try:
                            endpoint, output = self.parse_api_string(api_str, input_names, input_types)
                            self.write_to_terminal(f"🎯 Endpoint: {endpoint}", "blue")
                            if output[0]:
                                self.write_to_terminal(f"📤 Expected output: {output[0]} ({output[1]})", "blue")
                        except ValueError as e:
                            self.write_to_terminal(f"❌ Error parsing API string: {e}", "red")
                            continue
                        
                        # Check if inputs are needed
                        service_inputs = "()"
                        if input_names:
                            self.write_to_terminal(f"📝 Service requires {len(input_names)} input parameter(s):")
                            input_values = []
                            
                            for name, type_ in zip(input_names, input_types):
                                prompt = f"🔍 Enter value for '{name}' (type: {type_}): "
                                user_value = self.get_user_input_from_terminal(prompt)
                                input_values.append(user_value)
                                self.write_to_terminal(f"✅ {name} = '{user_value}'")
                            
                            service_inputs = f"({','.join(input_values)})"
                        else:
                            self.write_to_terminal("ℹ️  No input parameters required", "blue")
                        
                        # Build the call
                        thing_id = service.get('thing_id', 'MySmartThing01')
                        space_id = service.get('space_id', 'MySmartSpace')
                        service_name = service.get('name', endpoint)
                        
                        call_json = self.build_call(thing_id, space_id, service_name, service_inputs)
                        self.write_to_terminal("📋 Built service call:")
                        for line in call_json.split('\n'):
                            self.write_to_terminal(f"    {line}", "blue")
                        
                        # Execute the call
                        call_data = json.loads(call_json)
                        success = self.execute_service_call(call_data)
                        
                        if not success:
                            self.write_to_terminal("🛑 Execution stopped due to error", "red")
                            break
                        
                        self.write_to_terminal("─" * 40)
                    
                    self.write_to_terminal("=" * 60)
                    self.write_to_terminal("🎉 App execution completed successfully!")
                
                else:
                    # Fallback for apps without services attribute
                    self.write_to_terminal("⚠️  App structure not recognized or no services found", "yellow")
                    self.write_to_terminal("🔄 Attempting to use legacy invoke_iot_app method...")
                    
                    try:
                        invoke_iot_app(app)
                        self.write_to_terminal("✅ Legacy execution completed")
                    except Exception as e:
                        self.write_to_terminal(f"❌ Legacy execution failed: {str(e)}", "red")
                    
            except Exception as e:
                self.write_to_terminal(f"💥 Fatal error during execution: {str(e)}", "red")
                self.write_to_terminal("🔍 Please check the app configuration and try again", "yellow")
        
        # Run in separate thread to prevent UI blocking
        execution_thread = threading.Thread(target=run_app, daemon=True)
        execution_thread.start()