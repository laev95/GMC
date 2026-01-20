from src.gq.device import GMCDevice
from src.gq.errors import ServiceError

from tkinter import *
from tkinter import ttk, scrolledtext
import threading
from typing import Callable, Any
from queue import Queue


class GMCDataViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("GMC Data Viewer")
        self.root.geometry("800x600")
        self.root.iconphoto(False, PhotoImage(file="src/ui/radiation_icon.png"))

        self.device = GMCDevice()
        self.is_connected = False
        self.device_name = ""
        self.current_view = None
        self.radiation_active = False
        self.radiation_update_job = None

        # Thread safety for serial operations
        self.serial_lock = threading.Lock()
        self.task_queue = Queue()
        self.is_shutting_down = False

        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

        self._setup_header()
        self._setup_main_layout()

        self._connect_device()

    def _setup_header(self):
        """Setup header with connection status, device name, and port selector"""
        header_frame = ttk.Frame(self.root, padding="10")
        header_frame.grid(row=0, column=0, columnspan=2, sticky=(W, E), padx=10, pady=(10, 5))

        # Port selector
        ttk.Label(header_frame, text="Port:").grid(row=0, column=0, sticky=W, padx=(20, 5))

        self.port_var = StringVar()
        self.port_dropdown = ttk.Combobox(header_frame, textvariable=self.port_var,
                                          width=15, state='readonly')
        self.port_dropdown.grid(row=0, column=1, sticky=W, padx=(0, 10))

        self.device_label = ttk.Label(header_frame, text=f"{self.device_name}",
                                      font=('TkDefaultFont', 12, 'bold'))
        self.device_label.grid(row=0, column=2, sticky=W, padx=(0, 10))
        # Connect button
        self.connect_btn = ttk.Button(header_frame, text="Connect", command=self._manual_connect)
        self.connect_btn.grid(row=0, column=3, sticky=W)

        # Refresh ports button
        ttk.Button(header_frame, text="↻", width=3,
                  command=self._refresh_ports).grid(row=0, column=4, sticky=W, padx=(5, 0))

        self._refresh_ports()

    def _on_closing(self):
        """Handle window close event"""
        self.is_shutting_down = True
        self.radiation_active = False
        if self.radiation_update_job:
            self.root.after_cancel(self.radiation_update_job)
        if self.is_connected:
            self.device.disconnect()
        self.root.destroy()

    def _run_serial_task(self, task: Callable[[], Any], on_success: Callable[[Any], None] = None,
                        on_error: Callable[[Exception], None] = None):
        """
        Execute a blocking serial task in a background thread and handle the result in the main thread.

        :param task: The blocking function to execute (e.g., lambda: self.device.radiation.get_cpm())
        :param on_success: Callback to execute in main thread with the result
        :param on_error: Callback to execute in main thread if an error occurs
        """
        def worker():
            if self.is_shutting_down:
                return

            try:
                with self.serial_lock:
                    result = task()

                # Schedule the success callback in the main thread
                if on_success and not self.is_shutting_down:
                    self.root.after(0, lambda: on_success(result))
            except ServiceError as e:
                # Schedule the error callback in the main thread
                if on_error and not self.is_shutting_down:
                    self.root.after(0, lambda: on_error(e))

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

    def _setup_main_layout(self):
        """Setup the main two-column layout"""
        # Configure grid weights
        self.root.grid_columnconfigure(0, weight=1, minsize=160)  # 20% for left column
        self.root.grid_columnconfigure(1, weight=4, minsize=640)  # 80% for right column
        self.root.grid_rowconfigure(1, weight=1)

        # Left column - Navigation
        left_frame = ttk.Frame(self.root, padding="10")
        left_frame.grid(row=1, column=0, sticky=(N, S, W, E), padx=(10, 5), pady=(5, 10))

        ttk.Label(left_frame, text="Services", font=('TkDefaultFont', 10, 'bold')).pack(
            anchor=W, pady=(0, 10))

        # Service buttons (excluding config and sensors)
        services = [
            ("Radiation", self._show_radiation),
            ("History", self._show_history),
            ("Device Info", self._show_device_info),
            ("Audio", self._show_audio),
            ("Power", self._show_power),
            ("Input Keys", self._show_input_keys),
            ("RTC", self._show_rtc),
            ("WiFi", self._show_wifi),
            ("Heartbeat", self._show_heartbeat),
        ]

        for service_name, command in services:
            btn = ttk.Button(left_frame, text=service_name, command=command, width=18)
            btn.pack(fill=X, pady=2)

        # Right column - Content area
        self.content_frame = ttk.Frame(self.root, padding="10", relief="sunken", borderwidth=1)
        self.content_frame.grid(row=1, column=1, sticky=(N, S, W, E), padx=(5, 10), pady=(5, 10))

        # Show default view
        self._show_radiation()

    def _refresh_ports(self):
        """Refresh available serial ports"""
        def task():
            return self.device.get_available_ports()

        def on_success(ports):
            port_list = list(ports.values()) if ports else []
            self.port_dropdown['values'] = port_list
            if port_list and not self.port_var.get():
                self.port_var.set(port_list[0])

        self._run_serial_task(task, on_success)

    def _connect_device(self, port=""):
        """Connect to the device"""
        def task():
            self.device.connect(port)
            if self.device.connection_status:
                try:
                    device_name = self.device.device_info.get_hardware_model()
                except ServiceError:
                    device_name = "Connected"
                return True, device_name
            return False, "Not Connected"

        def on_success(result):
            connected, device_name = result
            self.is_connected = connected

            if self.is_connected:
                self.device_name = device_name
                self.device_label.config(text=f"{self.device_name}")
                self.connect_btn.config(text="Disconnect")
            else:
                self._set_disconnected_state()

        def on_error(e):
            self._set_disconnected_state()
            self._show_error(f"Connection failed: {e}")

        self._run_serial_task(task, on_success, on_error)

    def _manual_connect(self):
        """Manual connect/disconnect toggle"""
        if self.is_connected:
            # Disconnect is quick, can be done synchronously
            with self.serial_lock:
                self.device.disconnect()
            self._set_disconnected_state()
        else:
            port = self.port_var.get()
            self._connect_device(port if port else "")

    def _set_disconnected_state(self):
        """Set UI to disconnected state"""
        self.is_connected = False
        self.device_name = ""
        self.device_label.config(text=f"{self.device_name}")
        self.connect_btn.config(text="Connect")

    def _clear_content(self):
        """Clear the content frame"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Cancel any scheduled updates
        if self.radiation_update_job:
            self.root.after_cancel(self.radiation_update_job)
            self.radiation_update_job = None
        self.radiation_active = False

    def _show_error(self, message):
        """Show error message in content area"""
        error_label = ttk.Label(self.content_frame, text=f"⚠ {message}",
                               foreground='red', font=('TkDefaultFont', 10))
        error_label.pack(pady=10)

    def _check_connection(self):
        """Check if device is connected, show error if not"""
        if not self.is_connected:
            self._show_error("Device not connected!")
            return False
        return True

    # Service Views

    def _show_radiation(self):
        """Show radiation monitoring view"""
        self._clear_content()
        self.current_view = "radiation"

        ttk.Label(self.content_frame, text="Radiation Monitor",
                 font=('TkDefaultFont', 14, 'bold')).pack(anchor=W, pady=(0, 10))

        if not self._check_connection():
            return

        # Control buttons
        btn_frame = ttk.Frame(self.content_frame)
        btn_frame.pack(anchor=W, pady=(0, 20))

        self.rad_start_btn = ttk.Button(btn_frame, text="▶ Start",
                                        command=self._toggle_radiation_monitoring)
        self.rad_start_btn.pack(side=LEFT, padx=(0, 5))

        ttk.Button(btn_frame, text="↻ Update Once",
                  command=self._update_radiation_once).pack(side=LEFT)

        # Data display frame
        data_frame = ttk.LabelFrame(self.content_frame, text="Standard Values", padding="10")
        data_frame.pack(fill=BOTH, expand=True, pady=(0, 10))

        self.rad_labels = {}
        labels = ['CPM', 'CPS', 'Max CPS']
        for i, label in enumerate(labels):
            ttk.Label(data_frame, text=f"{label}:").grid(row=i, column=0, sticky=W, pady=5)
            self.rad_labels[label] = ttk.Label(data_frame, text="--", font=('TkDefaultFont', 10, 'bold'))
            self.rad_labels[label].grid(row=i, column=1, sticky=W, padx=(10, 0), pady=5)

        # Dual-tube frame
        dual_frame = ttk.LabelFrame(self.content_frame, text="Dual-Tube (GMC-500+)", padding="10")
        dual_frame.pack(fill=BOTH, expand=True)

        dual_labels = ['High Tube CPM', 'Low Tube CPM']
        for i, label in enumerate(dual_labels):
            ttk.Label(dual_frame, text=f"{label}:").grid(row=i, column=0, sticky=W, pady=5)
            self.rad_labels[label] = ttk.Label(dual_frame, text="--", font=('TkDefaultFont', 10, 'bold'))
            self.rad_labels[label].grid(row=i, column=1, sticky=W, padx=(10, 0), pady=5)

    def _toggle_radiation_monitoring(self):
        """Toggle automatic radiation data updates"""
        self.radiation_active = not self.radiation_active
        if self.radiation_active:
            self.rad_start_btn.config(text="⬛ Stop")
            self._update_radiation_loop()
        else:
            self.rad_start_btn.config(text="▶ Start")
            if self.radiation_update_job:
                self.root.after_cancel(self.radiation_update_job)
                self.radiation_update_job = None

    def _update_radiation_loop(self):
        """Periodic radiation data update"""
        if self.radiation_active and self.current_view == "radiation":
            self._update_radiation_once()
            self.radiation_update_job = self.root.after(1000, self._update_radiation_loop)

    def _update_radiation_once(self):
        """Update radiation data once"""
        if not self.is_connected:
            return

        def task():
            # Perform all serial reads in one locked operation
            cpm = self.device.radiation.get_cpm()
            cps = self.device.radiation.get_cps()
            max_cps = self.device.radiation.get_max_cps()
            cpm_h = self.device.radiation.get_cpm_high_tube()
            cpm_l = self.device.radiation.get_cpm_low_tube()
            return cpm, cps, max_cps, cpm_h, cpm_l

        def on_success(result):
            cpm, cps, max_cps, cpm_h, cpm_l = result
            self.rad_labels['CPM'].config(text=str(cpm))
            self.rad_labels['CPS'].config(text=str(cps))
            self.rad_labels['Max CPS'].config(text=str(max_cps))
            self.rad_labels['High Tube CPM'].config(text=str(cpm_h))
            self.rad_labels['Low Tube CPM'].config(text=str(cpm_l))

        def on_error(e):
            self._show_error(f"Error reading radiation data: {e}")

        self._run_serial_task(task, on_success, on_error)

    def _show_history(self):
        """Show history data view"""
        self._clear_content()
        self.current_view = "history"

        ttk.Label(self.content_frame, text="History Data",
                 font=('TkDefaultFont', 14, 'bold')).pack(anchor=W, pady=(0, 10))

        if not self._check_connection():
            return

        ttk.Button(self.content_frame, text="📊 Get History Data",
                  command=self._fetch_history).pack(anchor=W, pady=(0, 10))

        # Text area for history data
        self.history_text = scrolledtext.ScrolledText(self.content_frame, wrap=WORD,
                                                       height=20, width=80)
        self.history_text.pack(fill=BOTH, expand=True)

    def _fetch_history(self):
        """Fetch history data from device"""
        self.history_text.delete(1.0, END)
        self.history_text.insert(1.0, "Fetching history data... This may take a while...\n")
        self.root.update()

        def task():
            return self.device.history.get_history()

        def on_success(history):
            self.history_text.delete(1.0, END)
            self.history_text.insert(1.0, history)

        def on_error(e):
            self.history_text.delete(1.0, END)
            self.history_text.insert(1.0, f"Error: {e}")

        self._run_serial_task(task, on_success, on_error)

    def _show_device_info(self):
        """Show device information view"""
        self._clear_content()
        self.current_view = "device_info"

        ttk.Label(self.content_frame, text="Device Information",
                 font=('TkDefaultFont', 14, 'bold')).pack(anchor=W, pady=(0, 20))

        if not self._check_connection():
            return

        info_frame = ttk.Frame(self.content_frame)
        info_frame.pack(fill=BOTH, expand=True)

        def task():
            model = self.device.device_info.get_hardware_model()
            serial = self.device.device_info.get_serial_number_bytes().hex()
            voltage = self.device.device_info.get_voltage()
            return (model, serial, voltage)

        def on_success(result):
            model, serial, voltage = result
            info = [
                ("Hardware Model:", model),
                ("Serial Number:", serial),
                ("Voltage:", voltage),
            ]

            for i, (label, value) in enumerate(info):
                ttk.Label(info_frame, text=label).grid(row=i, column=0, sticky=W, pady=10, padx=(0, 10))
                ttk.Label(info_frame, text=value, font=('TkDefaultFont', 10, 'bold')).grid(
                    row=i, column=1, sticky=W, pady=10)

        def on_error(e):
            self._show_error(f"Error reading device info: {e}")

        self._run_serial_task(task, on_success, on_error)

    def _show_audio(self):
        """Show audio controls view"""
        self._clear_content()
        self.current_view = "audio"

        ttk.Label(self.content_frame, text="Audio Controls",
                 font=('TkDefaultFont', 14, 'bold')).pack(anchor=W, pady=(0, 20))

        if not self._check_connection():
            return

        # Echo controls
        echo_frame = ttk.LabelFrame(self.content_frame, text="Echo", padding="10")
        echo_frame.pack(fill=X, pady=(0, 10))

        ttk.Button(echo_frame, text="Echo ON",
                  command=lambda: self._audio_cmd("echo_on")).pack(side=LEFT, padx=5)
        ttk.Button(echo_frame, text="Echo OFF",
                  command=lambda: self._audio_cmd("echo_off")).pack(side=LEFT, padx=5)

        # Alarm controls
        alarm_frame = ttk.LabelFrame(self.content_frame, text="Alarm", padding="10")
        alarm_frame.pack(fill=X)

        ttk.Button(alarm_frame, text="Alarm ON",
                  command=lambda: self._audio_cmd("alarm_on")).pack(side=LEFT, padx=5)
        ttk.Button(alarm_frame, text="Alarm OFF",
                  command=lambda: self._audio_cmd("alarm_off")).pack(side=LEFT, padx=5)

        # Status label
        self.audio_status = ttk.Label(self.content_frame, text="", foreground='green')
        self.audio_status.pack(pady=20)

    def _audio_cmd(self, cmd):
        """Execute audio command"""
        def task():
            return getattr(self.device.audio, cmd)()

        def on_success(result):
            self.audio_status.config(text=f"✓ Command '{cmd}' executed successfully",
                                    foreground='green')

        def on_error(e):
            self.audio_status.config(text=f"✗ Error: {e}", foreground='red')

        self._run_serial_task(task, on_success, on_error)

    def _show_power(self):
        """Show power controls view"""
        self._clear_content()
        self.current_view = "power"

        ttk.Label(self.content_frame, text="Power Controls",
                 font=('TkDefaultFont', 14, 'bold')).pack(anchor=W, pady=(0, 20))

        if not self._check_connection():
            return

        ttk.Label(self.content_frame, text="⚠ Warning: These commands may disconnect the device!",
                 foreground='orange').pack(pady=10)

        btn_frame = ttk.Frame(self.content_frame)
        btn_frame.pack(pady=20)

        ttk.Button(btn_frame, text="Power ON",
                  command=lambda: self._power_cmd("power_on")).pack(side=LEFT, padx=10)
        ttk.Button(btn_frame, text="Power OFF",
                  command=lambda: self._power_cmd("power_off")).pack(side=LEFT, padx=10)
        ttk.Button(btn_frame, text="Reboot",
                  command=lambda: self._power_cmd("reboot")).pack(side=LEFT, padx=10)

        self.power_status = ttk.Label(self.content_frame, text="")
        self.power_status.pack(pady=20)

    def _power_cmd(self, cmd):
        """Execute power command"""
        def task():
            return getattr(self.device.power, cmd)()

        def on_success(result):
            self.power_status.config(text=f"✓ Command '{cmd}' sent", foreground='green')

        def on_error(e):
            self.power_status.config(text=f"✗ Error: {e}", foreground='red')

        self._run_serial_task(task, on_success, on_error)

    def _show_input_keys(self):
        """Show input keys view"""
        self._clear_content()
        self.current_view = "input_keys"

        ttk.Label(self.content_frame, text="Input Keys",
                 font=('TkDefaultFont', 14, 'bold')).pack(anchor=W, pady=(0, 20))

        if not self._check_connection():
            return

        ttk.Label(self.content_frame, text="Send key presses to the device:").pack(anchor=W, pady=10)

        btn_frame = ttk.Frame(self.content_frame)
        btn_frame.pack(pady=20)

        for i in range(4):
            ttk.Button(btn_frame, text=f"Key {i}",
                      command=lambda k=i: self._send_key(k)).pack(side=LEFT, padx=5)

        self.key_status = ttk.Label(self.content_frame, text="")
        self.key_status.pack(pady=20)

    def _send_key(self, key):
        """Send key press to device"""
        def task():
            return self.device.input_keys.send_key(key)

        def on_success(result):
            self.key_status.config(text=f"✓ Key {key} sent", foreground='green')

        def on_error(e):
            self.key_status.config(text=f"✗ Error: {e}", foreground='red')

        self._run_serial_task(task, on_success, on_error)

    def _show_rtc(self):
        """Show RTC (Real-Time Clock) view"""
        self._clear_content()
        self.current_view = "rtc"

        ttk.Label(self.content_frame, text="Real-Time Clock (RTC)",
                 font=('TkDefaultFont', 14, 'bold')).pack(anchor=W, pady=(0, 20))

        if not self._check_connection():
            return

        ttk.Button(self.content_frame, text="🕐 Get Device Time",
                  command=self._get_device_time).pack(anchor=W, pady=(0, 20))

        self.rtc_display = ttk.Label(self.content_frame, text="", font=('TkDefaultFont', 12))
        self.rtc_display.pack(pady=20)

    def _get_device_time(self):
        """Get device date/time"""
        def task():
            return self.device.rtc.get_datetime()

        def on_success(dt):
            time_str = (f"Device Time:\n"
                       f"20{dt.year_since_2000:02d}-{dt.month:02d}-{dt.day:02d} "
                       f"{dt.hour:02d}:{dt.minute:02d}:{dt.second:02d}")
            self.rtc_display.config(text=time_str, foreground='black')

        def on_error(e):
            self.rtc_display.config(text=f"Error: {e}", foreground='red')

        self._run_serial_task(task, on_success, on_error)

    def _show_wifi(self):
        """Show WiFi configuration view"""
        self._clear_content()
        self.current_view = "wifi"

        ttk.Label(self.content_frame, text="WiFi Configuration",
                 font=('TkDefaultFont', 14, 'bold')).pack(anchor=W, pady=(0, 20))

        if not self._check_connection():
            return

        # SSID
        ssid_frame = ttk.Frame(self.content_frame)
        ssid_frame.pack(fill=X, pady=5)
        ttk.Label(ssid_frame, text="SSID:", width=15).pack(side=LEFT)
        self.wifi_ssid = ttk.Entry(ssid_frame, width=30)
        self.wifi_ssid.pack(side=LEFT, padx=5)
        ttk.Button(ssid_frame, text="Set",
                  command=lambda: self._set_wifi("ssid")).pack(side=LEFT)

        # Password
        pw_frame = ttk.Frame(self.content_frame)
        pw_frame.pack(fill=X, pady=5)
        ttk.Label(pw_frame, text="Password:", width=15).pack(side=LEFT)
        self.wifi_pw = ttk.Entry(pw_frame, width=30, show="*")
        self.wifi_pw.pack(side=LEFT, padx=5)
        ttk.Button(pw_frame, text="Set",
                  command=lambda: self._set_wifi("password")).pack(side=LEFT)

        # Website
        web_frame = ttk.Frame(self.content_frame)
        web_frame.pack(fill=X, pady=5)
        ttk.Label(web_frame, text="Website:", width=15).pack(side=LEFT)
        self.wifi_website = ttk.Entry(web_frame, width=30)
        self.wifi_website.pack(side=LEFT, padx=5)
        ttk.Button(web_frame, text="Set",
                  command=lambda: self._set_wifi("website")).pack(side=LEFT)

        # URL
        url_frame = ttk.Frame(self.content_frame)
        url_frame.pack(fill=X, pady=5)
        ttk.Label(url_frame, text="URL:", width=15).pack(side=LEFT)
        self.wifi_url = ttk.Entry(url_frame, width=30)
        self.wifi_url.pack(side=LEFT, padx=5)
        ttk.Button(url_frame, text="Set",
                  command=lambda: self._set_wifi("url")).pack(side=LEFT)

        self.wifi_status = ttk.Label(self.content_frame, text="")
        self.wifi_status.pack(pady=20)

    def _set_wifi(self, param):
        """Set WiFi parameter"""
        def task():
            if param == "ssid":
                return self.device.wifi.set_wifi_ssid(self.wifi_ssid.get())
            elif param == "password":
                return self.device.wifi.set_wifi_password(self.wifi_pw.get())
            elif param == "website":
                return self.device.wifi.set_website(self.wifi_website.get())
            elif param == "url":
                return self.device.wifi.set_url(self.wifi_url.get())
            return None

        def on_success(result):
            self.wifi_status.config(text=f"✓ {param.upper()} set successfully",
                                   foreground='green')

        def on_error(e):
            self.wifi_status.config(text=f"✗ Error: {e}", foreground='red')

        self._run_serial_task(task, on_success, on_error)

    def _show_heartbeat(self):
        """Show heartbeat view"""
        self._clear_content()
        self.current_view = "heartbeat"

        ttk.Label(self.content_frame, text="Heartbeat Monitor",
                 font=('TkDefaultFont', 14, 'bold')).pack(anchor=W, pady=(0, 20))

        if not self._check_connection():
            return

        ttk.Label(self.content_frame,
                 text="⚠ Note: Heartbeat streaming may interfere with other operations",
                 foreground='orange').pack(pady=10)

        btn_frame = ttk.Frame(self.content_frame)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Start Heartbeat",
                  command=self._start_heartbeat).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="Stop Heartbeat",
                  command=self._stop_heartbeat).pack(side=LEFT, padx=5)

        self.heartbeat_text = scrolledtext.ScrolledText(self.content_frame,
                                                        wrap=WORD, height=15, width=60)
        self.heartbeat_text.pack(fill=BOTH, expand=True, pady=10)

    def _start_heartbeat(self):
        """Start heartbeat monitoring"""
        self.heartbeat_text.insert(END, "Starting heartbeat...\n")
        self.heartbeat_text.insert(END, "Note: This is a placeholder. ")
        self.heartbeat_text.insert(END, "Actual implementation requires async handling.\n")

    def _stop_heartbeat(self):
        """Stop heartbeat monitoring"""
        def task():
            return self.device.heartbeat.turn_off_heartbeat()

        def on_success(result):
            self.heartbeat_text.insert(END, "Heartbeat stopped.\n")

        def on_error(e):
            self.heartbeat_text.insert(END, f"Error: {e}\n")

        self._run_serial_task(task, on_success, on_error)

    def run(self):
        """Run the application"""
        self.root.mainloop()
