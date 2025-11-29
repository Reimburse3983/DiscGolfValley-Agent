from NavigateMenu import GameWindow
import time

game=GameWindow("DiscGolf.exe")
#game.click_throw_debug(debug=True) # for throw button
time.sleep(10)
game.focus()
game.take_screenshot_norm((0.0, 0.0), (1, 1), save_path='dist_area.png')
game.click_throw_rel(0.5, 0.9, debug=True)
time.sleep(3)
game.take_screenshot_norm((0, 0.05), (0.65, 0.74), save_path='dist_area2.png')
game.click_throw_rel(0.5, 0.9, debug=True)



