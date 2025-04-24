import numpy as np
import cv2 as cv
from collections import deque
from send_data import send_command # to send serial data
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
        self.x_avg_list = np.zeros(10) # list of x positions of ball
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
                        print("move right - HSV")
                    self.direction[0] = 0
                    self.direction[1] = cx > self.width_lower_bound # right
                elif (cx < self.width_upper_bound):
                    if (not self.direction[0]):
                        print("move left - HSV")
                    self.direction[0] = cx < self.width_upper_bound # right
                    self.direction[1] = 0
            return True
        return False

    def run(self):
        angle = 90  # start at center
        frame_count = 0
        while True:
            ret, frame = self.cap.read()
            frame_count += 1
            if not ret:
                print("Error: Could not read frame.")
                break

            found = self.process_frame(frame)
            if found:
                new_angle = self.determine_angle(angle)
                if new_angle != angle and frame_count % 5 == 0:  # send command every 5 frames
                    angle = new_angle
                    # print(f"Sending angle: {angle}")
                    send_command(angle)


            cv.imshow("Frame", frame)
            if cv.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv.destroyAllWindows()
        return True


    def calculate_speed(self):
        if len(self.position_history) < 2:
            return 0
        speeds = []
        for i in range(1, len(self.position_history)):
            x1, y1 = self.position_history[i - 1]
            x2, y2 = self.position_history[i]
            distancex = np.abs(x2 - x1)
            distancey = np.abs(y2 - y1)
            distance2d = np.sqrt(distancex ** 2 + distancey ** 2) # not sure if need bc we are only traveling in x direction
            speeds.append(distancex)

        #print(speeds)
        return np.mean(speeds) if speeds else 0.0
    


    def find_average_x_pos(self):
        if not self.position_history:
            return None
        x_vals = [x for x, _ in self.position_history]
        return sum(x_vals) / len(x_vals)

    

    def determine_angle(self, current_angle):
        average_x = self.find_average_x_pos()
        if average_x is None:
            return current_angle
        
        zone = (self.width - self.width_lower_bound) // 3
        Rzone0 = self.width_lower_bound
        Rzone1 = Rzone0 + zone 
        Rzone2 = Rzone1 + zone
        Lzone0 = self.width_upper_bound
        Lzone1 = Lzone0 - zone 
        Lzone2 = Lzone1 - zone

        if Rzone0 < average_x < Rzone1:
            # print("RZONE0")
            current_angle -= 2
        elif Rzone1 < average_x < Rzone2:
            # print("RZONE1")
            current_angle -= 5
        elif average_x > Rzone2:
            # print("RZONE2")
            current_angle -= 10
        elif Lzone1 < average_x < Lzone0:
            # print("LZONE0")
            current_angle += 2
        elif Lzone2 < average_x < Lzone1:
            # print("LZONE1")
            current_angle += 5
        elif average_x < Lzone2:
            # print("LZONE2")
            current_angle += 10

        return max(0, min(180, current_angle))

track = trackHSV(0, (5, 150, 150), (15, 255, 255))
track.run()