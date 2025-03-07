import cv2
from ultralytics import YOLO  # pip install ultralytics

model = YOLO("yolov5s.pt")  # yolov5s is a smaller model than detr

# initialize camera:
cap = cv2.VideoCapture(0)  # might have to change camera '#' later
width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
print("Camera dimensions:", (width, height))

# variables:
frame_count = 0
gui = False             # enables GUI
debug = False           # enables model results to terminal
debuff_en = False       # enable overload protection
debuff_range = 1        # process every x frames

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
    for i in range(len(boxes)):
        if labels[i] == 0:  # if a person,
            x1, y1, x2, y2 = boxes.xyxy[i].cpu().numpy()  # unpack the coordinates
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 3) # draw the rect.
            x_avg = round((x1+x2)/2,2)  # middle x coordinate
            print(f"Person {i} is at: {x_avg}")

    # debug gui: enable with [gui]
    if gui:
        cv2.imshow("Debug GUI", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): # exit gui
            break

cap.release()
cv2.destroyAllWindows()