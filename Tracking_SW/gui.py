from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton
import sys
from trackHSV import trackHSV

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tracking Software")
        button = QPushButton("Start")
        button.setCheckable(True)
        button.clicked.connect(self.start)
        self.setCentralWidget(button)
    def start(self, checked):
        tracker = trackHSV("archive/faceoff.mov", (5, 150, 150), (15, 255, 255))
        tracker.run()


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()