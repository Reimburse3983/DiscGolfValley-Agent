from GameWindow import GameWindow
from TakeScreenshot import take_screenshot
import time
from PIL import Image, ImageOps, ImageFilter
import pytesseract
import cv2
import numpy as np
import math
from ReinforcementLearning import Agent, make_actions, ACTIONS
import matplotlib
matplotlib.use("Agg")   # use non-GUI backend BEFORE importing pyplot
import matplotlib.pyplot as plt



def ocr_distance(screenshot):
    """OCR to extract distance digits from a PIL image."""
    distance_region=screenshot.convert('L')  # Convert to grayscale
    # Only allow digits
    custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789'
    distance_text = pytesseract.image_to_string(distance_region, config=custom_config)

    # Filter digits just in case
    distance = ''.join(filter(str.isdigit, distance_text))
    #print(distance)
    return distance

def ocr_distance_v2(pil_img):
    """OCR to extract distance digits from a PIL image."""

    # PIL → OpenCV
    img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

    # Convert to HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    lower_white = np.array([0, 0, 180])
    upper_white = np.array([255, 40, 255])
    mask = cv2.inRange(hsv, lower_white, upper_white)
    mask

    # Denoise
    mask = cv2.medianBlur(mask, 3)

    # Upscale for better OCR
    mask_big = cv2.resize(mask, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)

    # OCR digit-only whitelist
    config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789'

    text = pytesseract.image_to_string(mask_big, config=config)

    # Extract digits only
    digits = ''.join(c for c in text if c.isdigit())

    return digits

def ocr_digits_print_and_return_best(pil_img):
    """
    Try multiple preprocessing variants, print each variant's OCR,
    and return only the best digits string.
    """
    def run_tess(pil, config):
        raw = pytesseract.image_to_string(pil, config=config)
        digits = ''.join(ch for ch in raw if ch.isdigit())
        return raw, digits

    config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789'

    img_cv = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

    attempts = []

    # --- Variant A: autocontrast + unsharp + upscale (this produced correct '9' in testing) ---
    p = ImageOps.autocontrast(pil_img)
    p = p.filter(ImageFilter.UnsharpMask(radius=1, percent=200, threshold=3))
    for scale in [2, 3]:
        p_up = p.resize((p.width*scale, p.height*scale), Image.NEAREST)
        raw, digits = run_tess(p_up, config)
        attempts.append((f"autocontrast_unsharp_x{scale}", raw, digits, p_up))

    # --- Variant B: CLAHE (good for some images) ---
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    cl = clahe.apply(gray)
    for scale in [2, 3]:
        cl_up = cv2.resize(cl, (cl.shape[1]*scale, cl.shape[0]*scale), interpolation=cv2.INTER_NEAREST)
        raw, digits = run_tess(Image.fromarray(cl_up), config)
        attempts.append((f"clahe_x{scale}", raw, digits, Image.fromarray(cl_up)))

    # --- Variant C: simple Otsu (upscaled) ---
    up = cv2.resize(gray, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    _, th_otsu = cv2.threshold(up, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    raw, digits = run_tess(Image.fromarray(th_otsu), config)
    attempts.append(("otsu_x3", raw, digits, Image.fromarray(th_otsu)))

    # --- Variant D: adaptive threshold (upscaled) ---
    #th_adapt = cv2.adaptiveThreshold(up, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    #                                 cv2.THRESH_BINARY, 11, 2)
    #raw, digits = run_tess(Image.fromarray(th_adapt), config)
    #attempts.append(("adaptive_x3", raw, digits, Image.fromarray(th_adapt)))

    # --- Variant E: loose HSV mask (fill + upscale) ---
    hsv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2HSV)
    lower = np.array([0, 0, 120])
    upper = np.array([255, 120, 255])
    mask = cv2.inRange(hsv, lower, upper)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)), iterations=1)
    for scale in [2,3]:
        mask_up = cv2.resize(mask, (mask.shape[1]*scale, mask.shape[0]*scale), interpolation=cv2.INTER_NEAREST)
        raw, digits = run_tess(Image.fromarray(mask_up), config)
        attempts.append((f"hsv_loose_x{scale}", raw, digits, Image.fromarray(mask_up)))

    # Print all attempts and choose best
    print("\n=== OCR VARIANT RESULTS ===")
    best = None
    for name, raw, digits, img_for_debug in attempts:
        conf_note = "(no confidence used)"
        print(f"[{name}] raw={repr(raw)} digits='{digits}' {conf_note}")
        score = (1 if digits else 0, len(digits))
        if best is None or score > best[0]:
            best = (score, (name, raw, digits, img_for_debug))

    if best is not None:
        name, raw, digits, _ = best[1]
        print(f"\n=== BEST: {name} -> digits='{digits}' raw={repr(raw)} ===\n")
        return digits
    else:
        print("\nNo digits found in any preprocess.\n")
        return -1


