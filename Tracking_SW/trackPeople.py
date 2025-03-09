import cv2
from ultralytics import YOLO  # pip install ultralytics
from send_data import send_command # to send serial data

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
    print(f"Source dimensions: {width}x{height}")
    return cap, width, height

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

def process_video(video_path=0, model="yolov5s.pt", frame_skip_en=True, frame_skip=5, gui=True, debug=True, bound=0.1):
    """
    works for both camera and video input!
    video_path: 0 for camera, or path to video file
    frame_skip_en: if True, processes every xth frame (helps performance)
    frame_skip: the number of frames to skip
    gui: shows video processing
    debug: print general info (toggled with debug)
    """
    # load YOLO
    model = YOLO(model)

    # start video capture,
    cap, width, height = get_video_dims(video_path)

    # check if video is opened successfully,
    if check_video(cap) == False:
        print(f"Error: Couldn't open file.")
        return
    
    # output processing video,
    box_render = cv2.VideoWriter('box_render.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 10, (int(width), int(height)))
    original_film = cv2.VideoWriter('original_film.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 20, (int(width), int(height)))

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

        # calculate new angle
        angle = determine_angle(current_angle, x_avg_list, width_lower_bound, width_upper_bound, width)

        # prevent spam of the same angle,
        if angle != current_angle:
            current_angle = angle
            # send command:
            # send_command(angle)
            print(f"Angle: {angle}") # for testing

        # debug terminal stuff: enable with [debug]
        if debug:
            print_info(x_avg_list, width_lower_bound, width_upper_bound)
            
        # debug gui: enable with [gui]
        if gui:
            cv2.imshow("Video Processing", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):  # exit gui
                break
    
    # release everything,
    box_render.release() 
    original_film.release()             
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    # start operation:
    # video_path = './Tracking_SW/archive/faceoff.mov'
    video_path = 0
    # video_path = './archive/faceoff.mov'
    process_video(video_path, frame_skip_en=True, frame_skip=3, gui=True, debug=False, bound=0.4)
