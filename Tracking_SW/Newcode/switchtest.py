import numpy as np
import cv2 as cv
from collections import deque
import cv2
from ultralytics import YOLO  # pip install ultralytics
#from send_data import send_command # to send serial data
def print_info(x_avg_list, width_lower_bound, width_upper_bound):
    """
    Prints:
    - if camera should move left/right
    - people in frame
    - the average x coordinate of the people
    """
    if len(x_avg_list) != 0:
        average_x = round(sum(x_avg_list) / len(x_avg_list),2)
        people_in_frame = len(x_avg_list)
        print(f"People in Frame: {people_in_frame} | x_avg -> {average_x}")
        if (average_x > width_lower_bound):
            print("move right")
        elif (average_x < width_upper_bound):
            print("move left")

def get_video_dims(video_path):
    """
    returns the source object, width, and height of the video
    """
    cap = cv2.VideoCapture(video_path)
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"FPS: {fps}")
    print(f"Source dimensions: {width}x{height}")
    return cap, width, height, fps

def check_video(cap):
    """
    checks if the source opened properly, returns bool
    """
    if not cap.isOpened():
        return False
    print(f"Source opened successfully.")
    return True

def bound_set(width, bound):
    """
    sets the boundaries for camera movement based on the width of the video
    """
    width_lower_bound = width - (bound * width)
    width_upper_bound = 0 + (bound * width)
    print(f"width lower = {width_lower_bound}, width upper = {width_upper_bound} ")
    return width_lower_bound, width_upper_bound

def determine_angle(angle, x_avg_list, width_lower_bound, width_upper_bound, cam_width):
    if len(x_avg_list) != 0:
        average_x = round(sum(x_avg_list) / len(x_avg_list),2)
        zone = (cam_width - width_lower_bound) // 3 # each speed zone
        Rzone0 = width_lower_bound
        Rzone1 = Rzone0 + zone 
        Rzone2 = Rzone1 + zone
        Lzone0 = width_upper_bound
        Lzone1 = Lzone0 - zone 
        Lzone2 = Lzone1 - zone
        if (Rzone1 > average_x > Rzone0):
            print("RZONE0")
            angle = angle - 2
        elif (Rzone2 > average_x > Rzone1):
            print("RZONE1")
            angle = angle - 5
        elif (average_x > Rzone2):
            print("RZONE2")
            angle = angle - 10
        elif (Lzone1 < average_x < Lzone0):
            print("LZONE0")
            angle = angle + 2
        elif (Lzone2 < average_x < Lzone1):
            print("LZONE1")
            angle = angle + 5
        elif (average_x < Lzone2):
            print("LZONE2")
            angle = angle + 10

        # dont over-correct:
        if angle > 180:
            angle = 180
        elif angle < 0:
            angle = 0
        
    return angle

