import cv2
from ultralytics import YOLO  # pip install ultralytics

def print_info(x_avg_list, width_lower_bound, width_upper_bound):
        if len(x_avg_list) != 0:
            average_x = round(sum(x_avg_list) / len(x_avg_list),2)
            people_in_frame = len(x_avg_list)
            print(f"People in Frame: {people_in_frame} | x_avg -> {average_x}")
            if (average_x > width_lower_bound):
                print("move right")
            elif (average_x < width_upper_bound):
                print("move left")

def process_video(video_path, model="yolov5s.pt", debuff_en=False, debuff_range=1, gui=True, debug=False, bound=0.1):
    
    # load YOLO
    model = YOLO(model)

    # start video capture
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Couldn't open video file.")
        return

    # video dims:
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    print(f"Video dimensions: {width}x{height}")
    width_lower_bound = width - (bound * width)
    width_upper_bound = 0 + (bound * width)
    print(f"width lower = {width_lower_bound}, width upper = {width_upper_bound} ")

    frame_count = 0
    while True:
        ret, frame = cap.read()  # get the frame

        if not ret:  # if video ends or fails to grab frame
            print("Failed to grab frame")
            break

        # process every xth frame to reduce load
        if debuff_en:
            frame_count += 1
            if frame_count % debuff_range != 0:
                continue

        # gather data,
        results = model(frame, verbose=debug)
        boxes = results[0].boxes  # get the boxes
        labels = boxes.cls  # get labels
        confidences = boxes.conf  # get confidence scores

        # filter out non-person detections + store coordinates,
        x_avg_list = [] # to store average x coordinate
        for i in range(len(boxes)):
            if labels[i] == 0:  # class 0 is person
                x1, y1, x2, y2 = boxes.xyxy[i].cpu().numpy()  # get box coordinates
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 3)  # draw rect.
                cv2.putText(frame, f"Person {i} Conf: {confidences[i]:.2f}", (int(x1), int(y1)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2) # add text
                x_avg = round((x1 + x2) / 2, 2)  # average x-coordinate of each person
                x_avg_list.append(x_avg)
                # print(f"Person {i} is at: {x_avg}")

        print_info(x_avg_list, width_lower_bound, width_upper_bound)
            
        # debug gui: enable with [gui]
        if gui:
            cv2.imshow("Video Processing", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):  # exit gui
                break

    cap.release()
    cv2.destroyAllWindows()

def process_camera(camera=0, model="yolov5s.pt", debuff_en=False, debuff_range=1, gui=True, debug=False, bound=0.1):

    model = YOLO(model)  # yolov5s is a smaller model than detr

    # initialize camera:
    cap = cv2.VideoCapture(camera)  # might have to change camera '#' later
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    width_lower_bound = width - (bound * width)
    width_upper_bound = 0 + (bound * width)
    print("Camera dimensions:", (width, height)) 
    print(f"width lower = {width_lower_bound}, width upper = {width_upper_bound} ")

    # variables:
    frame_count = 0

    # start reading frames,
    while True:

        ret, frame = cap.read() # get each frame,

        if not ret: # if camera gets disconnected/failure,
            print("Failed to grab frame")
            break

        # process every xth frame to reduce load, [debuff_en]
        if debuff_en:
            frame_count += 1
            if frame_count % debuff_range != 0:
                continue

        # use YOLO model:
        results = model(frame, verbose=debug) # turn on verbose with [debug]
        boxes = results[0].boxes    # get results,
        labels = boxes.cls          # labels found
        confidences = boxes.conf    # confidence numbers

        # filter out other objects detected, class 0 -> people in COCO
        x_avg_list = [] # to store average x coordinate
        for i in range(len(boxes)):
            if labels[i] == 0:  # if a person,
                x1, y1, x2, y2 = boxes.xyxy[i].cpu().numpy()  # unpack the coordinates
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 3) # draw the rect.
                cv2.putText(frame, f"Person {i} Conf: {confidences[i]:.2f}", (int(x1), int(y1)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2) # add text
                x_avg = round((x1 + x2) / 2, 2)  # average x-coordinate of each person
                x_avg_list.append(x_avg)
                x_avg = round((x1+x2)/2,2)  # middle x coordinate
                # print(f"Person {i} is at: {x_avg}")
        print_info(x_avg_list, width_lower_bound, width_upper_bound)

        # debug gui: enable with [gui]
        if gui:
            cv2.imshow("Debug GUI", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): # exit gui
                break

    cap.release()
    cv2.destroyAllWindows()

# start operation:
process_camera(bound=0.25)
video_path = './Tracking_SW/archive/faceoff.mov'
process_video(video_path, bound=0.25)
