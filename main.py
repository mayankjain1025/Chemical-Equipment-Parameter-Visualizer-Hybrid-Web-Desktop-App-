"""
Chemical Equipment Parameter Visualizer - PyQt5 Desktop Application

A desktop application that connects to the Django API to upload CSV files
and visualize equipment data using Matplotlib.

Requirements:
    pip install PyQt5 matplotlib requests
"""

import sys
import requests
import requests

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QMessageBox, QGroupBox,
    QLineEdit, QFrame, QSizePolicy, QDialog, QFormLayout, QDialogButtonBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


# API Configuration
API_BASE_URL = "http://127.0.0.1:8000/api"


class AuthDialog(QDialog):
    """Dialog for entering Basic Auth credentials."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("API Authentication")
        self.setFixedWidth(350)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("🔐 Enter API Credentials")
        title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        self.username_input.setMinimumHeight(35)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(35)
        
        form_layout.addRow("Username:", self.username_input)
        form_layout.addRow("Password:", self.password_input)
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.handle_login)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def handle_login(self):
        token = self.authenticate()
        if token:
            self.token = token
            self.accept()
    
    def get_credentials(self):
        return self.username_input.text(), self.password_input.text()
        
    def authenticate(self):
        """Try to authenticate and get token."""
        username = self.username_input.text()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter username and password")
            return None
            
        try:
            response = requests.post(f"{API_BASE_URL}/login/", json={
                'username': username,
                'password': password
            })
            
            if response.status_code == 200:
                return response.json().get('token')
            elif response.status_code == 400:
                QMessageBox.warning(self, "Login Failed", "Invalid credentials")
            else:
                QMessageBox.warning(self, "Login Failed", f"Error: {response.text}")
        except Exception as e:
            QMessageBox.critical(self, "Connection Error", f"Could not connect to server: {e}")
            
        return None


class UploadWorker(QThread):
    """Worker thread for uploading CSV files to the API."""
    
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, file_path, token):
        super().__init__()
        self.file_path = file_path
        self.token = token
    
    def run(self):
        try:
            with open(self.file_path, 'rb') as f:
                files = {'file': (self.file_path.split('/')[-1].split('\\')[-1], f, 'text/csv')}
                response = requests.post(
                    f"{API_BASE_URL}/upload/",
                    files=files,
                    headers={'Authorization': f'Token {self.token}'},
                    timeout=30
                )
            
            if response.status_code == 201:
                self.finished.emit(response.json())
            elif response.status_code == 401:
                self.error.emit("Authentication failed. Please check your credentials.")
            else:
                error_msg = response.json().get('error', 'Unknown error occurred')
                if isinstance(error_msg, dict):
                    error_msg = str(error_msg)
                self.error.emit(f"API Error: {error_msg}")
                
        except requests.exceptions.ConnectionError:
            self.error.emit("Connection failed. Is the Django server running?")
        except requests.exceptions.Timeout:
            self.error.emit("Request timed out. Please try again.")
        except Exception as e:
            self.error.emit(f"Error: {str(e)}")


class MatplotlibCanvas(FigureCanvas):
    """Matplotlib canvas widget for embedding charts in PyQt5."""
    
    def __init__(self, parent=None, width=6, height=4, dpi=100):
        # Create figure with dark theme
        plt.style.use('dark_background')
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor='#1a2332')
        self.axes = self.fig.add_subplot(111)
        self.axes.set_facecolor('#1a2332')
        
        super().__init__(self.fig)
        self.setParent(parent)
        
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.updateGeometry()
    
    def plot_type_distribution(self, distribution):
        """Plot equipment type distribution as a bar chart."""
        self.axes.clear()
        
        if not distribution:
            self.axes.text(0.5, 0.5, 'No data to display', 
                          ha='center', va='center', fontsize=14, color='#888888')
            self.draw()
            return
        
        types = [item['type'] for item in distribution]
        counts = [item['count'] for item in distribution]
        
        # Color palette
        colors = ['#63b3ed', '#68d391', '#ed8936', '#9f7aea', '#f56565', '#48bb78', '#f6ad55']
        bar_colors = [colors[i % len(colors)] for i in range(len(types))]
        
        # Create bar chart
        bars = self.axes.bar(types, counts, color=bar_colors, edgecolor='white', linewidth=0.5)
        
        # Styling
        self.axes.set_xlabel('Equipment Type', fontsize=10, color='#a0aec0', labelpad=10)
        self.axes.set_ylabel('Count', fontsize=10, color='#a0aec0', labelpad=10)
        self.axes.set_title('Equipment Type Distribution', fontsize=12, color='white', fontweight='bold', pad=15)
        
        # Rotate x-axis labels for better readability
        self.axes.set_xticklabels(types, rotation=30, ha='right', fontsize=9, color='#a0aec0')
        self.axes.tick_params(axis='y', colors='#a0aec0')
        
        # Add value labels on bars
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            self.axes.annotate(f'{count}',
                              xy=(bar.get_x() + bar.get_width() / 2, height),
                              xytext=(0, 3),
                              textcoords="offset points",
                              ha='center', va='bottom',
                              fontsize=10, fontweight='bold', color='white')
        
        # Grid
        self.axes.yaxis.grid(True, linestyle='--', alpha=0.3)
        self.axes.set_axisbelow(True)
        
        # Adjust layout
        self.fig.tight_layout()
        self.draw()
    
    def clear_plot(self):
        """Clear the plot."""
        self.axes.clear()
        self.axes.text(0.5, 0.5, 'Upload a CSV file to view chart', 
                      ha='center', va='center', fontsize=12, color='#666666')
        self.draw()


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        super().__init__()
        self.token = None
        self.worker = None
        
        self.setup_ui()
        self.apply_dark_theme()
        self.show_auth_dialog()
    
    def setup_ui(self):
        """Setup the main user interface."""
        self.setWindowTitle("⚗️ Chemical Equipment Visualizer")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Content area
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        
        # Left panel - Controls and Statistics
        left_panel = self.create_left_panel()
        content_layout.addWidget(left_panel, stretch=1)
        
        # Right panel - Chart
        right_panel = self.create_right_panel()
        content_layout.addWidget(right_panel, stretch=2)
        
        main_layout.addLayout(content_layout)
        
        # Status bar
        self.statusBar().showMessage("Ready - Please upload a CSV file")
        self.statusBar().setStyleSheet("color: #a0aec0;")
    
    def create_header(self):
        """Create the header section."""
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1e3a5f, stop:1 #0d2137);
                border-radius: 12px;
                padding: 15px;
            }
        """)
        
        layout = QHBoxLayout(header)
        
        title = QLabel("⚗️ Chemical Equipment Parameter Visualizer")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color: white;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        subtitle = QLabel("Desktop Client • Connected to Django API")
        subtitle.setStyleSheet("color: #a0aec0; font-size: 11px;")
        layout.addWidget(subtitle)
        
        return header
    
    def create_left_panel(self):
        """Create the left panel with controls and statistics."""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background: #1a2332;
                border-radius: 12px;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Upload section
        upload_group = QGroupBox("📤 Upload CSV")
        upload_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                color: white;
                border: 1px solid #2d3748;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        upload_layout = QVBoxLayout(upload_group)
        
        self.upload_btn = QPushButton("📁 Select & Upload CSV File")
        self.upload_btn.setMinimumHeight(50)
        self.upload_btn.setCursor(Qt.PointingHandCursor)
        self.upload_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4299e1, stop:1 #3182ce);
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #63b3ed, stop:1 #4299e1);
            }
            QPushButton:pressed {
                background: #2b6cb0;
            }
            QPushButton:disabled {
                background: #4a5568;
                color: #718096;
            }
        """)
        self.upload_btn.clicked.connect(self.upload_file)
        upload_layout.addWidget(self.upload_btn)
        
        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet("color: #718096; font-size: 11px;")
        self.file_label.setWordWrap(True)
        upload_layout.addWidget(self.file_label)
        
        layout.addWidget(upload_group)
        
        # Statistics section
        stats_group = QGroupBox("📈 Summary Statistics")
        stats_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                color: white;
                border: 1px solid #2d3748;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        stats_layout = QVBoxLayout(stats_group)
        stats_layout.setSpacing(15)
        
        # Statistics labels
        self.total_label = self.create_stat_label("Total Equipment", "—", "🔧")
        self.flowrate_label = self.create_stat_label("Avg. Flowrate", "—", "💧")
        self.pressure_label = self.create_stat_label("Avg. Pressure", "—", "📊")
        self.temperature_label = self.create_stat_label("Avg. Temperature", "—", "🌡️")
        
        stats_layout.addWidget(self.total_label)
        stats_layout.addWidget(self.flowrate_label)
        stats_layout.addWidget(self.pressure_label)
        stats_layout.addWidget(self.temperature_label)
        
        layout.addWidget(stats_group)
        
        # Spacer
        layout.addStretch()
        
        # Auth button
        auth_btn = QPushButton("🔑 Change Credentials")
        auth_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #a0aec0;
                border: 1px solid #4a5568;
                border-radius: 6px;
                padding: 8px;
                font-size: 11px;
            }
            QPushButton:hover {
                background: #2d3748;
                color: white;
            }
        """)
        auth_btn.clicked.connect(self.show_auth_dialog)
        layout.addWidget(auth_btn)
        
        return panel
    
    def create_stat_label(self, title, value, icon):
        """Create a styled statistics label."""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: #0d1a26;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(12, 12, 12, 12)
        
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI", 18))
        layout.addWidget(icon_label)
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #a0aec0; font-size: 11px;")
        text_layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setObjectName(f"{title.lower().replace(' ', '_').replace('.', '')}_value")
        value_label.setStyleSheet("color: #63b3ed; font-size: 18px; font-weight: bold;")
        text_layout.addWidget(value_label)
        
        layout.addLayout(text_layout)
        layout.addStretch()
        
        # Store reference to value label for updates
        frame.value_label = value_label
        
        return frame
    
    def create_right_panel(self):
        """Create the right panel with the chart."""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background: #1a2332;
                border-radius: 12px;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Chart title
        title = QLabel("📊 Equipment Type Distribution")
        title.setFont(QFont("Segoe UI", 13, QFont.Bold))
        title.setStyleSheet("color: white;")
        layout.addWidget(title)
        
        # Matplotlib canvas
        self.canvas = MatplotlibCanvas(self, width=8, height=5, dpi=100)
        self.canvas.clear_plot()
        layout.addWidget(self.canvas)
        
        return panel
    
    def apply_dark_theme(self):
        """Apply dark theme to the application."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0d1a26;
            }
            QMessageBox {
                background-color: #1a2332;
                color: white;
            }
            QMessageBox QLabel {
                color: white;
            }
            QMessageBox QPushButton {
                background: #4299e1;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
            }
        """)
    
    def show_auth_dialog(self):
        """Show the authentication dialog."""
        dialog = AuthDialog(self)
        
        if dialog.exec_() == QDialog.Accepted:
            self.token = dialog.token
            if self.token:
                self.statusBar().showMessage(f"Authenticated successfully")
            else:
                QMessageBox.warning(self, "Warning", "Credentials are required to upload files.")
    
    def upload_file(self):
        """Open file dialog and upload selected CSV file."""
        if not self.token:
            self.show_auth_dialog()
            if not self.token:
                return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select CSV File",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if not file_path:
            return
        
        # Update UI
        filename = file_path.split('/')[-1].split('\\')[-1]
        self.file_label.setText(f"Selected: {filename}")
        self.file_label.setStyleSheet("color: #68d391; font-size: 11px;")
        self.upload_btn.setEnabled(False)
        self.upload_btn.setText("⏳ Uploading...")
        self.statusBar().showMessage("Uploading file to API...")
        
        # Start upload worker
        self.worker = UploadWorker(file_path, self.token)
        self.worker.finished.connect(self.on_upload_success)
        self.worker.error.connect(self.on_upload_error)
        self.worker.start()
    
    def on_upload_success(self, data):
        """Handle successful API response."""
        self.upload_btn.setEnabled(True)
        self.upload_btn.setText("📁 Select & Upload CSV File")
        
        # Update statistics
        stats = data.get('summary_statistics', {})
        
        self.total_label.value_label.setText(str(stats.get('total_count', 0)))
        self.flowrate_label.value_label.setText(f"{stats.get('avg_flowrate', 0):.2f} m³/h")
        self.pressure_label.value_label.setText(f"{stats.get('avg_pressure', 0):.2f} bar")
        self.temperature_label.value_label.setText(f"{stats.get('avg_temperature', 0):.2f} °C")
        
        # Update chart
        type_distribution = stats.get('type_distribution', [])
        self.canvas.plot_type_distribution(type_distribution)
        
        # Update status
        self.statusBar().showMessage(
            f"✅ Success! Loaded {stats.get('total_count', 0)} equipment records. "
            f"File ID: {data.get('file_id', 'N/A')}"
        )
        
        self.file_label.setStyleSheet("color: #68d391; font-size: 11px;")
    
    def on_upload_error(self, error_msg):
        """Handle upload error."""
        self.upload_btn.setEnabled(True)
        self.upload_btn.setText("📁 Select & Upload CSV File")
        self.file_label.setStyleSheet("color: #fc8181; font-size: 11px;")
        self.statusBar().showMessage(f"❌ Error: {error_msg}")
        
        QMessageBox.critical(self, "Upload Error", error_msg)


def main():
    """Main entry point."""
    # Enable high DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set application font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
