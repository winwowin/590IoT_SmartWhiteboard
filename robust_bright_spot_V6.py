# import the necessary packages
import numpy as np
import argparse
import cv2
import sys
import contextlib
with contextlib.redirect_stdout(None):
    import pygame
from pygame import gfxdraw
import numpy as np

print("Welcome to IR whiteboard program \n\nPress c to clear the screen\nPress s to save the screenshot\nPress q to quit the program\n\n")

circleSize = 11  #radius size ODD NUMBER ONLY ##################################### change circle size here ODD NUMBER ONLY!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
brightnessTrigger = 250  #Brightness trigger, min 0 max 255

meas = []
pred = []
frame = np.zeros((400, 400, 3), np.uint8)  # drawing canvas
mp = np.array((2, 1), np.float32)  # measurement
tp = np.zeros((2, 1), np.float32)  # tracked / prediction

# def adjust_gamma(image, gamma=1.0):
#    invGamma = 1.0 / gamma
#    table = np.array([((i / 255.0) ** invGamma) * 255
#       for i in np.arange(0, 256)]).astype("uint8")
#    return cv2.LUT(image, table)

import time

icount = 0
nameCount = 1

kalman = cv2.KalmanFilter(4, 2)
kalman.measurementMatrix = np.array([[1, 0, 0, 0], [0, 1, 0, 0]], np.float32)
kalman.transitionMatrix = np.array([[1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0], [0, 0, 0, 1]], np.float32)
kalman.processNoiseCov = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]], np.float32) * 0.03

cap = cv2.VideoCapture(0)       #object to capture video
frame_counter = 1               #just count frame

locationList = list()           #location for the spot drawing


while(True):

    # # construct the argument parse and parse the arguments

    # to make it stable, we neeed to make the bright spot detection become an area (radius) instead of a single pixel. 
    ap = argparse.ArgumentParser()                  #To pass the number of radius size, we need to use args() and this is the object 
    args = vars(ap.parse_args())                    #args is the function to pass the variable
    args["radius"]=circleSize                               #radius size

    # # load the image and convert it to grayscale for more stable than color
    ret, image = cap.read()                         #capter an image frame
    image[0:circleSize, 0:circleSize] = (brightnessTrigger,brightnessTrigger,brightnessTrigger)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  #convert image to gray scale

    gray = cv2.GaussianBlur(gray, (args["radius"], args["radius"]), 0)      # apply a Gaussian blur to the image then find the brightest region 
    # adjust_gamma(gray, -1.5)                                              #dim the grammar to make it easier to spot the light
    (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(gray)                  # find the (x, y) coordinates of the area of the image with the largest intensity value (function to locate min-max intensity)
    # print ( "Brightness: ", maxVal,  "    Location (x,y): ", maxLoc)        #print out the color code and location ####### slow down the program in RPi so comment out

    cv2.circle(image, maxLoc, args["radius"], (255, 0, 0), 2)               #drawing the circle at the location to show the spot

    # display the results of our newly improved method
    window = cv2.imshow("Hit q to quit", image)                             #show it on a window


    # to draw on the virtual board on computer >>>>>>>> I'm drawing it by save all the brightest location from every frame and use for loop to draw it
    canvas = pygame.display.set_mode((640,480))                 #set up empty canvas to draw. Canvas size >>>> set_mode(x,y)

    locationList.append(maxLoc)                                 #put the location of the brightest spot onto the location list we have set up at the beginning
    mp = np.array([[np.float32(maxLoc[0])], [np.float32(maxLoc[1])]])

    kalman.correct(mp)
    tp = kalman.predict()
    pred.append((int(tp[0]), int(tp[1])))

    if maxLoc != (0,0):
        for a in range(frame_counter):                              #for loop equal to draw a dot as many time as the number of frame (first )
            canvas.set_at(locationList[a], (255, 255, 255))         #drawing a dot from each frame
            # pygame.draw.line(canvas, (255, 255, 255), locationList[a - 1], locationList[a])
            for i in range(len(pred) - 1):
                if pred[i] > (0, 0):
                    icount += 1
                    if icount > 1:
                        pygame.draw.line(canvas, (0, 0, 200), pred[i], pred[i + 1],5)
                else:
                    icount = 0

        pygame.display.update() #flip()                             #update the canvas (flip is similar)


    # we can use pygame function to connect between the dot from locationList[]
    # then use kalman filter to smooth it out

    # then we need to make function (question) to start a new page 
        # >>>>> save canvas to a picture >>>> cv2.imwrite()
        # >>>>> clean up the drawing by empty the locationList[]

    if pygame.key.get_pressed()[pygame.K_s]:
        print("S(ave) pressed, saving screenshot...")
        pygame.image.save(canvas, "screenshot"+str(nameCount)+".jpg")
        print("screenshot"+str(nameCount)+".jpg has been saved...")
        nameCount += 1

    if pygame.key.get_pressed()[pygame.K_c]:
        print("C(lear) pressed, clearing the screen...")
        locationList.clear()
        frame_counter = 0
        pred = []
        frame = np.zeros((400, 400, 3), np.uint8)

    if pygame.key.get_pressed()[pygame.K_q]:
        print("Q(uit) pressed, exiting...")
        sys.exit()

    frame_counter += 1                          #+1 on frame counter
    # print("Frame: ", frame_counter)             #print frame number

    if cv2.waitKey(1) & 0xFF == ord('s'):
        print("S(ave) pressed, saving screenshot...")
        pygame.image.save(canvas, "screenshot"+str(nameCount)+".jpg")
        print("screenshot"+str(nameCount)+".jpg has been saved...")
        nameCount += 1

    if cv2.waitKey(1) & 0xFF == ord('c'):
        print("C(lear) pressed, clearing the screen...")
        locationList.clear()
        frame_counter = 0
        pred = []
        frame = np.zeros((400, 400, 3), np.uint8)

    if cv2.waitKey(1) & 0xFF == ord('q'):       #if key press is 'q' then
        print("Q(uit) pressed, exiting...")     #print quitting message
        sys.exit()                              #terminate the program
