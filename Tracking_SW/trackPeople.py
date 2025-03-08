import cv2
from ultralytics import YOLO  # pip install ultralytics

def print_info(x_avg_list, width_lower_bound, width_upper_bound):
    """"
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

def process_video(video_path=0, model="yolov5s.pt", frame_skip_en=False, frame_skip=5, gui=True, debug=False, bound=0.1):
    """
    works for both camera and video input!
    video_path: 0 for camera, or path to video file
    frame_skip_en: if True, processes every xth frame (helps performance)
    frame_skip: the number of frames to skip
    gui: shows video processing
    debug: prints model info (too much info)
    """
    # load YOLO
    model = YOLO(model)

    # start video capture,
    cap, width, height = get_video_dims(video_path)

    # check if video is opened successfully,
    if check_video(cap) == False:
        print(f"Error: Couldn't open {type} file.")
        return
    
    # output processing video,
    out = cv2.VideoWriter('output.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 30, (int(width), int(height)))

    # set bounds for camera movement,
    width_lower_bound, width_upper_bound = bound_set(width, bound)

    frame_count = 0
    while True:
        ret, frame = cap.read()  # get the frame

        if not ret:  # if video ends or fails to grab frame,
            print("Failed to grab frame")
            break

        # process every xth frame to reduce load, enable with [frame_skip_en & frame_skip],
        if frame_skip_en:
            frame_count += 1
            if frame_count % frame_skip != 0:
                continue

        # gather data,
        results = model(frame, verbose=debug)
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
        out.write(frame)
        print_info(x_avg_list, width_lower_bound, width_upper_bound)
            
        # debug gui: enable with [gui]
        if gui:
            cv2.imshow("Video Processing", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):  # exit gui
                break
    
    # release everything,
    out.release()             
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    # start operation:
    # video_path = './Tracking_SW/archive/faceoff.mov'
    video_path = 0
    process_video(video_path, bound=0.25, frame_skip_en=True, frame_skip=5)
