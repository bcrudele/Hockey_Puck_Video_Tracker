# fsm_tracking.py

import cv2
import time

# Define states
STATE_HSV_TRACKING = "hsv_tracking"
STATE_FALLBACK_YOLO = "fallback_yolo"

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

    def track_ball_hsv(self, frame):
        # Pseudocode for HSV thresholding
        # convert to HSV, threshold orange, return mask
        return mask

    def mask_valid(self, mask):
        # Check contour area or non-zero pixel count
        return True or False

    def run_yolo(self, frame):
        # Run YOLOv5 or pre-trained model to detect people
        return detections

    def control_camera_with_mask(self, mask):
        # Calculate center of mask and send servo command
        pass

    def control_camera_with_yolo(self, detections):
        # Average person positions, send tracking command
        pass

# Example usage
def main():
    cap = cv2.VideoCapture(0)
    tracker = BallTrackerFSM()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        tracker.process_frame(frame)

        # Optional: show frame with overlays
        cv2.imshow("Tracking", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
