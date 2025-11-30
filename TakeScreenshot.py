import pyautogui
import pygetwindow as gw
import time

def take_screenshot():
    # Find the window by title
    window = gw.getWindowsWithTitle("DiscGolf")[0]

    # Bring the window to the front
    window.activate()

    time.sleep(0.5)  # wait for the window to come to the front

    # Take a screenshot of the window area
    screenshot = pyautogui.screenshot(region=(window.left, window.top, window.width, window.height))

    # Crop the screenshot: (left, top, right, bottom)
    cropped = screenshot.crop((
        130,  # left
        90,  # top
        screenshot.width - 450,  # right
        screenshot.height - 200   # bottom
    ))

    # Save the cropped screenshot
    cropped.save("Screenshots/screenshot_cropped.png")
