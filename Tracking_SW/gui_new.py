from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout,
                             QWidget, QFileDialog, QLabel, QStackedWidget, QLineEdit)
from PyQt6.QtGui import QFont
from PyQt6.QtGui import QIntValidator
import sys
from trackHSV import trackHSV
import switchtest

#def init(self):
#    """Placeholder for the initialization function. Returns True on success."""
#    layout = QVBoxLayout()
#    
#    textcheck = QLabel("You shouldn't be able to click this.")
#    inputBox = QLineEdit()
#
#    self.completeButton = QPushButton("Initialization Complete")
#    self.completeButton.setFont(QFont("Arial", 14))
#    self.completeButton.setStyleSheet("background-color: #f39c12; color: white; padding: 10px; border-radius: 5px;")
#
#    layout.addWidget(inputBox)
#    layout.addWidget(textcheck)
#    layout.addWidget(self.completeButton)
#    self.setLayout(layout)
#    if (self.completeButton.clicked):
#        return True  # Replace with actual logic

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
        self.status_label = QLabel("Enter Initialization Values")
        self.status_label.setFont(QFont("Arial", 14))
        
        #self.init_button = QPushButton("Run Initialization")
        #self.init_button.setFont(QFont("Arial", 14))
        #self.init_button.setStyleSheet("background-color: #f39c12; color: white; padding: 10px; border-radius: 5px;")
        #self.init_button.clicked.connect(self.run_init)
        
        #self.start_recording_button = QPushButton("Start Recording")
        #self.start_recording_button.setFont(QFont("Arial", 14))
        #self.start_recording_button.setStyleSheet("background-color: #27ae60; color: white; padding: 10px; border-radius: 5px;")
        #self.start_recording_button.setEnabled(False)
        #self.start_recording_button.clicked.connect(lambda: self.switch_window("recording"))

        self.inputBox1 = QLineEdit("Enter Lower Hue Value (0 - 255)")
        self.inputBox1.setValidator(QIntValidator(0, 255))
        self.inputBox2 = QLineEdit("Enter Lower Saturation Value (0 - 255)")
        self.inputBox2.setValidator(QIntValidator(0, 255))
        self.inputBox3 = QLineEdit("Enter Lower Color Value (0 - 255)")
        self.inputBox3.setValidator(QIntValidator(0, 255))
        self.inputBox4 = QLineEdit("Enter Upper Hue Value (0 - 255)")
        self.inputBox4.setValidator(QIntValidator(0, 255))
        self.inputBox5 = QLineEdit("Enter Upper Saturation Value(0 - 255)")
        self.inputBox5.setValidator(QIntValidator(0, 255))
        self.inputBox6 = QLineEdit("Enter Upper Color Value (0 - 255)")
        self.inputBox6.setValidator(QIntValidator(0, 255))

        self.newValsButton = QPushButton("Set New Values")
        self.newValsButton.setFont(QFont("Arial", 14))
        self.newValsButton.setStyleSheet("background-color: #f39c12; color: white; padding: 10px; border-radius: 5px;")
        self.newValsButton.clicked.connect(self.saveNewValues)

        self.autoButton = QPushButton("Use Default Values")
        self.autoButton.setFont(QFont("Arial", 14))
        self.autoButton.setStyleSheet("background-color: #f39c12; color: white; padding: 10px; border-radius: 5px;")
        self.autoButton.clicked.connect(self.setStandard)

        self.completeButton = QPushButton("Complete Initialization")
        self.completeButton.setFont(QFont("Arial", 14))
        self.completeButton.setStyleSheet("background-color: #00d002; color: white; padding: 10px; border-radius: 5px;")
        self.completeButton.setEnabled(False)
        self.completeButton.clicked.connect(lambda: self.switch_window("recording"))

        layout.addWidget(self.status_label)
        layout.addWidget(self.inputBox1)
        layout.addWidget(self.inputBox2)
        layout.addWidget(self.inputBox3)
        layout.addWidget(self.inputBox4)
        layout.addWidget(self.inputBox5)
        layout.addWidget(self.inputBox6)
        layout.addWidget(self.autoButton)
        layout.addWidget(self.newValsButton)
        layout.addWidget(self.completeButton)

        self.setLayout(layout)

    def saveNewValues(self):
        global LH, LS, LV, UH, US, UV

        LH = self.inputBox1.text()
        LS = self.inputBox2.text()
        LV = self.inputBox3.text()
        UH = self.inputBox4.text()
        US = self.inputBox5.text()
        UV = self.inputBox6.text()

        LH = int(LH)
        LS = int(LS)
        LV = int(LV)
        UH = int(UH)
        US = int(US)
        UV = int(UV)

        if (LH > 255) or (LS > 255) or (LV > 255) or (UH > 255) or (US > 255) or (UV > 255): 
            self.switch_window("fail")

        self.completeButton.setEnabled(True)
        self.switch_window("test")

    def setStandard(self):
        global LH, LS, LV, UH, US, UV

        LH = 5
        LS = 150
        LV = 150
        UH = 15
        US = 255
        UV = 255

        self.completeButton.setEnabled(True)
        self.switch_window("test")
        return

