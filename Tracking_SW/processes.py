import multiprocessing
import os
import cv2
from recorder import CameraRecorder
from gui import *

# Producer function to capture frames from the camera and put them in a queue
def p0(frame_queue, stop_event):
    print("ID of process running camera capture: {}".format(os.getpid()))
    run_gui()

# GUI Process that retrieves frames, applies tracking, and records
def p1(frame_queue, stop_event):
    print("ID of process running GUI and tracking: {}".format(os.getpid()))
    recorder = CameraRecorder()
    recorder.run()  # Start the camera recording

if __name__ == "__main__":
    print("ID of main process: {}".format(os.getpid()))

    # Create a queue to share frames between the camera capture and GUI
    frame_queue = multiprocessing.Queue(maxsize=20)

    # Create a stop event to manage process termination
    stop_event = multiprocessing.Event()

    # Create process objects for camera capture and GUI (which handles tracking and recording)
    pr0 = multiprocessing.Process(target=p0, args=(frame_queue, stop_event))
    pr1 = multiprocessing.Process(target=p1, args=(frame_queue, stop_event))

    # Start the processes
    pr0.start()
    pr1.start()

    # Print process IDs
    print("ID of process pr0 (Camera capture): {}".format(pr0.pid))
    print("ID of process pr1 (GUI and tracking): {}".format(pr1.pid))

    # Wait for a specific time or user interrupt
    try:
        pr0.join(timeout=10)  # Camera capture
        pr1.join(timeout=10)  # GUI and tracking
    except KeyboardInterrupt:
        stop_event.set()  # Stop all processes on user interrupt

    # Stop all processes
    stop_event.set()

    pr0.join()  # Wait for the camera capture process to finish
    pr1.join()  # Wait for the GUI and tracking process to finish

    print("All processes finished execution!")

    # Check if the processes are still alive
    print("Process pr0 is alive: {}".format(pr0.is_alive()))
    print("Process pr1 is alive: {}".format(pr1.is_alive()))