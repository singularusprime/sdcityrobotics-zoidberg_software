import numpy as np
import cv2
from matplotlib import pyplot as plt

# images for testing:
# from comp's video: '001.png', '002.png', '003.png', 004.png', '005.png'
# external buoy's: '010.jpg', ...
img_text = '005.png'
img = cv2.imread(img_text, 0)
img_color = cv2.imread(img_text)
img_allcontours = cv2.imread(img_text)

# import sobel function to convert image (derivative WRT y)
# ksize value influences noise levels
sobel_y = cv2.Sobel(img, cv2.CV_8U, 0, 1, ksize = 5)

# functions to heighten contour detection, changed number of iterations
thresh_y = cv2.threshold(sobel_y, 200, 255, cv2.THRESH_BINARY)[1]
thresh_y = cv2.erode(thresh_y, None, iterations = 1)
thresh_y = cv2.dilate(thresh_y, None, iterations = 1)

######### Finding which contours are buoys #########
contours = cv2.findContours(thresh_y.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
contours = contours[1];

ratioMax = 0.5
ratioMin = 0.2

buoys = []
count = 0
for contour in contours:
    cv2.drawContours(img_allcontours, [contour], -1, (255, 255, 0), 2)
    if (len(contour) > 45):
      #find the highest point in y
      highestPt = [9999999, 9999999] #set to be just really high
      endPt1 = [9999999999, 0] #will be pt with lowest x
      endPt2 = [-1, 0] #will be pt with highest x

      for Point in contour:
         tempy = Point[0][1]
         tempx = Point[0][0]
         if (tempy < highestPt[1]):
            highestPt = Point[0]
         if (tempx < endPt1[0]):
            endPt1 = Point[0]
         if (tempx > endPt2[0]):
            endPt2 = Point[0]

      #pick the endpoint highest in y
      finalEndPt = endPt1;
      if (endPt1[1] > endPt2[1]):
         finalEndPt = endPt2;

      w = abs(highestPt[0] - finalEndPt[0])
      h = abs(highestPt[1] - finalEndPt[1])
      if (w != 0):
         ratio = (h/(2*w))
      else: #safeguard against dividing by 0
         ratio = 0

      if ((ratio >= ratioMin) and (ratio <= ratioMax)):
        # print('finalEndPt', finalEndPt)
        # print('highestPt', highestPt)
        # print('valid ratio: ', ratio)
        # print()
         buoys.append(contour)
         count = count+1

print('total valid ratios: ', count)


print("Format: [object count, center(x), center(y), object size/radius, {time stamp}")
cirCount = 0
for buoy in buoys:
	(x,y),radius = cv2.minEnclosingCircle(buoy)
	#y = y + 11
	center = (int(x), int(y))
	radius = int(radius)

	q = (radius*3)/4 #arbitrary distance from center
	outliers = 0;
	for point in buoy: 
		point = point[0]
		# comment
		if (point[1] > center[1] and (point[0] > center[0] - q and point[0] < center[0] + q)):
			outliers = outliers + 1

	#print('outliers: ', outliers)
	if (outliers > 1): 
		continue

	cv2.drawContours(img_color, [buoy], -1, (255, 255, 0), 2)
	img_color = cv2.circle(img_color, center, radius, (0, 255, 0), 2)
	cirCount = cirCount + 1
	int_x = int(x)
	int_y = int(y)
	intRadius = int(radius)

	# drawing rectangle around circle for labeling
	cv2.rectangle(img_color, (int_x + intRadius, int_y+ intRadius), (int_x - intRadius, int_y - intRadius), (255, 0, 0), 2)
	#print("center(x, y) = (" + str(x) + ", " + str(y) + ")")
	#print("radius = " + str(radius))
	print("{time stamp} [" + "{:01d}".format(0,) + str(cirCount) + ", " + str(int_x) + ", " + str(int_y) + ", " + str(radius) + "]")
	

#print("center - (x, y) = (" + str(x) + ", " + str(y) + ")")
#print("radius = " + str(radius))

#cv2.imshow('Contours', img_color)
#cv2.imshow('all contours', img_allcontours)

plt.axis("off")
plt.imshow(cv2.cvtColor(img_color, cv2.COLOR_BGR2RGB))
mng = plt.get_current_fig_manager()
mng.window.showMaximized()
plt.show()