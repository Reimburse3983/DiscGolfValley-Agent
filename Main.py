# Main runner
import time
from GameWindow import GameWindow
from OpenGame import ensure_game_running


ensure_game_running()
game = GameWindow("DiscGolf")
time.sleep(30)
game.navigate_menu()
print(game.get_size())