# Main runner
import time
from NavigateMenu import GameWindow
from OpenGame import ensure_game_running


ensure_game_running()


game = GameWindow("DiscGolf.exe")
time.sleep(40)
game.navigate_menu()
