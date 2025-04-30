import sys
import numpy as np
import pandas as pd
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QTabWidget, QFrame, QHBoxLayout, QGridLayout, QRadioButton, QGroupBox, QPushButton, QFileDialog
from PyQt5.QtCore import Qt, QTimer, QDateTime
from PyQt5.QtWidgets import QComboBox, QTextEdit, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QGroupBox
from PyQt5.QtGui import QFont, QColor, QPalette
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QComboBox, QRadioButton, QLineEdit, QFrame, QLabel, QPushButton, QFileDialog, QFormLayout, QDateTimeEdit
import serial.tools.list_ports
import pyqtgraph as pg
import pandas as pd
from PyQt5.QtCore import QTimer, QDateTime
from datetime import datetime
import pyqtgraph as pg
from scipy.stats import skew, kurtosis
import serial.tools.list_ports
from scipy.stats import skew, kurtosis

class OfflineLayer(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("offlineFrame")

        self.data = None  # To store loaded CSV data
        self.plot_type = "Frequency vs Time"  # Default plot type
        self.amplitude_data = None
        self.time_data = None
        self.file_path = "---"  # Initialize the file path to show no file selected initially

        # Set layout for the offline layer
        offline_layout = QVBoxLayout()

        # Create a PyQtGraph PlotWidget for offline graph
        self.offline_graph = pg.PlotWidget()
        self.offline_graph.setMinimumHeight(300)# Set a minimum height for the graph
        self.offline_graph.setBackground('w')
        self.offline_graph.showGrid(x=True, y=True, alpha=0.3)
        self.offline_graph.setLabel('left', 'Amplitude / Frequency / Parameter', color='#333', size='12pt')
        self.offline_graph.setLabel('bottom', 'Time (s)', color='#333', size='12pt')
        self.offline_graph.getAxis('left').setPen(pg.mkPen(color='#555', width=1.5))
        self.offline_graph.getAxis('bottom').setPen(pg.mkPen(color='#555', width=1.5))
        offline_legend = self.offline_graph.addLegend(offset=(10, 10))
        offline_legend.labelTextStyle = {'color': '#444', 'size': '10pt'}

        self.offline_graph_frame = QFrame()
        self.offline_graph_frame.setFrameShape(QFrame.StyledPanel)
        self.offline_graph_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 2px solid #e0e0e0;
                border-radius: 12px;
                padding: 10px;
            }
        """)
        self.offline_graph_layout = QVBoxLayout()
        self.offline_graph_layout.addWidget(self.offline_graph)
        self.offline_graph_frame.setLayout(self.offline_graph_layout)

        # Add to your main layout
        offline_layout.addWidget(self.offline_graph_frame)



        # Create a QFrame for additional widgets inside the Offline tab
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame_layout = QVBoxLayout()

        # Create a QLabel for current date and time (now inside the frame)
        self.time_display = QLabel()
        self.file_status_display = QLabel("File Status: ---")  # To display file status
        self.update_time()
        timer = QTimer(self)
        timer.timeout.connect(self.update_time)
        timer.start(1000)  # Update every second

        # Add time and file status display inside the frame, above buttons
        frame_layout.addWidget(self.time_display)
        frame_layout.addWidget(self.file_status_display)

        # Create a QGroupBox for Plot Settings with radio buttons
        plot_settings_group = QGroupBox("PLOT SETTINGS")
        plot_settings_layout = QVBoxLayout()

        # Create radio buttons for "Frequency vs Time" and "Parameter vs Time"
        self.freq_radio = QRadioButton("Frequency vs Time")
        self.param_radio = QRadioButton("Parameter vs Time")
        self.freq_radio.setChecked(True)  # Default selection is "Frequency vs Time"
        self.freq_radio.toggled.connect(self.update_plot_type)
        self.param_radio.toggled.connect(self.update_plot_type)
        plot_settings_layout.addWidget(self.freq_radio)
        plot_settings_layout.addWidget(self.param_radio)

        plot_settings_group.setLayout(plot_settings_layout)

        # Create a QGroupBox for Statistics section
        stats_group = QGroupBox("STATISTICS")
        stats_layout = QGridLayout()

        # Instead of QTextEdit, we will display "---" for each statistic value
        self.max_amp_label = QLabel("---")
        self.std_dev_label = QLabel("---")
        self.skewness_label = QLabel("---")
        self.kurtosis_label = QLabel("---")
        self.avg_label = QLabel("---")


        # Add labels to the grid layout
        stats_layout.addWidget(QLabel("Maximum Amplitude"), 0, 0)
        stats_layout.addWidget(self.max_amp_label, 0, 1)

        stats_layout.addWidget(QLabel("Standard Deviation"), 1, 0)
        stats_layout.addWidget(self.std_dev_label, 1, 1)

        stats_layout.addWidget(QLabel("Skewness"), 2, 0)
        stats_layout.addWidget(self.skewness_label, 2, 1)

        stats_layout.addWidget(QLabel("Kurtosis"), 3, 0)
        stats_layout.addWidget(self.kurtosis_label, 3, 1)

        stats_layout.addWidget(QLabel("Average (10-12s)"), 4, 0)
        stats_layout.addWidget(self.avg_label, 4, 1)

        stats_group.setLayout(stats_layout)

        # Create a QGroupBox for Probe Parameter (No ListWidget, only Labels)
        probe_param_group = QGroupBox("PROBE PARAMETER")
        
        # Create labels to show Probe Parameters
        self.param_label = QLabel("Parameter: ---")
        self.unit_label = QLabel("Unit: ---")
        self.coeff_a_label = QLabel("coeff a: ---")
        self.coeff_b_label = QLabel("coeff b: ---")
        self.coeff_c_label = QLabel("coeff c: ---")
        self.coeff_d_label = QLabel("coeff d: ---")
        
        # Create a layout to organize the labels in the Probe Parameter group
        probe_param_layout = QVBoxLayout()
        probe_param_layout.addWidget(self.param_label)
        probe_param_layout.addWidget(self.unit_label)
        probe_param_layout.addWidget(self.coeff_a_label)
        probe_param_layout.addWidget(self.coeff_b_label)
        probe_param_layout.addWidget(self.coeff_c_label)
        probe_param_layout.addWidget(self.coeff_d_label)
        
        probe_param_group.setLayout(probe_param_layout)

        # Create buttons (Browse and Start) inside a horizontal layout (side by side)
        button_layout = QHBoxLayout()
        
        browse_button = QPushButton("Browse")
        start_button = QPushButton("Start")
        browse_button.clicked.connect(self.browse_file)
        start_button.clicked.connect(self.load_data)  # Directly load the data when "Start" is clicked

        # Adjust the button size to fit the new layout
        browse_button.setFixedWidth(150)
        start_button.setFixedWidth(150)

        # Add buttons to horizontal layout
        button_layout.addWidget(browse_button)
        button_layout.addWidget(start_button)

        # Layout for the frame (to position the radio buttons, list widgets, and buttons)
        frame_inner_layout = QHBoxLayout()

        # Create a layout for the left section (for Plot Settings, Statistics)
        left_layout = QVBoxLayout()
        left_layout.addWidget(plot_settings_group)
        left_layout.addWidget(stats_group)

        # Create a layout for the right section (for Probe Parameter and Buttons)
        right_layout = QVBoxLayout()
        right_layout.addWidget(probe_param_group)
        right_layout.addLayout(button_layout)  # Add the button layout here

        # Add the left and right sections to the frame layout
        frame_inner_layout.addLayout(left_layout)
        frame_inner_layout.addLayout(right_layout)

        # Add the frame layout (with time display and buttons) to the frame
        frame_layout.addLayout(frame_inner_layout)
        frame.setLayout(frame_layout)

        # Add the frame to the offline layout (below the graph)
        offline_layout.addWidget(frame)

        # Set layout for offline layer
        self.setLayout(offline_layout)

    def update_time(self):
        current_time = QDateTime.currentDateTime()
        formatted_time = current_time.toString("yyyy-MM-dd hh:mm:ss")
        self.time_display.setText(f"Current Date and Time: {formatted_time}")
        self.file_status_display.setText(f"File Status: {self.file_path}")  # Display file path

    def update_plot_type(self):
        if self.freq_radio.isChecked():
            self.plot_type = "Frequency vs Time"
            self.param_label.setText("Parameter: ---")
            self.unit_label.setText("Unit: ---")
            self.coeff_a_label.setText("coeff a: ---")
            self.coeff_b_label.setText("coeff b: ---")
            self.coeff_c_label.setText("coeff c: ---")
            self.coeff_d_label.setText("coeff d: ---")
        else:
            self.plot_type = "Parameter vs Time"

    def browse_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if file_name:
            self.file_path = file_name  # Store file path

    def load_data(self):
        if not self.file_path or self.file_path == "---":
            self.display_error_message("No file selected.")
            return

        try:
            # Read the CSV file
            self.data = pd.read_csv(self.file_path)

            # Try to find a valid 'Time' column (checking various variations)
            time_column_names = ['Time', 'Time(s)', 'time', 'time (s)', 'DateTime', 'Time(S)', 'Time (s)']
            time_column_found = False

            # Check for the presence of any of the time column variations
            for col in time_column_names:
                if col in self.data.columns:
                    self.time_data = self.data[col]
                    time_column_found = True
                    break

            if not time_column_found:
                self.display_error_message("The CSV file does not contain a valid 'Time' column.")
                return  # Stop further execution if no time column is found

            # Validate data for the chosen plot type
            valid, error_message = self.validate_data()
            if not valid:
                self.display_error_message(error_message)
                return

            # If the data is valid, proceed with calculating and displaying statistics
            self.calculate_statistics()
            self.plot_data_on_graph()

        except Exception as e:
            self.display_error_message(f"Error loading file: {str(e)}")
            self.amplitude_data = None
            self.time_data = None

    def display_error_message(self, message):
        # Display an error message on the interface (could be a QLabel or something else)
        print(message)  # Optionally print the error to the console for debugging purposes

    def validate_data(self):
        """Validate the necessary columns in the data."""
        if self.plot_type == "Frequency vs Time":
            if 'Frequency (Hz)' not in self.data.columns:
                return False, "The CSV file does not contain a 'Frequency' column."
            self.amplitude_data = self.data['Frequency (Hz)']
            self.param_label.setText("Parameter: Frequency")
            self.unit_label.setText("Unit: Hz")
        elif self.plot_type == "Parameter vs Time":
            if 'Amplitude' in self.data.columns:
                self.amplitude_data = self.data['Amplitude']
                self.param_label.setText("Parameter: Amplitude")
                self.unit_label.setText("Unit: Volts")
            elif 'Inductance' in self.data.columns:
                self.amplitude_data = self.data['Inductance']
                self.param_label.setText("Parameter: Inductance")
                self.unit_label.setText("Unit: Henry")
                self.coeff_a_label.setText(f"coeff a: {self.data['coeff_a'].iloc[0] if 'coeff_a' in self.data else '---'}")
                self.coeff_b_label.setText(f"coeff b: {self.data['coeff_b'].iloc[0] if 'coeff_b' in self.data else '---'}")
                self.coeff_c_label.setText(f"coeff c: {self.data['coeff_c'].iloc[0] if 'coeff_c' in self.data else '---'}")
                self.coeff_d_label.setText(f"coeff d: {self.data['coeff_d'].iloc[0] if 'coeff_d' in self.data else '---'}")
            elif 'Capacitance' in self.data.columns:
                self.amplitude_data = self.data['Capacitance']
                self.param_label.setText("Parameter: Capacitance")
                self.unit_label.setText("Unit: Farads")
                self.coeff_a_label.setText(f"coeff a: {self.data['coeff_a'].iloc[0] if 'coeff_a' in self.data else '---'}")
                self.coeff_b_label.setText(f"coeff b: {self.data['coeff_b'].iloc[0] if 'coeff_b' in self.data else '---'}")
                self.coeff_c_label.setText(f"coeff c: {self.data['coeff_c'].iloc[0] if 'coeff_c' in self.data else '---'}")
                self.coeff_d_label.setText(f"coeff d: {self.data['coeff_d'].iloc[0] if 'coeff_d' in self.data else '---'}")
            else:
                return False, "The CSV file does not contain a valid parameter column."
        else:
            return False, "Invalid plot type selected."
        
        return True, ""

    def calculate_statistics(self):
        if self.amplitude_data is not None:
            # Maximum amplitude
            max_amp = np.max(self.amplitude_data - np.mean(self.amplitude_data))
            std_dev = np.std(self.amplitude_data)
            skew_value = skew(self.amplitude_data)
            kurt_value = kurtosis(self.amplitude_data)

            # Update core stats
            self.max_amp_label.setText(f"{max_amp:.2f}")
            self.std_dev_label.setText(f"{std_dev:.2f}")
            self.skewness_label.setText(f"{skew_value:.2f}")
            self.kurtosis_label.setText(f"{kurt_value:.2f}")

            # Calculate average frequency between 10s and 12s (first 20 samples)
            try:
                time_array = self.time_data.astype(float)
                mask = (time_array >= 10) & (time_array <= 12)
                filtered_freq = self.data.loc[mask, 'Frequency (Hz)'].head(20)
                avg_val = filtered_freq.mean()
                self.avg_label.setText(f"{avg_val:.2f}")
            except Exception as e:
                self.avg_label.setText("N/A")
        else:
            # Reset stats
            self.max_amp_label.setText("---")
            self.std_dev_label.setText("---")
            self.skewness_label.setText("---")
            self.kurtosis_label.setText("---")
            self.avg_label.setText("---")

    def plot_data_on_graph(self):
        self.offline_graph.clear()  # Clear existing plot
        if self.plot_type == "Frequency vs Time":
            self.offline_graph.plot(
                self.time_data, self.amplitude_data,
                pen=pg.mkPen(color='#e53935', width=3),  # Vivid red
                symbol='o', symbolSize=6, symbolBrush='#e53935',
                name="Frequency"
            )
        elif self.plot_type == "Parameter vs Time":
            self.offline_graph.plot(
                self.time_data, self.amplitude_data,
                pen=pg.mkPen(color='#1e88e5', width=3),  # Vivid blue
                symbol='t', symbolSize=6, symbolBrush='#1e88e5',
                name="Parameter"
            )


import time  
import serial
import serial.tools.list_ports
import pandas as pd

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QGroupBox, QFileDialog, QRadioButton, QCheckBox,
    QFrame, QMessageBox
)
from PyQt5.QtCore import QTimer, QDateTime
import pyqtgraph as pg




class OnlineLayer(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("onlineFrame")

        self.timer = QTimer(self)
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.poll_serial_and_plot)
        self.serial_connection = None
        self.is_plotting = False
        self.time_data = []
        self.freq_data = []
        self.amplitude_data = []
        self.parameter_data = []
        self.sample_time = 10
        self.current_time = 0
        self.last_sample_timestamp = None
        self.plotting_window_sec = None

        online_layout = QVBoxLayout()
        main_layout = QHBoxLayout()

        self.online_graph = pg.PlotWidget()
        self.online_graph.setBackground('w')
        self.online_graph.setMinimumHeight(300)
        self.online_graph.showGrid(x=True, y=True, alpha=0.3)
        self.online_graph.setLabel('left', 'Amplitude / Frequency / Parameter', color='#333', size='12pt')
        self.online_graph.setLabel('bottom', 'Time (s)', color='#333', size='12pt')
        self.online_graph.getAxis('left').setPen(pg.mkPen(color='#555', width=1.5))
        self.online_graph.getAxis('bottom').setPen(pg.mkPen(color='#555', width=1.5))
        legend = self.online_graph.addLegend(offset=(10, 10))
        legend.labelTextStyle = {'color': '#444', 'size': '10pt'}
        self.online_graph.addLegend()
        self.graph_frame = QFrame()
        self.graph_frame.setFrameShape(QFrame.StyledPanel)
        self.graph_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 2px solid #e0e0e0;
                border-radius: 12px;
                padding: 10px;
            }
        """)
        self.graph_layout = QVBoxLayout()
        self.graph_layout.addWidget(self.online_graph)
        self.graph_frame.setLayout(self.graph_layout)

        right_frame = QFrame()
        right_frame.setFrameShape(QFrame.StyledPanel)
        right_frame.setMinimumWidth(250)

        right_layout = QVBoxLayout()
        port_settings_group = self.create_port_settings_group()
        graph_setting_group = self.create_graph_setting_group()
        probe_parameter_group = self.create_probe_parameter_group()
        right_layout.addWidget(port_settings_group)
        right_layout.addWidget(graph_setting_group)
        right_layout.addWidget(probe_parameter_group)
        right_frame.setLayout(right_layout)

        bottom_frame = QFrame()
        bottom_frame.setFrameShape(QFrame.StyledPanel)
        bottom_frame.setMinimumHeight(120)
        bottom_layout = QHBoxLayout()
        time_settings_group = self.create_time_settings_group()
        status_group = self.create_status_group()
        button_layout = self.create_button_layout()
        bottom_layout.addWidget(time_settings_group)
        bottom_layout.addWidget(status_group)
        bottom_layout.addLayout(button_layout)
        bottom_frame.setLayout(bottom_layout)

        main_layout.addWidget(self.online_graph)
        main_layout.addWidget(right_frame)
        online_layout.addLayout(main_layout)
        online_layout.addWidget(bottom_frame)

        self.setLayout(online_layout)

        self.freq_curve = self.online_graph.plot( [], [], pen=pg.mkPen(color='#2ecc71', width=3), name='Frequency')
        self.amplitude_curve = self.online_graph.plot( [], [], pen=pg.mkPen(color='#e74c3c', width=3), name='Amplitude')
        self.param_curve = self.online_graph.plot([], [], pen=pg.mkPen(color='#3498db', width=3), name='Parameter')


        self.update_time_timer = QTimer(self)
        self.update_time_timer.setInterval(1000)
        self.update_time_timer.timeout.connect(self.update_date_time)
        self.update_time_timer.start()

    def update_date_time(self):
        current_time = QDateTime.currentDateTime().toString('yyyy-MM-dd HH:mm:ss')
        self.date_time_label.setText(f"Date & Time: {current_time}")

    def start_plotting(self):
        if self.is_plotting:
            self.start_button.setText("Start Plotting")
            self.sample_time = int(self.sample_time_input.text())
            self.is_plotting = False
            self.timer.stop()
        else:
            self.start_button.setText("Stop Plotting")
            self.is_plotting = True
            self.connect_serial()
            self.timer.start()

    def connect_serial(self):
        try:
            port = self.port_combobox.currentText()
            baud_rate = int(self.baud_combobox.currentText())
            self.serial_connection = serial.Serial(port, baud_rate, timeout=0.01)
            self.status_label.setText("Connection Status: Connected")
        except Exception as e:
            self.status_label.setText("Connection Status: Not connected")
            print(f"Serial connection error: {e}")

    def populate_com_ports(self):
        ports = serial.tools.list_ports.comports()
        self.port_combobox.clear()
        for port in ports:
            self.port_combobox.addItem(port.device)

    def create_port_settings_group(self):
        group = QGroupBox("PORT SETTINGS")
        layout = QVBoxLayout()
        h_layout = QHBoxLayout()

        self.port_combobox = QComboBox()
        self.populate_com_ports()
        h_layout.addWidget(QLabel("Port:"))
        h_layout.addWidget(self.port_combobox)

        self.baud_combobox = QComboBox()
        self.baud_combobox.addItems(["9600", "115200", "38400", "57600", "19200", "14400"])
        h_layout.addWidget(QLabel("Baud Rate:"))
        h_layout.addWidget(self.baud_combobox)

        layout.addLayout(h_layout)
        group.setLayout(layout)
        return group

    def create_graph_setting_group(self):
        group = QGroupBox("GRAPH SETTING")
        layout = QVBoxLayout()

        self.freq_radio = QRadioButton("Frequency vs Time")
        self.param_radio = QRadioButton("Parameter vs Time")
        self.amplitude_radio = QRadioButton("Amplitude vs Time")
        self.freq_radio.setChecked(True)

        self.freq_radio.toggled.connect(self.update_plot_visibility)
        self.param_radio.toggled.connect(self.update_plot_visibility)
        self.amplitude_radio.toggled.connect(self.update_plot_visibility)

        layout.addWidget(self.freq_radio)
        layout.addWidget(self.param_radio)
        layout.addWidget(self.amplitude_radio)
        group.setLayout(layout)
        return group

    def update_plot_visibility(self):
        self.freq_curve.setVisible(self.freq_radio.isChecked())
        self.param_curve.setVisible(self.param_radio.isChecked())
        self.amplitude_curve.setVisible(self.amplitude_radio.isChecked())

    def create_probe_parameter_group(self):
        group = QGroupBox("PROBE PARAMETER")
        layout = QFormLayout()

        self.parameter_input = QLineEdit()
        self.unit_input = QLineEdit()
        self.coeff_a_input = QLineEdit("0")
        self.coeff_b_input = QLineEdit("0")
        self.coeff_c_input = QLineEdit("0")
        self.coeff_d_input = QLineEdit("0")

        layout.addRow("Parameter:", self.parameter_input)
        layout.addRow("Unit:", self.unit_input)
        layout.addRow("Coeff A:", self.coeff_a_input)
        layout.addRow("Coeff B:", self.coeff_b_input)
        layout.addRow("Coeff C:", self.coeff_c_input)
        layout.addRow("Coeff D:", self.coeff_d_input)

        group.setLayout(layout)
        return group

    def create_time_settings_group(self):
        group = QGroupBox("Time Settings")
        layout = QFormLayout()

        self.date_time_label = QLabel("Date & Time: ---")
        layout.addRow("Date & Time:", self.date_time_label)

        self.sample_time_input = QLineEdit(str(self.sample_time))
        layout.addRow("Sample Time (ms):", self.sample_time_input)

        self.plotting_time_input = QLineEdit("10")
        layout.addRow("Plotting Window (s):", self.plotting_time_input)

        group.setLayout(layout)
        return group

    def create_status_group(self):
        group = QGroupBox("Status")
        layout = QVBoxLayout()

        self.freq_label = QLabel("Frequency: ---")
        self.status_label = QLabel("Connection Status: Not connected")

        layout.addWidget(self.freq_label)
        layout.addWidget(self.status_label)
        group.setLayout(layout)
        return group

    def create_button_layout(self):
        layout = QVBoxLayout()

        self.save_button = QPushButton("Save as CSV")
        self.start_button = QPushButton("Start Plotting")
        self.clear_button = QPushButton("Clear Plot")

        self.save_button.clicked.connect(self.save_csv)
        self.start_button.clicked.connect(self.start_plotting)
        self.clear_button.clicked.connect(self.clear_plot)

        layout.addWidget(self.save_button)
        layout.addWidget(self.clear_button)
        layout.addWidget(self.start_button)
        return layout

    def poll_serial_and_plot(self):
        if not self.is_plotting or not self.serial_connection:
            return

        try:
            if self.serial_connection.in_waiting:
                line = self.serial_connection.readline()
                try:
                    decoded_line = line.decode('utf-8').strip()
                except UnicodeDecodeError:
                    return

                frequency = None
                amplitude = None

                if decoded_line.startswith("Frequency:"):
                    try:
                        frequency = float(decoded_line.split(":")[1].strip().split()[0])
                        self.freq_label.setText(f"Frequency: {frequency:.2f} Hz")
                    except:
                        return

                elif decoded_line.startswith("Amplitude:"):
                    try:
                        amplitude = float(decoded_line.split(":")[1].strip().split()[0])
                    except:
                        return

                # Append only when frequency is read (we assume it's the base signal)
                if frequency is not None:
                    self.current_time += self.sample_time / 1000.0
                    self.time_data.append(self.current_time)
                    self.freq_data.append(frequency)

                    # Amplitude fallback
                    if amplitude is not None:
                        self.amplitude_data.append(amplitude)
                    else:
                        self.amplitude_data.append(self.amplitude_data[-1] if self.amplitude_data else 0)

                    try:
                        a = float(self.coeff_a_input.text())
                        b = float(self.coeff_b_input.text())
                        c = float(self.coeff_c_input.text())
                        d = float(self.coeff_d_input.text())
                        parameter = a * frequency**3 + b * frequency**2 + c * frequency + d
                        self.parameter_data.append(parameter)
                    except:
                        self.parameter_data.append(0.0)

                    # Trim based on plotting window
                    max_window = float(self.plotting_time_input.text())
                    while self.time_data and self.current_time - self.time_data[0] > max_window:
                        self.time_data.pop(0)
                        self.freq_data.pop(0)
                        self.amplitude_data.pop(0)
                        self.parameter_data.pop(0)

                    # Update only the selected graph
                    self.freq_curve.setVisible(self.freq_radio.isChecked())
                    self.amplitude_curve.setVisible(self.amplitude_radio.isChecked())
                    self.param_curve.setVisible(self.param_radio.isChecked())

                    if self.freq_radio.isChecked():
                        self.freq_curve.setData(self.time_data, self.freq_data)
                    elif self.amplitude_radio.isChecked():
                        self.amplitude_curve.setData(self.time_data, self.amplitude_data)
                    elif self.param_radio.isChecked():
                        self.param_curve.setData(self.time_data, self.parameter_data)
                        
        except Exception as e:
            print(f"Error in serial read: {e}")
            self.status_label.setText("Connection Status: Error")
            self.timer.stop()
            self.is_plotting = False


    def save_csv(self):
        file_dialog = QFileDialog(self)
        file_dialog.setDefaultSuffix(".csv")
        file_dialog.setFileMode(QFileDialog.AnyFile)
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        if file_dialog.exec_():
            file_name = file_dialog.selectedFiles()[0]
            data = {"Time (s)": self.time_data}
            if self.freq_radio.isChecked():
                data["Frequency (Hz)"] = self.freq_data
            elif self.amplitude_radio.isChecked():
                data["Amplitude"] = self.amplitude_data
            elif self.param_radio.isChecked():
                data["Parameter"] = self.parameter_data
            df = pd.DataFrame(data)
            df.to_csv(file_name, index=False)
            QMessageBox.information(self, "CSV Saved", f"Data saved to:\n{file_name}")

    def clear_plot(self):
        self.time_data.clear()
        self.freq_data.clear()
        self.amplitude_data.clear()
        self.parameter_data.clear()
        self.current_time = 0
        self.freq_curve.clear()
        self.amplitude_curve.clear()
        self.param_curve.clear()
        self.status_label.setText("Connection Status: Not connected")
        print("Plot cleared.")

        
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Graphical User Interface Module")
        self.setGeometry(100, 100, 1360, 768)

        self.data = None  # To store loaded CSV data

        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()

        # Heading
        heading = QLabel("Design and Development of GUI for Pulsating Sensor based \nControl and Data Acquisition System")
        heading.setObjectName("heading")
        heading.setFont(QFont("Helvetica", 18, QFont.Bold))
        heading.setAlignment(Qt.AlignCenter)

        # Subheading
        subheading = QLabel("EIG/SISD/IGCAR Kalpakkam")
        subheading.setObjectName("subheading")
        subheading.setFont(QFont("Helvetica", 16, QFont.Bold))
        subheading.setAlignment(Qt.AlignCenter)

        # Add heading and subheading
        main_layout.addWidget(heading)
        main_layout.addWidget(subheading)

        # Tab widget
        tab_widget = QTabWidget()
        tab_widget.setObjectName("mainTabWidget")  # For specific styling

        self.online_layer = OnlineLayer()
        self.offline_layer = OfflineLayer()

        tab_widget.addTab(self.online_layer, "Online Analysis")
        tab_widget.addTab(self.offline_layer, "Offline Analysis")

        main_layout.addWidget(tab_widget)
        central_widget.setLayout(main_layout)

        self.set_palette()
        self.set_styles()

    def set_palette(self):
        palette = QPalette()
        palette.setColor(QPalette.WindowText, QColor(200, 162, 200))
        palette.setColor(QPalette.Background, QColor(173, 216, 230))
        self.setPalette(palette)

    def set_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #FFF3E0;
                border: none;
            }

            QLabel {
                font-family: 'Helvetica';
                color: #1A237E;
            }

            QLabel#heading {
                font-size: 28px;
                font-weight: bold;
                color: #000000;
            }

            QLabel#subheading {
                font-size: 18px;
                font-weight: bold;
                color: 	#FF0000;
            }

            QTabWidget {
                border-radius: 12px;
            }

            QTabWidget#mainTabWidget {
                background-color: #FFF8E1;
                border: 2px solid #FF80AB;
                border-radius: 12px;
            }

            QTabWidget#mainTabWidget::pane {
                border: none;
            }

            QTabBar::tab {
                padding: 12px;
                margin: 2px;
                border: 2px solid #FFD54F;
                border-radius: 8px;
                background-color: #FFECB3;
                color: #BF360C;
                font-weight: bold;
            }

            QTabBar::tab:selected {
                background-color: #FFD740;
                border: 2px solid #FF6F00;
                color: #E65100;
            }

            QTabBar::tab:hover {
                background-color: #FFE57F;
                border: 2px solid #FFA000;
            }

            QPushButton {
                font-size: 15px;
                font-family: 'Helvetica';
                padding: 12px 28px;
                border-radius: 8px;
                background-color: #00E5FF;
                color: #004D40;
                font-weight: bold;
                border: none;
            }

            QPushButton:hover {
                background-color: #1DE9B6;
            }

            QPushButton:pressed {
                background-color: #00BFA5;
            }

            QWidget {
                font-size: 14px;
                font-family: 'Helvetica';
            }

            QLineEdit, QTextEdit {
                background-color: #E1F5FE;
                border: 2px solid #81D4FA;
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
                color: #0D47A1;
            }

            QLineEdit:focus, QTextEdit:focus {
                border-color: #2979FF;
                box-shadow: 0 0 10px rgba(41, 121, 255, 0.5);
            }

            QScrollBar:vertical {
                background: #FFF9C4;
                width: 10px;
            }

            QScrollBar::handle:vertical {
                background: #FFCA28;
                border-radius: 5px;
            }

            QScrollBar::handle:vertical:hover {
                background: #FFB300;
            }

            QToolTip {
                background-color: #212121;
                color: #FFEA00;
                border: 1px solid #FF4081;
                padding: 6px;
                font-size: 13px;
                font-family: 'Helvetica';
            }

            /* Frame-specific styling */
            QWidget#onlineFrame {
                background-color: #FFFDE7;
                border: 2px solid #FFCCBC;
                border-radius: 10px;
            }

            QWidget#offlineFrame {
                background-color: #E3F2FD;
                border: 2px solid #90CAF9;
                border-radius: 10px;
            }
        """)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
