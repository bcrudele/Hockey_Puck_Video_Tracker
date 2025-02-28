import numpy as np
import cv2 as cv
from collections import deque
class trackHSV():
    def __init__(self, camera_idx, HSV_lower, HSV_upper):
        self.cap = cv.VideoCapture(camera_idx)
        self.width = self.cap.get(cv.CAP_PROP_FRAME_WIDTH)
        self.height = self.cap.get(cv.CAP_PROP_FRAME_HEIGHT)
        self.bound = 0.10
        self.width_lower_bound = self.width - (self.bound * self.width)
        self.width_upper_bound = 0 + (self.bound * self.width)
        self.height_lower_bound = self.height - (self.bound * self.height)
        self.height_upper_bound = self.height + (self.bound * self.height)
        self.orangeLower = HSV_lower # (5, 150, 150)
        self.orangeUpper = HSV_upper # (15, 255, 255)

        self.history_size = 10
        self.position_history = deque(maxlen = self.history_size)

        self.direction = [0,0]
        print("Camera dimensions:", (self.width, self.height))
        print(f"width lower = {self.width_lower_bound}, width upper = {self.width_upper_bound} ")
        print(f"height lower = {self.height_lower_bound}, height upper = {self.height_upper_bound}")
    
    def process_frame(self, frame):
        hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        hsv[..., 2] = cv.createCLAHE(clipLimit=5).apply(hsv[..., 2]) 
        # Create mask for orange color
        mask = cv.inRange(hsv, np.array(self.orangeLower), np.array(self.orangeUpper))
        
        # Find contours of the masked image
        contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        
        # Track the largest contour (assuming it's the main orange blob)
        if contours:
            largest_contour = max(contours, key=cv.contourArea)
            M = cv.moments(largest_contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                point = (cx, cy)
                self.position_history.append(point)
                if (len(self.position_history) > 10):
                    self.position_history.popleft()
                cv.circle(frame, (cx, cy), 5, (0, 255, 0), -1)
                cv.putText(frame, f"({cx}, {cy})", (cx + 10, cy - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2) 
                if (cx > self.width_lower_bound):
                    if (not self.direction[1]):
                        print("move right")
                    self.direction[0] = 0
                    self.direction[1] = cx > self.width_lower_bound # right
                elif (cx < self.width_upper_bound):
                    if (not self.direction[0]):
                        print("move left")
                    self.direction[0] = cx < self.width_upper_bound # right
                    self.direction[1] = 0

    def run(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Error: Could not read frame.")
                break
            self.process_frame(frame)
            cv.imshow("Frame", frame)
            if cv.waitKey(1) & 0xFF == ord('q'):
                break
        self.cap.release()
        cv.destroyAllWindows()

    def calculate_speed(self):
        if len(self.position_history) < 2:
            return 0
        speeds = []
        for i in range(1, len(self.position_history)):
            x1, y1 = self.position_history[i - 1]
            x2, y2 = self.position_history[i]
            distance = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            speeds.append(distance)
            
        print(speeds)
        return np.mean(speeds) if speeds else 0.0
    
        

