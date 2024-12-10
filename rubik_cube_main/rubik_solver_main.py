###########################################
# pc側メインプログラム
# 実行するのはこれ
###########################################

import cube_gui as cubeGUI

gui = cubeGUI.GUI()
try:
    gui.start()
finally:
    del gui