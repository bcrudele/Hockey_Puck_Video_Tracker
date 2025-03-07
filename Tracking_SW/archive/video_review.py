import cv2
from ultralytics import YOLO  # pip install ultralytics

def process_video(video_path, model_path="yolov5s.pt", debuff_en=False, debuff_range=1, gui=True, debug=False):
    # Load the model
    model = YOLO(model_path)  # Load the YOLO model

    # Initialize video capture from file
    cap = cv2.VideoCapture(video_path)  # Replace with your video file path
    if not cap.isOpened():
        print("Error: Couldn't open video file.")
        return

    # Get video dimensions
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    print(f"Video dimensions: {width}x{height}")

    frame_count = 0  # Counter for debuffing
    while True:
        ret, frame = cap.read()  # Get each frame

        if not ret:  # If video ends or fails to grab frame
            print("Failed to grab frame")
            break

        # Process every xth frame to reduce load
        if debuff_en:
            frame_count += 1
            if frame_count % debuff_range != 0:
                continue

        # Use YOLO model to perform inference
        results = model(frame, verbose=debug)  # Perform inference
        boxes = results[0].boxes  # Get the boxes (detections)
        labels = boxes.cls  # Class labels
        confidences = boxes.conf  # Confidence scores

        # Filter out non-person detections (class 0 corresponds to 'person' in COCO dataset)
        x_avg_list = [] # to store average x coordinate
        for i in range(len(boxes)):
            if labels[i] == 0:  # Class 0 is person
                x1, y1, x2, y2 = boxes.xyxy[i].cpu().numpy()  # Get box coordinates
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 3)  # Draw bounding box
                x_avg = round((x1 + x2) / 2, 2)  # Calculate the average x-coordinate
                x_avg_list.append(x_avg)
                # print(f"Person {i} is at: {x_avg}")
        average_x = round(sum(x_avg_list) / len(x_avg_list),2)
        print(f"Average x coordinate -> {average_x}")

        # debug gui: enable with [gui]
        if gui:
            cv2.imshow("Video Processing", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):  # exit gui
                break

    cap.release()
    cv2.destroyAllWindows()

# Call the function with a video file
video_path = './Tracking_SW/archive/faceoff.mov'  # Replace with the path to your video
process_video(video_path)
