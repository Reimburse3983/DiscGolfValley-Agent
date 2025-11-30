import pyautogui
import pygetwindow as gw
import time

def take_screenshot(left_crop, top_crop, right_crop, bottom_crop, screenshot_path="", should_save=False):
    # Find the window by title
    window = gw.getWindowsWithTitle("DiscGolf")[0]

    # Bring the window to the front
    window.activate()

    time.sleep(0.5)  # wait for the window to come to the front

    # Take a screenshot of the window area
    screenshot = pyautogui.screenshot(region=(window.left, window.top, window.width, window.height))

    # Crop the screenshot: (left, top, right, bottom)
    cropped = screenshot.crop((
        left_crop,  # left
        top_crop,  # top
        screenshot.width - right_crop,  # right
        screenshot.height - bottom_crop   # bottom
    ))
    # Save the cropped screenshot
    if should_save:
        cropped.save(screenshot_path)
    return cropped
