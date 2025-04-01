from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout,
                             QWidget, QFileDialog, QLabel, QStackedWidget)
from PyQt6.QtGui import QFont
import sys
from trackHSV import trackHSV

def init():
    """Placeholder for the initialization function. Returns True on success."""
    return True  # Replace with actual logic

class StyledWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #2c3e50; color: white; font-family: Arial;")

class StartWindow(StyledWindow):
    def __init__(self, switch_window):
        super().__init__()
        self.switch_window = switch_window
        self.setWindowTitle("Start Up")

        layout = QVBoxLayout()
        self.begin_button = QPushButton("Begin")
        self.begin_button.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.begin_button.setStyleSheet("background-color: #3498db; color: white; padding: 10px; border-radius: 5px;")
        self.begin_button.clicked.connect(lambda: self.switch_window("init"))

        layout.addWidget(self.begin_button)
        self.setLayout(layout)

class InitWindow(StyledWindow):
    def __init__(self, switch_window):
        super().__init__()
        self.switch_window = switch_window
        self.setWindowTitle("Initialization")

        layout = QVBoxLayout()
        self.status_label = QLabel("Click to initialize")
        self.status_label.setFont(QFont("Arial", 14))
        
        self.init_button = QPushButton("Run Initialization")
        self.init_button.setFont(QFont("Arial", 14))
        self.init_button.setStyleSheet("background-color: #f39c12; color: white; padding: 10px; border-radius: 5px;")
        self.init_button.clicked.connect(self.run_init)
        
        self.start_recording_button = QPushButton("Start Recording")
        self.start_recording_button.setFont(QFont("Arial", 14))
        self.start_recording_button.setStyleSheet("background-color: #27ae60; color: white; padding: 10px; border-radius: 5px;")
        self.start_recording_button.setEnabled(False)
        self.start_recording_button.clicked.connect(lambda: self.switch_window("recording"))
        
        layout.addWidget(self.status_label)
        layout.addWidget(self.init_button)
        layout.addWidget(self.start_recording_button)
        self.setLayout(layout)

    def run_init(self):
        if init():
            self.status_label.setText("Initialization successful!")
            self.start_recording_button.setEnabled(True)
        else:
            self.status_label.setText("Initialization failed. Try again.")

class RecordingWindow(StyledWindow):
    def __init__(self, switch_window):
        super().__init__()
        self.switch_window = switch_window
        self.setWindowTitle("Recording in Progress")

        layout = QVBoxLayout()
        self.stop_button = QPushButton("Stop Recording")
        self.stop_button.setFont(QFont("Arial", 14))
        self.stop_button.setStyleSheet("background-color: #e74c3c; color: white; padding: 10px; border-radius: 5px;")
        self.stop_button.clicked.connect(self.stop_tracking)
        
        self.reinit_button = QPushButton("Reinitialize")
        self.reinit_button.setFont(QFont("Arial", 14))
        self.reinit_button.setStyleSheet("background-color: #9b59b6; color: white; padding: 10px; border-radius: 5px;")
        self.reinit_button.clicked.connect(lambda: self.switch_window("save_reinit"))
        
        layout.addWidget(self.stop_button)
        layout.addWidget(self.reinit_button)
        self.setLayout(layout)

        self.tracker = trackHSV("archive/faceoff.mov", (5, 150, 150), (15, 255, 255))
        self.tracker.run()
    
    def stop_tracking(self):
        self.tracker.stop()
        self.switch_window("save")

class SaveWindow(StyledWindow):
    def __init__(self, switch_window, reinit=False):
        super().__init__()
        self.switch_window = switch_window
        self.reinit = reinit
        self.setWindowTitle("Save Video")

        layout = QVBoxLayout()
        self.label = QLabel("Choose location to save video")
        self.label.setFont(QFont("Arial", 14))
        
        self.save_button = QPushButton("Save")
        self.save_button.setFont(QFont("Arial", 14))
        self.save_button.setStyleSheet("background-color: #16a085; color: white; padding: 10px; border-radius: 5px;")
        self.save_button.clicked.connect(self.save_video)

        self.done_button = QPushButton("Done")
        self.done_button.setFont(QFont("Arial", 14))
        self.done_button.setStyleSheet("background-color: #2ecc71; color: white; padding: 10px; border-radius: 5px;")
        self.done_button.setEnabled(False)
        self.done_button.clicked.connect(self.finish)
        
        layout.addWidget(self.label)
        layout.addWidget(self.save_button)
        layout.addWidget(self.done_button)
        self.setLayout(layout)
    
    def save_video(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Video", "", "Video Files (*.mp4 *.avi)")
        if file_path:
            self.label.setText("Video saved successfully!")
            self.done_button.setEnabled(True)
    
    def finish(self):
        if self.reinit:
            self.switch_window("init")
        else:
            self.switch_window("start")

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tracking Software")
        self.setStyleSheet("background-color: #34495e;")
        self.switch_window("start")

    def switch_window(self, window_name):
        if window_name == "start":
            self.setCentralWidget(StartWindow(self.switch_window))
        elif window_name == "init":
            self.setCentralWidget(InitWindow(self.switch_window))
        elif window_name == "recording":
            self.setCentralWidget(RecordingWindow(self.switch_window))
        elif window_name == "save":
            self.setCentralWidget(SaveWindow(self.switch_window))
        elif window_name == "save_reinit":
            self.setCentralWidget(SaveWindow(self.switch_window, reinit=True))

app = QApplication(sys.argv)
main_window = MainApp()
main_window.show()
app.exec()
