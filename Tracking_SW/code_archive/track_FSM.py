# fsm_tracking.py

import cv2
import time

# Define states
STATE_HSV_TRACKING = "hsv_tracking"
STATE_FALLBACK_YOLO = "fallback_yolo"

# IDEA SOS: based on the distance of the ball from the camera (find the area of the moment), adaptively change hsv values depending on distance
class BallTrackerFSM:
    def __init__(self):
        self.state = STATE_HSV_TRACKING
        self.hsv_lost_counter = 0
        self.hsv_lost_threshold = 10  # frames before switching to YOLO
        self.yolo_check_interval = 5  # only run YOLO every N frames
        self.frame_count = 0
        self.yolo_mode_cooldown = 30  # min frames before trying to go back to HSV
        self.last_yolo_mode_entry = -999

    def process_frame(self, frame):
        if self.state == STATE_HSV_TRACKING:
            mask = self.track_ball_hsv(frame)
            if self.mask_valid(mask):
                self.hsv_lost_counter = 0
                self.control_camera_with_mask(mask)
            else:
                self.hsv_lost_counter += 1
                if self.hsv_lost_counter >= self.hsv_lost_threshold:
                    self.state = STATE_FALLBACK_YOLO
                    self.last_yolo_mode_entry = self.frame_count

        elif self.state == STATE_FALLBACK_YOLO:
            if self.frame_count % self.yolo_check_interval == 0:
                detections = self.run_yolo(frame)
                self.control_camera_with_yolo(detections)

                # Still run HSV tracking in the background
                mask = self.track_ball_hsv(frame)
                if self.mask_valid(mask):
                    if self.frame_count - self.last_yolo_mode_entry >= self.yolo_mode_cooldown:
                        self.state = STATE_HSV_TRACKING
                        self.hsv_lost_counter = 0

        self.frame_count += 1

    