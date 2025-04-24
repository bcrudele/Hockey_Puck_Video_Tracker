import cv2
import keyboard
# import threading

class CameraRecorder():
    def __init__(self, cam_index=0, output="camera_recording.mp4", fps=30, resolution=(640, 480)):
        super().__init__()
        self.cam_index = cam_index
        self.output = output
        self.fps = fps
        self.resolution = resolution
        self.running = False
        self.frames = 0
    def run(self):
        cap = cv2.VideoCapture(self.cam_index)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
        cap.set(cv2.CAP_PROP_FPS, self.fps)

        writer = cv2.VideoWriter(
            self.output,
            cv2.VideoWriter_fourcc(*'mp4v'),
            self.fps,
            self.resolution
        )

        self.running = True
        while self.running:
            ret, frame = cap.read()
            self.frames += 1
            if not ret:
                print("Recording: failed to read from camera")
                break
            writer.write(frame)
            if self.frames == 300: 
                break
        cap.release()
        writer.release()
        print("Recording stopped and saved:", self.output)

