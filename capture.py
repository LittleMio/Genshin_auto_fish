# TO MASK
import cv2 as cv
img = cv.imread('./images/bite.png')
grayImg = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
ret, thresh = cv.threshold(grayImg, 127, 255,cv.THRESH_BINARY)
cv.imwrite('./images/bite_mask.png', thresh)
cv.imshow("show thresh", thresh)
cv.waitKey(0)