
#----------------- VIRTUAL PAINT TRACKER ----------------

# THIS PROJECT WAS CREATED CAPTURING LIVE FOOTAGE FROM MY LAPTOP'S WEBCAM AND FROM A SPECIFIC LOCATION, BASED ON WHICH CERTAIN VALUES
# AND PREPROCESSING WAS REQUIRED, THE SAME MAY NOT BE REQUIRED FOR YOU SHOULD YOU DECIDE TO REFER TO THIS CODE FOR IMPLEMENTATION.

import cv2
import numpy as np            ###Importing Libraries

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4,480)
cap.set(10,150)

kernel = np.ones((5,5), np.uint8)  ### Defining a kernel to use for dialting the image later

def empty(x):  ##An empty function to pass when adjuisting trackbars
    pass

# cv2.namedWindow('HSV')
cv2.namedWindow('Trackbars')
cv2.createTrackbar('Hue_min','Trackbars',0,179,empty)           #creating Trackbars for hue, saturation and value
cv2.createTrackbar('Hue_max','Trackbars',179,179,empty)         
cv2.createTrackbar('Sat_min','Trackbars',0,255,empty)
cv2.createTrackbar('Sat_max','Trackbars',255,255,empty)
cv2.createTrackbar('Val_min','Trackbars',0,255,empty)
cv2.createTrackbar('Val_max','Trackbars',255,255,empty)


def getContours(ican,iconts):
    conts, hier = cv2.findContours(ican,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)    #Finding the contours of the object we want to track
    x,y,w,h = 0, 0, 0, 0                                                    
    for cnt in conts:
        area = cv2.contourArea(cnt)
        if area > 3000:                                                             #Retrieving the largest contour as this is the object who's motion we need to track
            cv2.drawContours(iconts,cnt,-1,(51,255,255),3)
            peri = cv2.arcLength(cnt,True)
            approx = cv2.approxPolyDP(cnt,0.02*peri,True)                           #retrieving the bounding box of the object    
            x,y,w,h = cv2.boundingRect(approx)
    return x+w//2,y            
                                                                                    # returning the center of the top edge of the object


points = []  #all the points that need to be plotted onto the image for paint simulation

hsvCol = [[0,116,196, 41,191,255],[57,102,135, 100,189,255], [38,40,172, 72,255,255]]  #The hsv values we need for yellow, blue and green colors, retrieved after scanning mask values from below

colors = [[51,255,255],      #BGR values for yellow, blue and green
            [255,0,0],
            [51,255,51]]


while True:
    succ, img = cap.read()
    iframe = cv2.GaussianBlur(img,(7,7),1)        #Due to a very noisy image from my laptop webcam we need to blur
    imgHSV = cv2.cvtColor(iframe,cv2.COLOR_BGR2HSV)
    
    iconts = iframe.copy()               #resultant image
    count = 0                       #tracks colors
    

    # h_min =  cv2.getTrackbarPos('Hue_min','Trackbars')
    # h_max =  cv2.getTrackbarPos('Hue_max','Trackbars')
    # s_min =  cv2.getTrackbarPos('Sat_min','Trackbars')
    # s_max =  cv2.getTrackbarPos('Sat_max','Trackbars')      Values we used to find the respective HSV values for each color
    # v_min =  cv2.getTrackbarPos('Val_min','Trackbars')
    # v_max =  cv2.getTrackbarPos('Val_max','Trackbars')

    for c in hsvCol:

        m = cv2.inRange(imgHSV,np.array(c[0:3]),np.array(c[3:6]))
        cv2.imshow(str(c[0]),m)
        icolor = cv2.bitwise_and(iframe,iframe,mask=m)              # Retrieving the color from the image, and detecting the edges of the colored object
        ican = cv2.Canny(icolor,50,50)                              # Dilating the image due to thin contour shapes drawn
        idil = cv2.dilate(ican, kernel=kernel, iterations=2)        
        x,y = getContours(idil,iconts)
        if x != 0 and y != 0:
            points.append([x,y,count])
        if len(points) != 0:
            for point in points:                                                                #Drawing all the points tracked by the object, the count variable describes which color to draw based on the index in the colors list
                cv2.circle(iconts, (point[0],point[1]), 8, colors[point[2]], cv2.FILLED)
        count = count + 1                                                                               #h = 0, 41  s = 116,191  v = 196,255 for yellow  h = 57,100, s = 102,189, v = 135,255 for blue  h = 38,72, s = 40,255, v = 172,255 for green
    #cv2.imshow('HSV',imgHSV)                      
    cv2.imshow('res', iconts)
    
    # icolor = cv2.bitwise_and(iframe,iframe,mask=m)
    # cv2.imshow('result', icolor)

    # a = cv2.add(imgHSV,iframe) add is  superposition of images
    # cv2.imshow('out', a)



    if cv2.waitKey(1) & 0xFF == ord('q'):
        break