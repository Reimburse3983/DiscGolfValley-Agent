from turtle import distance
from pyscreeze import screenshot
from NavigateMenu import GameWindow
from TakeScreenshot import take_screenshot
import time
import pytesseract


def ocr_stuff(screenshot):

    distance_region=screenshot.convert('L')  # Convert to grayscale
    # Only allow digits
    custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789'
    distance_text = pytesseract.image_to_string(distance_region, config=custom_config)

    # Filter digits just in case
    distance = ''.join(filter(str.isdigit, distance_text))
    print(distance)
    return distance



game = GameWindow("DiscGolf.exe")
print("window_rect:", game.get_window_rect())
time.sleep(10)
game.focus()
game.click_throw()
take_screenshot(130, 90, 450, 200, "Screenshots/screenshot_cropped.png", should_save=True)
print("window_rect after actions:", game.get_window_rect())
ocr_distance=take_screenshot(770, 45, 505, 700, should_save=False)
distance=ocr_stuff(ocr_distance)









