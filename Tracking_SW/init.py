# initialization code to optimize HSV parameters
import numpy as np
import cv2 as cv
import time
import matplotlib.pyplot as plt
# setup camera
cap = cv.VideoCapture(0)
#first fram cap roi select

'''
DISPLAY thing that says "place ball in center of frame", count down 3 2 1 or click capture and then go to ret, frame = cap.read() code 
'''
hsv_init_values = []
hsv_average = 0
for i in range(0, 5):
    ret, frame = cap.read()
    bbox = cv.selectROI('select', frame, False)
    # calculate hsv_average
    hsv_init_values.append(hsv_average)
    print("step back 5 ft")
    time.sleep(5)

# either average or send this array as an input into the FSM

# IDEA SOS: based on the distance of the ball from the camera (find the area of the moment), adaptively change hsv values depending on distance

