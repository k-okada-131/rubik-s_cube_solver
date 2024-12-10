class Transform:
    def __init__(self):
        self.color_list = ['w','y','g','r','b','o']
        self.corner_parts_color = [['w', 'b', 'o'], ['w', 'r', 'b'], ['w', 'g', 'r'], ['w', 'o', 'g'], 
                    ['y', 'o', 'b'], ['y', 'b', 'r'], ['y', 'r', 'g'], ['y', 'g', 'o']]
        # 各エッジパーツの色
        self.edge_parts_color = [['b', 'o'], ['b', 'r'], ['g', 'r'], ['g', 'o'], 
                            ['w', 'b'], ['w', 'r'], ['w', 'g'], ['w', 'o'],
                            ['y', 'b'], ['y', 'r'], ['y', 'g'], ['y', 'o']]
        # コーナーパーツの場所の候補
        self.cp_coordinate = [[[0,0],[4,1],[5,0]],[[0,1],[3,1],[4,0]],[[0,2],[2,1],[3,0]],[[0,3],[5,1],[2,0]],
                            [[1,3],[5,3],[4,2]],[[1,2],[4,3],[3,2]],[[1,1],[3,3],[2,2]],[[1,0],[2,3],[5,2]]]
        # コーナーパーツの向きの候補
        self.co_coordinate = [[0,0],[0,1],[0,2],[0,3],
                            [1,3],[1,2],[1,1],[1,0]]
        # エッジパーツの場所の候補
        self.ep_coordinate = [[[4,5],[5,7]],[[4,7],[3,5]],[[2,5],[3,7]],[[2,7],[5,5]],
                            [[0,4],[4,4]],[[0,5],[3,4]],[[0,6],[2,4]],[[0,7],[5,4]],
                            [[1,6],[4,6]],[[1,5],[3,6]],[[1,4],[2,6]],[[1,7],[5,6]]]
        # エッジパーツの向きの候補
        self.eo_coordinate = [[4,5],[4,7],[2,5],[2,7],
                        [0,4],[0,5],[0,6],[0,7],
                        [1,6],[1,5],[1,4],[1,7]]


    def gen_color_num(self, input_color_num):
        color_num_tmp = input_color_num.copy()
        # 撮影順配置から基準の配置の配列を取得
        #       白(0) 
        # 橙(5) 緑(2) 赤(3) 青(4)
        #       黄(1) ()内の数字:中央(8番目の要素)の色番号
        # 展開図上の横にスライド、縦でスライドで配列操作
        # 横スライド(右から左が正)、0:90、1:-90、2~5:2←3←4←5
        # 縦スライド(下から上が正)、0←2←1←4(4のみ180度反転)、3:90、5:-90

        # 白が(0,1,2,3,4,5)面にあると(0,0,0,1,2,3)回横スライド->白を012に
        white_center_list = [0,0,0,1,2,3]
        color_num_tmp = self.turn_x(color_num_tmp, white_center_list[self.find_color_low(color_num_tmp,0)])
        # 白が(0,1,2)面にある(0,2,1)縦スライド->白を0に
        white_up_list = [0,2,1,0,0,0]
        color_num_tmp = self.turn_y(color_num_tmp, white_up_list[self.find_color_low(color_num_tmp,0)])
        # 緑が(2,3,4,5)面にある(0,1,2,3)横スライド->2-5面を揃える
        green_front_list = [0,0,0,1,2,3]
        color_num_tmp = self.turn_x(color_num_tmp, green_front_list[self.find_color_low(color_num_tmp,2)])

        # キューブの向き(0~23までの数字)を計算
        # w:0,g:1,r:2,y:3,b:4,o:5
        cube_direction_list = [0,3,1,2,4,5]
        f_list = [[1, 2, 4, 5], [3, 2, 0, 5], [3, 4, 0, 1], [4, 2, 1, 5], [3, 5, 0, 2], [3, 1, 0, 4]]
        u_num = cube_direction_list[input_color_num[0][8]]
        f_num = cube_direction_list[input_color_num[2][8]]
        direction = u_num * 4 + f_list[u_num].index(f_num)

        return color_num_tmp, direction

    def num_to_str(self, color_num_list):
        return [[self.color_list[color_num_list[i][j]] for j in range(8)]for i in range(6)]


    # 引数の色番号の面が何番の面にあるか
    def find_color_low(self, input_color_num,color_num):
        center_color_list = []
        for i in range(6):
            center_color_list.append(input_color_num[i][8])
        return center_color_list.index(color_num)


    # 横スライド(右から左が正)、move_value = 0:90、1:-90、2~5:2←3←4←5
    def turn_x(self, input_color_num,move_value):
        new_color_num = [[i for _ in range(9)] for i in range(6)]
        new_color_num[0] = self.face_move(input_color_num[0],move_value)
        new_color_num[1] = self.face_move(input_color_num[1],-1 * move_value)
        for i in range(2,6):
            new_color_num[(i - 2 - move_value) % 4 + 2] = input_color_num[i]
        return new_color_num


    # 縦スライド(下から上が正)、move_value = 0←2←1←4(4のみ180度反転)、3:90、5:-90
    def turn_y(self, input_color_num,move_value):
        new_color_num = input_color_num.copy()
        new_color_num[3] = self.face_move(input_color_num[3],move_value)
        new_color_num[5] = self.face_move(input_color_num[5],-1 * move_value)
        if move_value == 1:
            new_color_num[0] = input_color_num[2]
            new_color_num[1] = self.face_move(input_color_num[4],2)
            new_color_num[2] = input_color_num[1]
            new_color_num[4] = self.face_move(input_color_num[0],2)
        elif move_value == 2:
            new_color_num[0] = input_color_num[1]
            new_color_num[1] = input_color_num[0]
            new_color_num[2] = self.face_move(input_color_num[4],2)
            new_color_num[4] = self.face_move(input_color_num[2],2)
        return new_color_num


    # 面を回転させる
    def face_move(self, tmp_color_num,move_value):
        new_color_num = tmp_color_num.copy()
        for i in range(8):
            new_pos = (i + move_value) % 4
            if i > 3:
                new_pos += 4
            new_color_num[new_pos] = tmp_color_num[i]
        return new_color_num

    # 色のデータからルービックキューブの状態配列を生成
    def taransform(self, colors_data):
        for colors_str in colors_data:
            print(colors_str)
        cp_tmp = [0] * 8
        co_tmp = [0] * 8
        ep_tmp = [0] * 12
        eo_tmp = [0] * 12
        # cp配列に変換
        for i in range(8):
            for j in range(8):
                flag = True
                for k in range(3):
                    for l in range(3):
                        # 角に面する3箇所の色が完全一致の場合のみflagがTrue
                        if not (self.corner_parts_color[j][k] == colors_data[self.cp_coordinate[i][l][0]][self.cp_coordinate[i][l][1]]):
                            flag = False
                        else:
                            flag = True
                            break
                    if not flag:
                        break
                if flag:
                    #何番目に何番のパーツが入っているか
                    cp_tmp[i] = j
        # co配列に変換
        for i in range(8):
            for j in range(3):
                # 基準面(白or黄色の面の色を確認,その面の色で向きを確認)
                if self.corner_parts_color[cp_tmp[i]][j] == colors_data[self.co_coordinate[i][0]][self.co_coordinate[i][1]]:
                    co_tmp[i] = j
                    break
            # co_tmp[i] = corner_parts_color[cp_tmp[i]].index(colors_data[co_coordinate[i][0]][co_coordinate[i][1]])
        # ep配列に変換
        for i in range(12):
            for j in range(12):
                flag = True
                for k in range(2):
                    for l in range(2):
                        if not (self.edge_parts_color[j][k] == colors_data[self.ep_coordinate[i][l][0]][self.ep_coordinate[i][l][1]]):
                            flag = False
                        else:
                            flag = True
                            break
                    if not flag:
                        break
                if flag:
                    ep_tmp[i] = j
        # eo配列に変換
        for i in range(12):
            for j in range(2):
                if self.edge_parts_color[ep_tmp[i]][j] == colors_data[self.eo_coordinate[i][0]][self.eo_coordinate[i][1]]:
                    eo_tmp[i] = j
                    break
        # cpの配列の確認(cpに0~7がすべて含まれているか)
        for i in range(8):
            if not (i in cp_tmp):
                print("cp errpr")
                return None
        # coの配列の確認(coの合計が3の倍数か)
        if not (sum(co_tmp) % 3 == 0):
            print("co errpr")
            return None
        # epの配列の確認(epに0~11がすべて含まれているか)
        for i in range(12):
            if not (i in ep_tmp):
                print("ep errpr")
                return None
        # eoの配列の確認(eoの合計が2の倍数か)
        if not (sum(eo_tmp) % 2 == 0):
            print("eo errpr")
            return None 

        return [cp_tmp, co_tmp, ep_tmp, eo_tmp]
