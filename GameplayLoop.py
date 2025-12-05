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

def ocr_wind_power(pil_img):
    img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_BGR2RGB)

    # --- Convert to HSV (much better for isolating colors) ---
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)

    # --- Mask for yellow digit ---
    # Tune if needed, but this range matches your screenshot perfectly
    mask = hsv
    # --- Upscale the mask ---
    mask = cv2.resize(mask, None, fx=4, fy=4, interpolation=cv2.INTER_NEAREST)

    # --- (Optional) Slight dilation to thicken the shape ---
    kernel = np.ones((3,3), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=1)

    # --- OCR tuned for digit ---
    config = "--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789"
    text = pytesseract.image_to_string(mask, config=config)

    return ''.join(filter(str.isdigit, text))

def get_wind_angle(screenshot):
    # ---- Load image ----
    img = cv2.imread(screenshot)

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

    print("Gauge center:", (int(gx), int(gy)))
    print("Arrow tip:", (int(tx), int(ty)))
    print("Angle (0–360°):", angle)
    return angle

game = GameWindow("DiscGolf")
print("window_rect:", game.get_window_rect())
time.sleep(1)

game.focus()
print("focused")
game.click_throw()
print("throw clicked")
take_screenshot(130, 90, 450, 200, "Screenshots/screenshot_cropped.png", should_save=True)
print("window_rect after actions:", game.get_window_rect())
ocr_distance=take_screenshot(770, 45, 505, 700, should_save=False)
distances=ocr_stuff(ocr_distance)
wind_direction=take_screenshot(1060, 275, 50, 300, screenshot_path="Screenshots/wind_gauge.png", should_save=True)
other_thing=take_screenshot(1140, 345, 126, 395, screenshot_path="Screenshots/other_thing.png", should_save=True)
wind_power=ocr_wind_power(other_thing)
print("Distance:", distances)
print("Wind Power:", wind_power)

get_wind_angle("Screenshots/wind_gauge.png")







