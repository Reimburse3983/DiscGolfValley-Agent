from turtle import distance
from pyscreeze import screenshot
from NavigateMenu import GameWindow
from TakeScreenshot import take_screenshot
import time
import pytesseract
import cv2
import numpy as np
import math


def ocr_stuff(screenshot):

    distance_region=screenshot.convert('L')  # Convert to grayscale
    # Only allow digits
    custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789'
    distance_text = pytesseract.image_to_string(distance_region, config=custom_config)

    # Filter digits just in case
    distance = ''.join(filter(str.isdigit, distance_text))
    print(distance)
    return distance

def get_wind_angle(screenshot):
    # ---- Load image ----
    img = cv2.imread("gauge.png")

    # ---- Convert to HSV for arrow detection ----
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # ---- Mask red arrow only (center color irrelevant) ----
    lower_red1 = np.array([0, 80, 80])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 80, 80])
    upper_red2 = np.array([180, 255, 255])
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = mask1 | mask2

    # ---- Find arrow contour ----
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    arrow = max(contours, key=cv2.contourArea)

    # ---- Arrow centroid ----
    M = cv2.moments(arrow)
    cx = int(M["m10"] / M["m00"])
    cy = int(M["m01"] / M["m00"])

    # ---- Tip is farthest from centroid ----
    farthest = max(arrow, key=lambda p: (p[0][0]-cx)**2 + (p[0][1]-cy)**2)
    tx, ty = farthest[0]

    # ---- Detect the gauge circle (center is color-independent) ----
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)

    circles = cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=100,
        param1=50,
        param2=30,
        minRadius=10,
        maxRadius=500
)

    if circles is None:
        raise Exception("No circle found — increase contrast or tweak params.")

    circles = np.uint16(np.around(circles))
    gx, gy, radius = circles[0][0]
    # ---- Compute 0–360° angle ----
    dx = tx - gx
    dy = gy - ty     # invert y axis

    angle_rad = math.atan2(dx, dy)
    angle_deg = math.degrees(angle_rad)
    angle = (angle_deg + 360) % 360

    print("Gauge center:", (gx, gy))
    print("Arrow tip:", (tx, ty))
    print("Angle (0–360°):", np.angle)

game = GameWindow("DiscGolf")
print("window_rect:", game.get_window_rect())
time.sleep(10)
game.click_throw()
take_screenshot(130, 90, 450, 200, "Screenshots/screenshot_cropped.png", should_save=True)
print("window_rect after actions:", game.get_window_rect())
ocr_distance=take_screenshot(770, 45, 505, 700, should_save=False)
distance=ocr_stuff(ocr_distance)









