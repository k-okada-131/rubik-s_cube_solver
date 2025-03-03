import tkinter # UIを作るためtkinterライブラリをインポート

# 3×3×3のルービックキューブの状態を表すクラス
class State:
    def __init__(self, cp, co, ep, eo):
        self.cp = cp # コーナーパーツの位置
        self.co = co # コーナーパーツの向き
        self.ep = ep # エッジパーツの位置
        self.eo = eo # エッジパーツの向き

    # 指定された動きを適用して新しい状態を返す
    def apply_move(self, move):
        new_cp = [self.cp[p] for p in move.cp]
        new_co = [(self.co[p] + move.co[i]) % 3 for i, p in enumerate(move.cp)]
        new_ep = [self.ep[p] for p in move.ep]
        new_eo = [(self.eo[p] + move.eo[i]) % 2 for i, p in enumerate(move.ep)]
        return State(new_cp, new_co, new_ep, new_eo)

# 3×3×3のルービックキューブをシミュレートするクラス
class Cube:
    def __init__(self, state):
        self.state = state
        self.moves = {
            'U': State([3, 0, 1, 2, 4, 5, 6, 7],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 1, 2, 3, 7, 4, 5, 6, 8, 9, 10, 11],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
            'D': State([0, 1, 2, 3, 5, 6, 7, 4],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 8],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
            'L': State([4, 1, 2, 0, 7, 5, 6, 3],
                    [2, 0, 0, 1, 1, 0, 0, 2],
                    [11, 1, 2, 7, 4, 5, 6, 0, 8, 9, 10, 3],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
            'R': State([0, 2, 6, 3, 4, 1, 5, 7],
                    [0, 1, 2, 0, 0, 2, 1, 0],
                    [0, 5, 9, 3, 4, 2, 6, 7, 8, 1, 10, 11],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
            'F': State([0, 1, 3, 7, 4, 5, 2, 6],
                    [0, 0, 1, 2, 0, 0, 2, 1],
                    [0, 1, 6, 10, 4, 5, 3, 7, 8, 9, 2, 11],
                    [0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0]),
            'B': State([1, 5, 2, 3, 0, 4, 6, 7],
                    [1, 2, 0, 0, 2, 1, 0, 0],
                    [4, 8, 2, 3, 1, 5, 6, 7, 0, 9, 10, 11],
                    [1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]
                    )}
        self.move_names = []
        faces = list(self.moves.keys())
        for face_name in faces:
            self.move_names += [face_name, face_name + '2', face_name + '\''] # 例 [U, U2, U']を追加
            self.moves[face_name + '2'] = self.moves[face_name].apply_move(self.moves[face_name]) # 例 [U2]に180°(90°×2)分の動作
            self.moves[face_name + '\''] = self.moves[face_name].apply_move(self.moves[face_name]).apply_move(self.moves[face_name]) # 例 [U']に-90°(90°×3)分の動作
        
        self.color_list = ['w','y','g','r','b','o']
        self.color_num = [[i for _ in range(9)] for i in range(6)] # 色の番号の配列

        # 各コーナーパーツの色
        # 例：元々0番の位置のコーナーパーツ(.cp[*]が0)は向き(.co[*]が0~2)によって['w', 'b', 'o']に対応します
        self.corner_parts_color = [['w', 'b', 'o'], ['w', 'r', 'b'], ['w', 'g', 'r'], ['w', 'o', 'g'], 
                            ['y', 'o', 'b'], ['y', 'b', 'r'], ['y', 'r', 'g'], ['y', 'g', 'o']]
        # 各エッジパーツの色
        # 例：元々0番の位置のエッジパーツ(.ep[*]が0)は向き(.eo[*]が0~1)によって['b', 'o']に対応します
        self.edge_parts_color = [['b', 'o'], ['b', 'r'], ['g', 'r'], ['g', 'o'], 
                            ['w', 'b'], ['w', 'r'], ['w', 'g'], ['w', 'o'],
                            ['y', 'b'], ['y', 'r'], ['y', 'g'], ['y', 'o']]
        # コーナーパーツの場所の候補 
        # 例：位置配列が0(cp[0])のコーナーパーツは展開図配列における[0,0],[4,1],[5,0]に対応します
        self.cp_coordinate = [[[0,0],[4,1],[5,0]],[[0,1],[3,1],[4,0]],[[0,2],[2,1],[3,0]],[[0,3],[5,1],[2,0]],
                        [[1,3],[5,3],[4,2]],[[1,2],[4,3],[3,2]],[[1,1],[3,3],[2,2]],[[1,0],[2,3],[5,2]]]
        # エッジパーツの場所の候補 
        # 例：位置配列が0(ep[0])のエッジパーツは展開図配列における[4,5],[5,7]に対応します
        self.ep_coordinate = [[[4,5],[5,7]],[[4,7],[3,5]],[[2,5],[3,7]],[[2,7],[5,5]],
                        [[0,4],[4,4]],[[0,5],[3,4]],[[0,6],[2,4]],[[0,7],[5,4]],
                        [[1,6],[4,6]],[[1,5],[3,6]],[[1,4],[2,6]],[[1,7],[5,6]]]

    # 指定された動きを適用して新しい状態を返す
    def scramble(self, move_name):
        self.state = self.state.apply_move(self.moves[move_name])
        return self.state
    
    # 現在の状態を返す
    def get_state(self):
        return self.state

    # 現在の状態を展開図の色番号に変換
    def cube_to_color_num(self):
        for i in range(8):
            for j in range(3):
                self.color_num[self.cp_coordinate[i][j][0]][self.cp_coordinate[i][j][1]] =  self.color_list.index(self.corner_parts_color[self.state.cp[i]][(j + self.state.co[i]) % 3])
        for i in range(12):
            for j in range(2):
                self.color_num[self.ep_coordinate[i][j][0]][self.ep_coordinate[i][j][1]] =  self.color_list.index(self.edge_parts_color[self.state.ep[i]][(j + self.state.eo[i]) % 2])
        return self.color_num

# GUIを作るためのクラス
class GUI:
    def __init__(self):
        self.root = tkinter.Tk()
        self.root.title("rubik's solver") # UIのタイトル
        self.root.geometry("700x500") # UIの画面サイズ
        self.color_list = ['w','y','g','r','b','o']
        self.button_colors = ['#ffffff','#ffff00','#00ff00','#ff0000', '#0000ff', '#ffAA00'] # 画像上に表示する色
        self.color_num = [[i for _ in range(9)] for i in range(6)] # 色の番号の配列

        self.entry = [[None for _ in range(9)] for _ in range(6)] # UI上のボタンの配列

        self.cube = Cube(State(
            [0, 1, 2, 3, 4, 5, 6, 7],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ))
        self.move_log = []

    def __def__(self):
        None

    # resetボタンが押された時のコールバック関数
    def reset_btn_callback(self, event=None):
        self.cube = Cube(State(
            [0, 1, 2, 3, 4, 5, 6, 7],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ))
        for i in range(6):
            for j in range(8):
                self.entry[i][j].config(bg = self.button_colors[i]) # ボタンの色のリセット
        self.move_log = [] # ログのリセット
        # 各バーに情報を表示
        self.cp_ver.set("cp -> " + str(self.cube.get_state().cp))
        self.cp_ver_obj.update()
        self.co_ver.set("co -> " + str(self.cube.get_state().co))
        self.co_ver_obj.update()
        self.eo_ver.set("ep -> " + str(self.cube.get_state().ep))
        self.eo_ver_obj.update()
        self.ep_ver.set("eo -> " + str(self.cube.get_state().eo))
        self.ep_ver_obj.update()
        self.move_log_ver.set("move_log -> " + str(self.move_log)[1:-1])
        self.move_log_ver_obj.update()

    # goボタンが押された時のコールバック関数
    def go_btn_callback(self, event=None):
        input_move_data = self.input_move.get() # GUI上で入力された文字列を取得
        # 入力された文字列が正しい入力か確認
        if input_move_data in self.cube.move_names:
            self.cube.scramble(input_move_data) # 入力された文字列に対応する動きを適用
            self.color_num = self.cube.cube_to_color_num() # 現在の状態を展開図の色番号に変換
            for i in range(6): 
                for j in range(9):
                    self.entry[i][j].config(bg = self.button_colors[self.color_num[i][j]]) # ボタンの色を変更
            self.move_log.append(input_move_data) # ログに追加
            # 各バーに情報を表示
            self.cp_ver.set("cp -> " + str(self.cube.get_state().cp))
            self.cp_ver_obj.update()
            self.co_ver.set("co -> " + str(self.cube.get_state().co))
            self.co_ver_obj.update()
            self.eo_ver.set("ep -> " + str(self.cube.get_state().ep))
            self.eo_ver_obj.update()
            self.ep_ver.set("eo -> " + str(self.cube.get_state().eo))
            self.ep_ver_obj.update()
            self.move_log_ver.set("move_log -> " + str(self.move_log)[1:-1])
            self.move_log_ver_obj.update()
        else:
            print("Invalid move")

    # backボタンが押された時のコールバック関数
    def back_btn_callback(self, event=None):
        if self.move_log: # ログが空でない場合
            self.cube.scramble(self.move_log.pop())
            self.color_num = self.cube.cube_to_color_num()
            for i in range(6):
                for j in range(9):
                    self.entry[i][j].config(bg = self.button_colors[self.color_num[i][j]]) # ボタンの色を変更
            # 各バーに情報を表示
            self.cp_ver.set("cp -> " + str(self.cube.get_state().cp))
            self.cp_ver_obj.update()
            self.co_ver.set("co -> " + str(self.cube.get_state().co))
            self.co_ver_obj.update()
            self.eo_ver.set("ep -> " + str(self.cube.get_state().ep))
            self.eo_ver_obj.update()
            self.ep_ver.set("eo -> " + str(self.cube.get_state().eo))
            self.ep_ver_obj.update()
            self.move_log_ver.set("move_log -> " + str(self.move_log)[1:-1])
            self.move_log_ver_obj.update() 

    # GUIの立ち上げ
    def start(self):
        # 展開図(ボタン)を設置
        for i in range(6):
            grid = 30 # ボタン間の幅
            offset = 30 # ボタンの端からの距離
            face_pos = [[3,0],[3,6],[3,3],[6,3],[9,3],[0,3]] # 各面の全体の位置
            cell_pos = [[0,0],[2,0],[2,2],[0,2],[1,0],[2,1],[1,2],[0,1],[1,1]] # 各面の中の各ボタンの位置
            for j in range(9):
                self.entry[i][j] = tkinter.Button(master=self.root, width=2, bg=self.button_colors[i]) # ボタンの生成
                self.entry[i][j].place(x = offset + (face_pos[i][0] + cell_pos[j][0]) * grid, y = offset + (face_pos[i][1] + cell_pos[j][1]) * grid) # 展開図の配置
        
        # バーを設置
        self.cp_ver = tkinter.StringVar(master=self.root,value="cp -> " + str(self.cube.get_state().cp))
        self.cp_ver_obj = tkinter.Label(textvariable=self.cp_ver, font=("", 15)) # 表示するテキストの設定
        self.cp_ver_obj.place(x =0, y = 350)

        self.co_ver = tkinter.StringVar(master=self.root,value='co -> ' + str(self.cube.get_state().co))
        self.co_ver_obj = tkinter.Label(textvariable=self.co_ver, font=("", 15))
        self.co_ver_obj.place(x =0, y = 375)

        self.eo_ver = tkinter.StringVar(master=self.root,value='ep -> ' + str(self.cube.get_state().ep))
        self.eo_ver_obj = tkinter.Label(textvariable=self.eo_ver,font=("", 15)) 
        self.eo_ver_obj.place(x =0, y = 400)

        self.ep_ver = tkinter.StringVar(master=self.root,value='eo -> ' + str(self.cube.get_state().eo))
        self.ep_ver_obj = tkinter.Label(textvariable=self.ep_ver,font=("", 15)) 
        self.ep_ver_obj.place(x =0, y = 425)

        self.move_log_ver = tkinter.StringVar(master=self.root,value='move_log -> ' + str(self.move_log)[1:-1])
        self.move_log_ver_obj = tkinter.Label(textvariable=self.move_log_ver,font=("", 15)) 
        self.move_log_ver_obj.place(x =0, y = 450)
        
        # テキストボックスを設置
        self.input_move = tkinter.Entry(master=self.root, width=20)
        self.input_move.place(x = 500, y = 350)

        # ボタンを設置  
        go_btn = tkinter.Button(master=self.root,text="Go",command=self.go_btn_callback)
        go_btn.place(x = 600, y = 350)
        back_btn = tkinter.Button(master=self.root,text="Back",command=self.back_btn_callback)
        back_btn.place(x = 600, y = 375)

        # GUIからキーボードの入力を受け付ける
        self.root.bind("<Escape>", self.reset_btn_callback)      
        
        self.root.mainloop() # GUIの表示

if __name__ == '__main__':
    gui = GUI()
    gui.start()