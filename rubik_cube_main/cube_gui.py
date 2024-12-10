###########################################
# pc側メインプログラム
# 実行するのはこれ
###########################################

########
# 前操作
########

# cv2のインポート前にカメラに関する設定を行う
# カメラの起動を高速化する
# https://github.com/opencv/opencv/issues/17687
import os 
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"

import cv2 #画像認識のためにopencvをインポート
import tkinter # UIを作るためtkinterライブラリをインポート
from time import sleep, time
import cube_capture as cubeCapture
import cube_transform as cubeTransform
import cube_socket as cubeSocket
import cube_control as cubeControl

path = 'image_log/'
capture = cubeCapture.Capture(path)
transform = cubeTransform.Transform()
socket = cubeSocket.Socket()
control = cubeControl.Control()


############
# GUI
############
class GUI:
    def __init__(self):
        self.root = tkinter.Tk()
        self.root.title("rubik's solver") # UIのタイトル
        self.root.geometry("700x500") # UIの画面サイズ
        self.color_list = ['w','y','g','r','b','o']
        self.button_colors = ['#ffffff','#ffff00','#00ff00','#ff0000', '#0000ff', '#ffAA00'] # 画像上に表示する色
        self.color_num = [[i for _ in range(9)] for i in range(6)] # 色の番号の配列

        self.entry = [[None for _ in range(9)] for _ in range(6)] # UI上のボタン

    def __def__(self):
        del capture
        del transform
        del socket
        del control

    # 色のボタンが押された時のコールバック関数
    def change_btn_callback(self, i, j):
        def x():
            self.color_num[i][j] = (self.color_num[i][j] + 1) % 6 # 色を変える
            self.entry[i][j].config(bg = self.button_colors[self.color_num[i][j]]) # 反映する
        return x

    # resetボタンが押された時のコールバック関数
    def reset_btn_callback(self, event=None):
        control.reset()

    # setボタンが押された時のコールバック関数
    def set_btn_callback(self, event=None):
        control.release_all()
        sleep(3)
        control.grip_all()

    # testボタンが押された時のコールバック関数
    def test_btn_callback(self, event=None):
        self.status_ver.set("Status -> Scanning ...")
        # self.status_ver.update()
        capture.test_capture()

    # captureボタンが押された時のコールバック関数
    # 撮影開始の送信
    def capture_btn_callback(self, event=None):
        self.status_ver.set("Status -> Scanning ...")
        # self.status_ver.update()
        # 画像保存用に現在時刻を取得
        capture.set_date_now()
        print("capture start")
        for phase in range(6):
            control.scan(phase)
            # sleep(.5)
            face_colors = capture.find_color(phase)
            for cell in range(9):
                self.color_num[phase][cell] = face_colors[cell] # 面の色を保存
                self.entry[phase][cell].config(bg = self.button_colors[self.color_num[phase][cell]]) # ボタンの生成
                self.entry[phase][cell].update()
        control.scan_finalize()
        control.arm_setup()

    # 画面の情報の初期化
    def window_setup(self):
        for phase in range(6):
            for cell in range(9):
                self.entry[phase][cell].config(bg = "#101010") # ボタンの生成
                self.entry[phase][cell].update()
        self.status_ver.set("Status -> Waiting ...")
        self.status_ver_obj.update()
        self.solution_ver.set("Solution ->")
        self.solution_ver_obj.update()
        self.time_ver.set("Solve Time ->")
        self.time_ver_obj.update()
        self.text_ver.set("キューブを台に置いたら，ボタンを押してね")
        self.text_ver_obj.update()

    # startボタンが押された時のコールバック関数
    # キューブを解くプログラムに依頼する
    def start_btn_callback(self, event=None):
        self.window_setup()
        # タッチセンサを待機
        while not(control.button_pressed()):
            pass    
        control.reset()
        sleep(.5)
        self.text_ver.set("動作中 ...")
        self.text_ver_obj.update()
        control.grip_all()
        sleep(.5)
        control.lift_down()
        control.grip_all()
        self.capture_btn_callback()
        color_num_list, direction = transform.gen_color_num(self.color_num) # キューブの状態と基準面の展開図配列に変換
        color_num_str = transform.num_to_str(color_num_list) # 色番号の配列を文字の配列に変換
        scrambled_state = transform.taransform(color_num_str) # 色の配列から状態の配列へ変換
        if scrambled_state: # 配列を変換できたか
            solution, solution_time = socket.send_solver(scrambled_state)
            if solution:
                self.time_ver.set(f"Solve Time -> 答えを見つけるまで {solution_time:.3f}秒")
                self.time_ver_obj.update()
                solution_len = len(solution.split())
                self.status_ver.set("Status -> Running ...")
                self.status_ver_obj.update()
                self.solution_ver.set(f"Solution -> 見つけた答え {solution} ({solution_len} 手)")
                self.solution_ver_obj.update()                
                print(f"ans:{solution}({solution_len}moves), direction={direction}")
                start = time()
                control.execute(solution, direction)
                end = time()
                self.time_ver.set(f"Solve Time -> 答えを見つけるまで {solution_time:.3f}秒, キューブを解くまで {end - start:.1f}秒")
                self.time_ver_obj.update()
            else:
                print("Recv Timed out")
                self.status_ver.set("Status -> Recv Timed out")
                self.status_ver_obj.update()
        else:
            self.status_ver.set("Status -> Color Error")
            self.status_ver_obj.update()
            color_count = [0,0,0,0,0,0]
            for color_str in color_num_str:
                for i, color in enumerate(self.color_list):
                    color_count[i] += color_str.count(color)
        control.arm_setup()
        sleep(1)
        control.lift_up()
        control.release_all()

        self.status_ver.set("Status -> Finish !")
        self.status_ver_obj.update()
        self.text_ver.set("Spaceキーで開始 その他キー割り当てはREADME参照")
        self.text_ver_obj.update()

        sleep(.5)
        control.reset()

    def lift_up_callback(self, event=None):
        control.lift_up()
    
    def lift_down_callback(self, event=None):
        control.lift_down()

    
    def cell_reset(self):
        for i in range(6):
            for j in range(9):
                self.entry[i][j].config(bg = self.button_colors[i]) # ボタンの色のリセット

    def start(self):
        for i in range(6):
            grid = 30 # ボタン間の幅
            offset = 30 # ボタンの端からの距離
            face_pos = [[3,0],[3,6],[3,3],[6,3],[9,3],[0,3]] # 各面の全体の位置
            cell_pos = [[0,0],[2,0],[2,2],[0,2],[1,0],[2,1],[1,2],[0,1],[1,1]] # 各面の中の各ボタンの位置
            for j in range(9):
                self.entry[i][j] = tkinter.Button(master=self.root, width=2, bg='#101010',command=self.change_btn_callback(i,j)) # ボタンの生成
                self.entry[i][j].place(x = offset + (face_pos[i][0] + cell_pos[j][0]) * grid, y = offset + (face_pos[i][1] + cell_pos[j][1]) * grid) # 展開図の配置

        self.status_ver = tkinter.StringVar(master=self.root,value="Status -> ") # エラーログを表示するバーの生成
        self.status_ver_obj = tkinter.Label(textvariable=self.status_ver) # 表示するテキストの設定
        self.status_ver_obj.place(x =0, y = 350) # 表示するテキストの位置

        self.solution_ver = tkinter.StringVar(master=self.root,value='Solution ->')
        self.solution_ver_obj = tkinter.Label(textvariable=self.solution_ver)
        self.solution_ver_obj.place(x =0, y = 375)

        self.time_ver = tkinter.StringVar(master=self.root,value='Solve Time ->')
        self.time_ver_obj = tkinter.Label(textvariable=self.time_ver) 
        self.time_ver_obj.place(x =0, y = 400)

        self.text_ver = tkinter.StringVar(master=self.root,value='Spaceキーで開始 その他キー割り当てはREADME参照')
        self.text_ver_obj = tkinter.Label(textvariable=self.text_ver) 
        self.text_ver_obj.place(x =0, y = 425)

        self.root.bind("<r>", self.reset_btn_callback)
        self.root.bind("<t>", self.test_btn_callback)
        self.root.bind("<space>", self.start_btn_callback)
        self.root.bind("<u>", self.lift_up_callback)
        self.root.bind("<d>", self.lift_down_callback)
        self.root.mainloop() # GUIの表示