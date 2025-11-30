from NavigateMenu import GameWindow
from TakeScreenshot import take_screenshot
import time

game = GameWindow("DiscGolf.exe")
print("window_rect:", game.get_window_rect())
# game.click_throw_debug(debug=True) # for throw button
time.sleep(10)
game.focus()
game.click_throw()
take_screenshot()
print("window_rect after actions:", game.get_window_rect())



