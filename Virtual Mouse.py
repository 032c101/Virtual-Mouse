import datetime

import cv2
import numpy as np
import time
import HandTracking as ht
import autopy
import math
import os


### Variables Declaration
pTime = 0               # Used to calculate frame rate
width = 600             # Width of Camera
height = 480           # Height of Camera
frameR = 100            # Frame Rate
smoothening = 8         # Smoothening Factor
prev_x, prev_y = 0, 0   # Previous coordinates
curr_x, curr_y = 0, 0   # Current coordinates

cap = cv2.VideoCapture(0)   # Getting video feed from the webcam
cap.set(4, width)           # Adjusting size
cap.set(6, height)

detector = ht.handDetector(maxHands=1) # Detecting one hand at max
screen_width, screen_height = autopy.screen.size()      # Getting the screen size




while True:
    success, img = cap.read()
    img = detector.findHands(img)                       # Finding the hand
    lmlist, bbox = detector.findPosition(img)           # Getting position of hand

    if len(lmlist)!=0:
        x1, y1 = lmlist[8][1:]
        x2, y2 = lmlist[12][1:]

        fingers = detector.fingersUp()      # Checking if fingers are upwards
        cv2.rectangle(img, (frameR, frameR), (width - frameR, height - frameR - 50), (255, 0, 255), 2)   # Creating boundary box


        # Right Click
        if fingers[0] == 0 and fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 0:
            x1, y1 = lmlist[8][1], lmlist[8][2]
            x2, y2 = lmlist[12][1], lmlist[12][2]
            x3, y3 = lmlist[16][1], lmlist[16][2]

            cv2.circle(img, (x1, y1), 15, (0, 255, 0), cv2.FILLED)
            cv2.circle(img, (x2, y2), 15, (0, 255, 0), cv2.FILLED)
            cv2.circle(img, (x3, y3), 15, (0, 255, 0), cv2.FILLED)

            length1 = math.hypot(x3 - x2, y3 - y2)
            length2 = math.hypot(x2 - x1, y2 - y1)
            if(length1 < 45 and length2 < 45):
                autopy.mouse.click(autopy.mouse.Button.RIGHT) # Right Click

        # Screenshot
        if fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0: #If thumb and index finger both are up

            x1, y1 = lmlist[4][1], lmlist[4][2]
            x2, y2 = lmlist[8][1], lmlist[8][2]
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

            cv2.circle(img, (x1,y1), 15, (255,0,255), cv2.FILLED)
            cv2.circle(img, (x2,y2), 15, (255,0,255), cv2.FILLED)
            cv2.line(img, (x1,y1), (x2,y2), (255,0,255), 3)
            cv2.circle(img, (cx, cy), 10, (255, 0, 255), cv2.FILLED)

            length = math.hypot(x2 - x1, y2 - y1)

            if(length < 30):
                cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)
                now = datetime.datetime.now()
                filename = f"screenshot_{now.strftime('%Y-%m-%d_%H-%M-%S')}.png"
                screenshot = autopy.bitmap.capture_screen()
                screenshot.save(filename)
                print("Screenshot Captured")

        # Cursor movement
        if fingers[1] == 1 and fingers[2] == 0 and fingers[0] == 0:     # If fore finger is up and middle finger is down
            x3 = np.interp(x1, (frameR,width-frameR), (0,screen_width))
            y3 = np.interp(y1, (frameR, height-frameR), (0, screen_height))

            curr_x = prev_x + (x3 - prev_x)/smoothening
            curr_y = prev_y + (y3 - prev_y) / smoothening

            autopy.mouse.move(screen_width - curr_x, curr_y)    # Moving the cursor
            cv2.circle(img, (x1, y1), 7, (255, 0, 255), cv2.FILLED)
            prev_x, prev_y = curr_x, curr_y

        # Left Click
        if fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0:     # If fore finger & middle finger both are up
            length, img, lineInfo = detector.findDistance(8, 12, img)

            if length < 40:     # If both fingers are really close to each other
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                autopy.mouse.click()    # Perform Left Single Click

        # Shut Down
        if fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 1:
            x1, y1 = lmlist[8][1], lmlist[8][2]
            x2, y2 = lmlist[12][1], lmlist[12][2]
            x3, y3 = lmlist[16][1], lmlist[16][2]
            x4, y4 = lmlist[20][1], lmlist[20][2]
            x0, y0 = lmlist[4][1], lmlist[4][2]

            cv2.circle(img, (x1, y1), 15, (0, 255, 0), cv2.FILLED)
            cv2.circle(img, (x2, y2), 15, (0, 255, 0), cv2.FILLED)
            cv2.circle(img, (x3, y3), 15, (0, 255, 0), cv2.FILLED)
            cv2.circle(img, (x4, y4), 15, (0, 255, 0), cv2.FILLED)
            cv2.circle(img, (x0, y0), 15, (0, 255, 0), cv2.FILLED)

            length0 = math.hypot(x1 - x0, y1 - y0)
            length1 = math.hypot(x2 - x1, y2 - y1)
            length2 = math.hypot(x3 - x2, y3 - y2)
            length3 = math.hypot(x4 - x3, y4 - y3)
            #print(length0, length1, length2, length3)
            if(length0 < 35 and length1 < 35 and length2 < 35 and length3 < 35):
                os.system("shutdown /s /t 0")



    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)
    cv2.imshow("Image", img)
    cv2.waitKey(1)