class InitFailWindow(StyledWindow):
    def __init__(self, switch_window):
        super().__init__()
        self.switch_window = switch_window
        self.setWindowTitle("Initialization Error")

        layout = QVBoxLayout()
        self.status_label = QLabel("Enter Initialization Values")
        self.status_label.setFont(QFont("Arial", 14))

        self.error_label = QLabel("Error! Improper Value!")
        self.error_label.setFont(QFont("Arial", 14))

        self.inputBox1 = QLineEdit("Enter Lower Hue Value (0 - 255)")
        self.inputBox1.setValidator(QIntValidator(0, 255))
        self.inputBox2 = QLineEdit("Enter Lower Saturation Value (0 - 255)")
        self.inputBox2.setValidator(QIntValidator(0, 255))
        self.inputBox3 = QLineEdit("Enter Lower Color Value (0 - 255)")
        self.inputBox3.setValidator(QIntValidator(0, 255))
        self.inputBox4 = QLineEdit("Enter Upper Hue Value (0 - 255)")
        self.inputBox4.setValidator(QIntValidator(0, 255))
        self.inputBox5 = QLineEdit("Enter Upper Saturation Value(0 - 255)")
        self.inputBox5.setValidator(QIntValidator(0, 255))
        self.inputBox6 = QLineEdit("Enter Upper Color Value (0 - 255)")
        self.inputBox6.setValidator(QIntValidator(0, 255))

        self.newValsButton = QPushButton("Set New Values")
        self.newValsButton.setFont(QFont("Arial", 14))
        self.newValsButton.setStyleSheet("background-color: #f39c12; color: white; padding: 10px; border-radius: 5px;")
        self.newValsButton.clicked.connect(self.saveNewValues2)

        self.autoButton = QPushButton("Use Default Values")
        self.autoButton.setFont(QFont("Arial", 14))
        self.autoButton.setStyleSheet("background-color: #f39c12; color: white; padding: 10px; border-radius: 5px;")
        self.autoButton.clicked.connect(self.setStandard2)

        self.completeButton = QPushButton("Complete Initialization")
        self.completeButton.setFont(QFont("Arial", 14))
        self.completeButton.setStyleSheet("background-color: #00d002; color: white; padding: 10px; border-radius: 5px;")
        self.completeButton.setEnabled(False)
        self.completeButton.clicked.connect(lambda: self.switch_window("recording"))
        
        layout.addWidget(self.status_label)
        layout.addWidget(self.error_label)
        layout.addWidget(self.inputBox1)
        layout.addWidget(self.inputBox2)
        layout.addWidget(self.inputBox3)
        layout.addWidget(self.inputBox4)
        layout.addWidget(self.inputBox5)
        layout.addWidget(self.inputBox6)
        layout.addWidget(self.autoButton)
        layout.addWidget(self.newValsButton)
        layout.addWidget(self.completeButton)

        self.setLayout(layout)

    def saveNewValues2(self):
        global LH, LS, LV, UH, US, UV

        LH = self.inputBox1.text()
        LS = self.inputBox2.text()
        LV = self.inputBox3.text()
        UH = self.inputBox4.text()
        US = self.inputBox5.text()
        UV = self.inputBox6.text()

        LH = int(LH)
        LS = int(LS)
        LV = int(LV)
        UH = int(UH)
        US = int(US)
        UV = int(UV)

        if (LH > 255) or (LS > 255) or (LV > 255) or (UH > 255) or (US > 255) or (UV > 255): 
            self.switch_window("fail")

        self.completeButton.setEnabled(True)
        self.switch_window("test")

    def setStandard2(self):
        global LH, LS, LV, UH, US, UV
    
        LH = 5
        LS = 150
        LV = 150
        UH = 15
        US = 255
        UV = 255
        
        self.completeButton.setEnabled(True)
        self.switch_window("test")
        return

class VerifyInitWindow(StyledWindow):
    def __init__(self, switch_window):
        super().__init__()
        self.switch_window = switch_window
        self.setWindowTitle("Verifying Initialization")

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

        global LH, LS, LV, UH, US, UV

        self.tracker = trackHSV(0, (LH, LS, LV), (UH, US, UV))       #change to track_FSM?
        self.tracker.run()

    def stop_tracking(self):
        self.tracker.stop()
        self.switch_window("save")

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

        global LH, LS, LV, UH, US, UV
        trackHSV.end = True
        tracker = switchtest.trackHSV(0, (LH, LS, LV), (UH, US, UV))
        tracker.run(1)

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
            self.setCentralWidget(StartWindow(self.switch_window))                  #start window
        elif window_name == "init":
            self.setCentralWidget(InitWindow(self.switch_window))                   #init window
        elif window_name == "recording":
            self.setCentralWidget(RecordingWindow(self.switch_window))              #recording window
        elif window_name == "save":
            self.setCentralWidget(SaveWindow(self.switch_window))                   #save window
        elif window_name == "save_reinit":
            self.setCentralWidget(SaveWindow(self.switch_window, reinit=True))      #???
        elif window_name == "fail":
            self.setCentralWidget(InitFailWindow(self.switch_window))               #init failed window
        elif window_name == "test":
            self.setCentralWidget(VerifyInitWindow(self.switch_window))             #run the tracking to just verify the init

app = QApplication(sys.argv)
main_window = MainApp()
main_window.show()
app.exec()