def process_frame(frame, model):
    """
    works for both camera and video input!
    processes a SINGLE frame for unblocking representation
    video_path: 0 for camera, or path to video file
    """
    # gather data,
    results = model(frame, verbose=False)  # change verbose to True if you want model info per process (too much)
    boxes = results[0].boxes    # get the boxes
    labels = boxes.cls          # get labels
    confidences = boxes.conf    # get confidence scores

    # filter out non-person detections + store coordinates,
    x_avg_list = [] # to store average x coordinate
    for i in range(len(boxes)):
        if labels[i] == 0:  # class 0 is person
            x1, y1, x2, y2 = boxes.xyxy[i].cpu().numpy()            # get box coordinates
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 3)  # draw rect.
            cv2.putText(frame, f"Person {i} Conf: {confidences[i]:.2f}", (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2) # add text
            x_avg = round((x1 + x2) / 2, 2)                         # average x-coordinate of each person
            x_avg_list.append(x_avg)
            # print(f"Person {i} is at: {x_avg}")

    # write to output,
    box_render.write(frame)

    return x_avg_list

def process_video(video_path=0, model="yolov5s.pt", frame_skip_en=True, frame_skip=5, gui=True, debug=True, bound=0.1):
    """
    works for both camera and video input!
    video_path: 0 for camera, or path to video file
    frame_skip_en: if True, processes every xth frame (helps performance)
    frame_skip: the number of frames to skip
    gui: shows video processing
    debug: print general info (toggled with debug)
    """
    global LH, LS, LV, UH, US, UV

    # load YOLO
    model = YOLO(model)

    # start video capture,
    cap, width, height, fps = get_video_dims(video_path)

    # check if video is opened successfully,
    if check_video(cap) == False:
        print(f"Error: Couldn't open file.")
        return
    
    # output processing video,
    box_render = cv2.VideoWriter('box_render.mp4', cv2.VideoWriter_fourcc(*'mp4v'), fps//frame_skip, (int(width), int(height)))
    original_film = cv2.VideoWriter('original_film.mp4', cv2.VideoWriter_fourcc(*'mp4v'), fps, (int(width), int(height)))

    # set bounds for camera movement,
    width_lower_bound, width_upper_bound = bound_set(width, bound)

    frame_count = 0
    current_angle = 90 # start at this angle
    while True:
        ret, frame = cap.read()  # get the frame

        if not ret:  # if video ends or fails to grab frame,
            print("Failed to grab frame")
            break

        original_film.write(frame)

        # process every xth frame to reduce load, enable with [frame_skip_en & frame_skip],
        if frame_skip_en:
            frame_count += 1
            if frame_count % frame_skip != 0:
                continue

        # gather data,
        results = model(frame, verbose=False)  # change verbose to True if you want model info per process (too much)
        boxes = results[0].boxes    # get the boxes
        labels = boxes.cls          # get labels
        confidences = boxes.conf    # get confidence scores

        # filter out non-person detections + store coordinates,
        x_avg_list = [] # to store average x coordinate
        for i in range(len(boxes)):
            if labels[i] == 0:  # class 0 is person
                x1, y1, x2, y2 = boxes.xyxy[i].cpu().numpy()            # get box coordinates
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 3)  # draw rect.
                cv2.putText(frame, f"Person {i} Conf: {confidences[i]:.2f}", (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2) # add text
                x_avg = round((x1 + x2) / 2, 2)                         # average x-coordinate of each person
                x_avg_list.append(x_avg)
                # print(f"Person {i} is at: {x_avg}")

        # write to output,
        box_render.write(frame)
        '''
        # calculate new angle
        angle = determine_angle(current_angle, x_avg_list, width_lower_bound, width_upper_bound, width)

        # prevent spam of the same angle,
        if angle != current_angle:
            current_angle = angle
            send_command(angle)
                
            print(f"Angle: {angle}") # for testing

        # debug terminal stuff: enable with [debug]
        if debug:
            print_info(x_avg_list, width_lower_bound, width_upper_bound)
        '''
        # debug gui: enable with [gui]
        if gui:
            cv2.imshow("Video Processing", frame)
            #if cv2.waitKey(1) & 0xFF == ord('q'):  # exit gui
            if cv2.waitKey(1) & frame_count >= 150:
                tracker = trackHSV(0, (LH, LS, LV), (UH, US, UV))
                tracker.run(0)
    
    # release everything,
    box_render.release() 
    original_film.release()             
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    ## for tracking in blocking function:

    # video_path = 0
    # video_path = './archive/faceoff.mov'
    #process_video(video_path, frame_skip_en=True, frame_skip=3, gui=True, debug=False, bound=0.4) # this is blocking!

    # for FSM unblocking,
    ## for process frame: 

    # load path (usually to camera)
    # video_path = 0
    video_path = './Tracking_SW/archive/faceoff.mov'

    # load YOLO
    model = YOLO("yolov5s.pt") # do this before FSM begins

    # start video capture,
    cap, width, height, fps = get_video_dims(video_path) # do this before the FSM begins
    bound = 0.1 # threshold for how sensitive we want to change camera angle
    current_angle = 90 # this will be adjusted and changing 
    debug = True

    # check if video is opened successfully,
    if check_video(cap) == False:
        print(f"Error: Couldn't open file.")
    else:
        # output processing video,
        box_render = cv2.VideoWriter('box_render.mp4', cv2.VideoWriter_fourcc(*'mp4v'), fps, (int(width), int(height))) # with boxes (wont be needed)
        original_film = cv2.VideoWriter('original_film.mp4', cv2.VideoWriter_fourcc(*'mp4v'), fps, (int(width), int(height))) # original video for footage saving

        # set bounds for camera movement,
        width_lower_bound, width_upper_bound = bound_set(width, bound)

        ret, frame = cap.read()  # get the frame

        if not ret:  # if video ends or fails to grab frame,
            print("Failed to grab frame")
        else:

            original_film.write(frame)

            x_avg_list = process_frame(frame, model)

            angle = determine_angle(current_angle, x_avg_list, width_lower_bound, width_upper_bound, width)

            # prevent spam of the same angle,
            if angle != current_angle:
                current_angle = angle
                # send_command(angle)
                    
                print(f"Angle: {angle}") # for testing

            # debug terminal stuff: enable with [debug]
            if debug:
                print_info(x_avg_list, width_lower_bound, width_upper_bound)

            # when done with everything,
            box_render.release() 
            original_film.release()             
            cap.release()
            cv2.destroyAllWindows()

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
        global LH, LS, LV, UH, US, UV
        LH = HSV_lower[0]
        LS = HSV_lower[1]
        LV = HSV_lower[2]
        UH = HSV_upper[0]
        US = HSV_upper[1]
        UV = HSV_upper[2]
        
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

    def run(self, first):
        failCount = 0
        startCount = 0
        switch = 0
        initCheck = 0
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Error: Could not read frame.")
                break
            valid = self.process_frame(frame)
            self.process_frame(frame)
            cv.imshow("Frame", frame)

            if (first):
                if valid and startCount == 0:
                    initCheck += 1
                    print("Init frames remaining: ", (20 - initCheck))
                elif not valid and initCheck < 20:
                    initCheck = 0
                    print("init count reset")
            else:
                initCheck = 21

            if startCount == 0 and initCheck >= 20:
                startCount = 1
                print("Started counting failures.")
            elif valid and startCount == 1:
                failCount = 0
                print("Reset fail count.")
            elif not valid and startCount == 1:
                print("Fail Count: ", failCount)
                failCount += 1
            
            if (failCount >= 30):
                switch = 1
            if (cv2.waitKey(1) and switch):
                process_video(0, frame_skip_en=True, frame_skip=3, gui=True, debug=False, bound=0.4)
            #if cv2.waitKey(1) & 0xFF == ord('q'):  # exit gui
            #    process_video(0, frame_skip_en=True, frame_skip=3, gui=True, debug=False, bound=0.4)
            speed = self.calculate_speed()
        self.cap.release()
        cv.destroyAllWindows()

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

if __name__ == '__main__':
    user_input = input("Please enter something: ")
    if (user_input == "1"):
        tracker = trackHSV(0, (5, 150, 150), (15, 255, 255))
        tracker.run(0)
    elif (user_input == "0"):
        process_video(0, frame_skip_en=True, frame_skip=3, gui=True, debug=False, bound=0.4)