def ocr_wind_power(pil_img):
    """ Returns wind power as string from PIL image. """
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

    #print("Gauge center:", (int(gx), int(gy)))
    #print("Arrow tip:", (int(tx), int(ty)))
    print("Angle (0–360°):", angle)
    return angle

def get_game_information(game, count):
    """ Returns [distance_to_hole, wind_power, wind_angle] """
    #game.focus()
    #print("focused")
    game.click_throw()
    print("throw clicked")
    take_screenshot(130, 90, 450, 200, "Screenshots/screenshot_cropped.png", should_save=False)
    #print("window_rect after actions:", game.get_window_rect())
    ocr_distance_screenshot=take_screenshot(770, 45, 505, 700, should_save=False)
    distance_to_hole=ocr_digits_print_and_return_best(ocr_distance_screenshot)
    take_screenshot(1060, 275, 50, 300, screenshot_path=f"Screenshots/wind_angle_screenshot{count}.png", should_save=True)
    wind_power_screenshot=take_screenshot(1140, 345, 126, 395, screenshot_path="Screenshots/other_thing.png", should_save=False)
    wind_power=ocr_wind_power(wind_power_screenshot)
    print("Distance:", distance_to_hole)
    print("Wind Power:", wind_power)
    wind_angle= get_wind_angle(f"Screenshots/wind_angle_screenshot{count}.png")
    return [int(distance_to_hole), int(wind_power), round(wind_angle)]

def throw_disc(game, distance_to_hole, x_coord, y_coord):
    """ Performs the throw action and returns the reward value. """
    game.click_throw()
    time.sleep(1)
    game.drag(650, 125, x_coord , y_coord)
    time.sleep(11) # wait for throw animaiton to finish
    game.click(900, 670) # clicking move to hole
    time.sleep(1)
    end_distance_screenshot= take_screenshot(770, 45, 482, 700, screenshot_path="Screenshots/end_distance_screenshot.png", should_save=True)
    end_distance = ocr_digits_print_and_return_best(end_distance_screenshot)
    print("End Distance:", end_distance)
    if end_distance == '':
        print("OCR failed to read end distance due to single digit problems. Assigning default reward of 0.85")
        return -1 # OCR failed due to single digit weirdness. Return -1 to indicate a skip during training loop.
    reward_value = 2 if int(distance_to_hole) == int(end_distance) else (int(distance_to_hole)-int(end_distance))/int(distance_to_hole)
    print("Reward Calculation:" + str(reward_value))
    # reinfocement learning should out x between 0-500 and y between 0 -200
    return reward_value



"""# --- Main Training Loop ---"""
agent=Agent()
gameObject = GameWindow("DiscGolf")
#print("window_rect:", gameObject.get_window_rect())
time.sleep(1)
reward_history = []
for ep in range(10000):
    """ Training loop for the RL agent. """
    state =get_game_information(gameObject, ep)

    # one throw only
    a_idx = agent.act(state)
    action_xy = ACTIONS[a_idx]

    reward = throw_disc(gameObject, state[0], action_xy[0], action_xy[1])
    if reward == -1:
        print("Skipping training update due to OCR failure.")
        gameObject.reset()
        continue
    reward = reward**2  # square reward to emphasize good throws
    agent.update(state, a_idx, reward)
    reward_history.append(reward)
    print(f"Episode {ep}, reward={reward:.3f}, epsilon={agent.epsilon:.3f}")
    if ep % 10 == 0 and ep > 0:
        plt.figure()
        plt.plot(reward_history)
        plt.xlabel("Episode")
        plt.ylabel("Reward")
        plt.title(f"Reward Over Time — Episode {ep}")
        plt.savefig(f"Plots/reward_plot_ep{ep}.png")  # save image
        plt.close()  # prevent memory leak
        agent.save(f"Checkpoints/agent_checkpoint_ep{ep}.pth")

    gameObject.reset()



