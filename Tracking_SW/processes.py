import multiprocessing
import os

def p0():
    print("ID of process running tracking and gui: {}".format(os.getpid()))

def p1():
    print("ID of process running recording: {}".format(os.getpid()))

if __name__ == "__main__":
    print("ID of main process: {}".format(os.getpid()))

    # Create process objects
    pr0 = multiprocessing.Process(target=p0)
    pr1 = multiprocessing.Process(target=p1)

    # Start the processes
    pr0.start()
    pr1.start()

    # Print process IDs (from process objects)
    print("ID of process pr0: {}".format(pr0.pid))
    print("ID of process pr1: {}".format(pr1.pid))

    # Wait for processes to finish
    pr0.join()
    pr1.join()

    print("Both processes finished execution!")

    # Check if they're still alive
    print("Process pr0 is alive: {}".format(pr0.is_alive()))
    print("Process pr1 is alive: {}".format(pr1.is_alive()))
