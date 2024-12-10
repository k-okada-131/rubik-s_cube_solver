import ev3_dc as ev3
from collections import namedtuple
from time import sleep
from cmd import rotate, rotate1, rotate2, reset, stop, is_pressed, run, read_color, color_off, rotate_t, lift

HOSTS = [
    '00:16:53:4F:0A:68',
    '00:16:53:50:0C:7F',
    '00:16:53:50:1F:F7',
    # '00:16:53:44:8F:C5'
    '00:16:53:4A:AB:B7'
]

Motor = namedtuple('Motor', ['brick', 'ports'])
MOVE_DEG = 125 # アームを90度回すのに必要な回転角度
TURN_DEG = 125 # アームを正確に90度回すのに必要な回転角度
ARM_DEG = 33
RELEASE = 0
GRIP = 1
PORT_A = 0
PORT_B = 1
PORT_C = 2
PORT_D = 3
WAIT_DEG = 10
EV3_MOVE1 = 0
EV3_MOVE2 = 1
EV3_ARM = 2
EV3_LIFT = 3
DELAY = 0
TURN_DELAY = 0

class Control:
    def __init__(self):
        Motor = namedtuple('Motor', ['brick', 'ports'])
        Sensor = namedtuple('Sensor', ['brick', 'ports'])
        self.MOVE_DEGS = [MOVE_DEG, (MOVE_DEG * 2), -MOVE_DEG, -(MOVE_DEG * 2)]
        self.MOVE_DEGS = [TURN_DEG, (TURN_DEG * 2), -TURN_DEG, -(TURN_DEG * 2)]
        self.ARM_DEGS = [ARM_DEG, -(ARM_DEG+2)]

        self.MOVE_MOTOR = [
            Motor(EV3_MOVE1, ev3.PORT_A + ev3.PORT_B),  
            Motor(EV3_MOVE2, ev3.PORT_A + ev3.PORT_B),  
            Motor(EV3_MOVE1, ev3.PORT_C + ev3.PORT_D),  
            Motor(EV3_MOVE2, ev3.PORT_C + ev3.PORT_D)   
        ]

        self.ARM_MOTOR = [
            Motor(EV3_ARM, ev3.PORT_A),  
            Motor(EV3_ARM, ev3.PORT_B),  
            Motor(EV3_ARM, ev3.PORT_C),  
            Motor(EV3_ARM, ev3.PORT_D)   
        ]

        self.COLOR_SENSOR = [
            Sensor(EV3_MOVE2, ev3.PORT_1),  
            Sensor(EV3_MOVE1, ev3.PORT_1),  
            Sensor(EV3_MOVE2, ev3.PORT_2),  
            Sensor(EV3_MOVE1, ev3.PORT_2)   
        ]

        self.bricks = [
            ev3.EV3(protocol=ev3.USB, host=host) for host in HOSTS
        ]
        # for i in range(len(self.bricks)):
        #     self.bricks[i].verbosity = 1
        
        # 動作の候補
        self.move_candidate = ["U1", "U2", "U3", "F1", "F2", "F3", "R1", "R2", "R3",
                               "D1", "D2", "D3", "B1", "B2", "B3", "L1", "L2", "L3"]
        self.reset()

    def __del__(self):
        self.reset()

    # 単体操作(アームの回転)
    def move(self, motor_num, deg):
        motor = self.MOVE_MOTOR[motor_num]
        waitdeg = abs(deg) - WAIT_DEG
        rotate(self.bricks[motor.brick], motor.ports, deg, waitdeg)

    # 同時操作(アームの回転、同じ角度)
    def move_inv(self, motor_num1, deg1, motor_num2, deg2):
        motor1 = self.MOVE_MOTOR[motor_num1]
        motor2 = self.MOVE_MOTOR[motor_num2]
        waitdeg = max(abs(deg1), abs(deg2)) - WAIT_DEG
        rotate1(self.bricks[motor1.brick], motor1.ports, motor2.ports, deg1, deg2, waitdeg)

    # 同時操作(アームの回転、違う角度)
    def move_inv2(self, motor_num1, deg1, motor_num2, deg2):
        motor1 = self.MOVE_MOTOR[motor_num1]
        motor2 = self.MOVE_MOTOR[motor_num2]
        waitdeg = max(abs(deg1), abs(deg2)) - WAIT_DEG
        rotate2(self.bricks[motor1.brick], motor1.ports, motor2.ports, deg1, deg2, 5, waitdeg)

    '''
    アームを閉じる際の不具合で目標角度に到達できずにモータがロックされる
    ・エンコーダの精度が悪い
    ・タイムアウト機能
        ・出来れば理想
        ・そもそもモータの操作命令がかかり続けている
        ・角度指定ではなく、指定時間動作
        ・モータは相対角度で動作
        ・指定角度動いたかどうかの判別は動作前の角度+動作する角度と現在の角度の比較
            → 目標角度に到達できないことによる待ちではなく、モータの動作命令が完了していない
            → 閉まり切らないのは相対角度で動かしたときに目標角度に到達できない
            → 初期位置がずれている
            → 開ききることが大事?
    '''
    
    def lift_up(self):
        lift(self.bricks[EV3_LIFT], ev3.PORT_A, -90*14)
        sleep(2)

    def lift_down(self):
        lift(self.bricks[EV3_LIFT], ev3.PORT_A, 90*14)
        sleep(2)

    # 単体操作(アームの開閉)
    def grip(self, motor_num, deg):
        motor = self.ARM_MOTOR[motor_num]
        waitdeg = 5
        if deg < 0:
            rotate_t(self.bricks[motor.brick], motor.ports, deg)
        else:
            rotate(self.bricks[motor.brick], motor.ports, deg, waitdeg)
    
    # 同時操作(アームの開閉、同じ角度)
    def grip_inv(self, motor_num1, motor_num2, deg):
        motor1 = self.ARM_MOTOR[motor_num1]
        motor2 = self.ARM_MOTOR[motor_num2]
        waitdeg = 5
        if deg < 0:
            rotate_t(self.bricks[motor1.brick], motor1.ports + motor2.ports, deg)
        else:
            rotate1(self.bricks[motor1.brick], motor1.ports, motor2.ports, deg, deg, waitdeg)

    # アームのリセット
    def reset(self):
        for i in range(3):
            stop(self.bricks[i], ev3.PORT_A+ev3.PORT_B+ev3.PORT_C+ev3.PORT_D)
            reset(self.bricks[i], ev3.PORT_A+ev3.PORT_B+ev3.PORT_C+ev3.PORT_D)
        print("Reset All Motors")
    
    # ボタンが押されたか
    def button_pressed(self):
        return is_pressed(self.bricks[EV3_MOVE1], ev3.PORT_4)

    def read_color(self, sensor_num):
        sensor = self.COLOR_SENSOR[sensor_num]
        return read_color(self.bricks[sensor.brick], sensor.ports)

    
    # 全てのアームで離す
    def release_all(self):
        deg = self.ARM_DEGS[RELEASE]
        waitdeg = abs(deg)
        rotate(self.bricks[EV3_ARM], ev3.PORT_A+ev3.PORT_B+ev3.PORT_C+ev3.PORT_D, deg, waitdeg)
    
    # 全てのアームで掴む
    def grip_all(self):
        deg = self.ARM_DEGS[GRIP]
        waitdeg = abs(deg)
        # rotate(self.bricks[EV3_ARM], ev3.PORT_A+ev3.PORT_B+ev3.PORT_C+ev3.PORT_D, deg, waitdeg)
        rotate_t(self.bricks[EV3_ARM], ev3.PORT_A+ev3.PORT_B+ev3.PORT_C+ev3.PORT_D, deg)
        sleep(.5)
        reset(self.bricks[EV3_ARM], ev3.PORT_A+ev3.PORT_B+ev3.PORT_C+ev3.PORT_D)


    def rotate(self, motor_num, deg):
        self.move(motor_num, deg)
        self.grip(motor_num, self.ARM_DEGS[RELEASE])
        self.move(motor_num, -deg)
        self.grip(motor_num, self.ARM_DEGS[GRIP])

    
    def rotate_inv(self, motor_num1, deg1, motor_num2, deg2):        
        if abs(deg1) != abs(deg2):
            if abs(deg2) >  abs(deg1):
                return self.rotate_inv(motor_num2, deg2, motor_num1, deg1)
            # 90°+180°のケース
            self.move_inv2(motor_num1, deg1, motor_num2, deg2)
            self.grip_inv(motor_num1, motor_num2, self.ARM_DEGS[RELEASE])
            self.move_inv2(motor_num1, -deg1, motor_num2, -deg2)
            self.grip_inv(motor_num1, motor_num2, self.ARM_DEGS[GRIP])
        else:
            self.move_inv(motor_num1, deg1, motor_num2, deg2)
            self.grip_inv(motor_num1, motor_num2, self.ARM_DEGS[RELEASE])
            self.move_inv(motor_num1, -deg1, motor_num2, -deg2)
            self.grip_inv(motor_num1, motor_num2, self.ARM_DEGS[GRIP])
        
    # AモータとCモータを回して持ち替え
    def turn_x(self, deg):
        self.grip_inv(PORT_B, PORT_D, self.ARM_DEGS[RELEASE])
        self.move_inv(PORT_A, deg, PORT_C, -deg)
        sleep(TURN_DELAY)
        self.grip_inv(PORT_B, PORT_D, self.ARM_DEGS[GRIP])
        self.grip_inv(PORT_A, PORT_C, self.ARM_DEGS[RELEASE])
        sleep(TURN_DELAY)
        self.move_inv(PORT_A, -deg, PORT_C, deg)
        self.grip_inv(PORT_A, PORT_C, self.ARM_DEGS[GRIP])
    
    # BモータとDモータを回して持ち替え
    def turn_y(self, deg):
        self.grip_inv(PORT_A, PORT_C, self.ARM_DEGS[RELEASE])
        self.move_inv(PORT_B, deg, PORT_D, -deg)
        sleep(TURN_DELAY)
        self.grip_inv(PORT_A, PORT_C, self.ARM_DEGS[GRIP])
        self.grip_inv(PORT_B, PORT_D, self.ARM_DEGS[RELEASE])
        sleep(TURN_DELAY)
        self.move_inv(PORT_B, -deg, PORT_D, deg)
        self.grip_inv(PORT_B, PORT_D, self.ARM_DEGS[GRIP])
    
    def scan(self, phase):
        # for i in range(4):
        #     sensor = self.COLOR_SENSOR[i]
        #     print(i)
        #     return read_color(self.bricks[sensor.brick], sensor.ports)
        if phase == 0:
            pass
        elif phase == 1:
            self.grip_inv(PORT_A, PORT_C, self.ARM_DEGS[RELEASE])
            self.move_inv(PORT_B, -TURN_DEG * 2, PORT_D, TURN_DEG * 2)
        elif phase == 2:
            self.move_inv(PORT_B, -TURN_DEG, PORT_D, TURN_DEG)
        elif phase == 3:
            self.grip_inv(PORT_A, PORT_C, self.ARM_DEGS[GRIP])
            sleep(DELAY)
            self.grip_inv(PORT_B, PORT_D, self.ARM_DEGS[RELEASE])
            # sleep(TURN_DELAY)
            self.move_inv(PORT_B, TURN_DEG, PORT_D, TURN_DEG)
            self.move_inv(PORT_A, -TURN_DEG, PORT_C, TURN_DEG)
        elif phase == 4:
            self.move_inv(PORT_A, -TURN_DEG, PORT_C, TURN_DEG)
        elif phase == 5:
            self.move_inv(PORT_A, -TURN_DEG, PORT_C, TURN_DEG)
        sleep(.5)
    
    def scan_finalize(self):
        self.move_inv(PORT_A, -TURN_DEG, PORT_C, TURN_DEG)
        self.grip_inv(PORT_B, PORT_D, self.ARM_DEGS[GRIP])
        sleep(DELAY)
        self.grip_inv(PORT_A, PORT_C, self.ARM_DEGS[RELEASE])
        sleep(DELAY)
        self.move_inv(PORT_B, -TURN_DEG, PORT_D, TURN_DEG)
        self.grip_inv(PORT_A, PORT_C, self.ARM_DEGS[GRIP])
        sleep(DELAY)
        self.grip_inv(PORT_B, PORT_D, self.ARM_DEGS[RELEASE])
        sleep(DELAY)
        self.move_inv(PORT_B, TURN_DEG, PORT_D, -TURN_DEG)
        self.grip_inv(PORT_B, PORT_D, self.ARM_DEGS[GRIP])

    def move_to_num(self, solution_data):
        solution_list = solution_data.split() # ' 'で文字列を分割
        rot_num = [self.move_candidate.index(i[:2]) if len(i) > 2 else self.move_candidate.index(i) for i in solution_list] # 回転記号から番号へ
        rot_num2 = [self.move_candidate.index(i[2:]) if len(i) > 2 else -1 for i in solution_list] # 対面の回転記号から番号へ
        return rot_num, rot_num2 # 変換した番号の配列を返す

    '''
    動作のオーバーラップ
    今回の動作と次回の動作の組み合わせ以下
    ・横面
    ・対面
    ・操作不可(持ち替えが必要)面
    組み合わせごとのオーバーラップは以下
    ・横面
    A 回転 | 開く | 回転 | 閉じ 
    B             | 回転 | 開く
    ・対面
    A 回転 | 開く | 回転 | 閉じ
    C 回転 | 開く | 回転 | 閉じ
    //持ち替えの直前手は持ち替え時の動作面を垂直位置に揃える必要ありとする
    ・操作不可面(直前の操作面と持ち替え動作面が同じ)
           持ち替え開始                       持ち替え終了
           ↓                                  ↓
    A 回転 | 開く | 回転 | 閉じ |             | 回転 | 
    C      | 開く |      | 閉じ |
    B             | 回転 | 開く | 回転 | 閉じ |
    D             | 回転 | 開く | 回転 | 閉じ |
    ・操作不可面(直前の操作面と持ち替え動作面が違う) 
                         持ち替え開始                       持ち替え終了
                         ↓                                  ↓    
    A 回転 | 開く | 回転 | 閉じ | 回転 | 開く | 回転 | 閉じ |     
    C                           | 回転 | 開く | 回転 | 閉じ |
    B                    | 開く |      | 閉じ |             | 回転 |
    D                    | 開く |      | 閉じ |             
    
    -> 直前の操作面と持ち替え動作面が同じ場合、持ち替え前のセットアップが不要になるため短い
    '''


    def execute(self, solution, direction):
        # ans = [] # 回転番号の配列のリセット
        # ans2 = []
        # ans, ans2 = self.move_to_num(solution) # 文字列から回転番号の配列へ
        # rot = [] # 操作の配列のリセット
        # ans_hlf = len(ans)//2 # 解の長さの半分(切り捨て)
        # ans_first = ans[0:ans_hlf] # 前半
        # ans2_first = ans2[0:ans_hlf]
        # ans_last = ans[ans_hlf:len(ans)] # 後半
        # ans2_last = ans2[ans_hlf:len(ans2)]
        # rot_tmp, _, direction, _, _ = self.proc_motor(rot, 0, direction, ans_first, ans2_first) # 前半の最適手順をrot配列(空配列)に追加
        # rot, _, _, _, _ = self.proc_motor(rot_tmp, 0, direction, ans_last, ans2_last) # 後半の最適手順を前半に追加
        rot = self.optimize_motor(solution, direction)
        for i in range(len(rot)): # rot分だけ回す
            if len(rot[i]) > 3:
                self.rotate_inv(rot[i][0], rot[i][1], rot[i][2], rot[i][3])
            else:
                if rot[i][0] < 4: # [i][_]が0~3ならキューブを回す
                    self.rotate(rot[i][0], rot[i][1])
                elif rot[i][0] == 4: # [i][_]が4なら左<->右持ち替え
                    self.turn_x(rot[i][1])
                elif rot[i][0] == 5: # [i][_]が5なら上<->下持ち替え
                    self.turn_y(rot[i][1]) 
            sleep(DELAY)
            # print(f"[{self.read_color(0)}, {self.read_color(1)}, {self.read_color(2)}, {self.read_color(3)}]")
    
    def test_execute(self, solution, direction):
        # ans = [] # 回転番号の配列のリセット
        # ans2 = []
        # ans, ans2 = self.move_to_num(solution) # 文字列から回転番号の配列へ
        # rot = [] # 操作の配列のリセット
        # ans_hlf = len(ans)//2 # 解の長さの半分(切り捨て)
        # ans_first = ans[0:ans_hlf] # 前半
        # ans2_first = ans2[0:ans_hlf]
        # ans_last = ans[ans_hlf:len(ans)] # 後半
        # ans2_last = ans2[ans_hlf:len(ans2)]
        # rot_tmp, _, direction, _, _ = self.proc_motor(rot, 0, direction, ans_first, ans2_first) # 前半の最適手順をrot配列(空配列)に追加
        # rot, _, _, _, _ = self.proc_motor(rot_tmp, 0, direction, ans_last, ans2_last) # 後半の最適手順を前半に追加
        rot = self.optimize_motor(solution, direction)
        for i in range(len(rot)): # rot分だけ回す
            if len(rot[i]) > 3:
                self.rotate_inv(rot[i][0], rot[i][1], rot[i][2], rot[i][3])
            else:
                if rot[i][0] < 4: # [i][_]が0~3ならキューブを回す
                    self.rotate(rot[i][0], rot[i][1])
                    # sleep(DELAY)
                    # self.arm_setup(rot[i][0])
                elif rot[i][0] == 4: # [i][_]が4なら左<->右持ち替え
                    self.turn_x(rot[i][1])
                    # # sleep(DELAY)
                    # self.arm_setup(0)
                    # self.arm_setup(2)
                elif rot[i][0] == 5: # [i][_]が5なら上<->下持ち替え
                    self.turn_y(rot[i][1]) 
                    # # sleep(DELAY)
                    # self.arm_setup(1)
                    # self.arm_setup(3)
            sleep(DELAY)
            # self.arm_setup()
            while not(self.button_pressed()):
                pass

    def optimize_motor(self, solution, direction):
        # ans = [] # 回転番号の配列のリセット
        # ans2 = []
        ans, ans2 = self.move_to_num(solution) # 文字列から回転番号の配列へ
        rot = [] # 操作の配列のリセット
        ans_hlf = len(ans)//2 # 解の長さの半分(切り捨て)
        ans_first, ans2_first = ans[0:ans_hlf], ans2[0:ans_hlf] # 前半
        ans_last, ans2_last = ans[ans_hlf:len(ans)], ans2[ans_hlf:len(ans2)] # 後半
        rot_tmp, _, direction, _, _ = self.proc_motor(rot, 0, direction, ans_first, ans2_first) # 前半の最適手順をrot配列(空配列)に追加
        rot, _, _, _, _ = self.proc_motor(rot_tmp, 0, direction, ans_last, ans2_last) # 後半の最適手順を前半に追加
        return rot

    # 回転記号番号の配列から回すモーターを決定
    def proc_motor(self, rot, num, direction, ans, ans2):
        if num == len(ans):# 全て変換したか
            return rot, num, direction, ans,ans2 # 最終的な解を返す
        # 移動量の配列 90° 180° -90°
        turn_arr = [1, 2, -1]
        ##############################
        # 以下 w:0,g:1,r:2,y:3,b:4,o:5
        ##############################
        # u面をもとにしたあり得るf面の配列
        f_arr = [[1, 2, 4, 5], [3, 2, 0, 5], [3, 4, 0, 1], [4, 2, 1, 5], [3, 5, 0, 2], [3, 1, 0, 4]]
        # f,u面をもとにしたr面の配列,-1はあり得ない面
        r_arr = [[-1, 2, 4, -1, 5, 1], [5, -1, 0, 2, -1, 3], [1, 3, -1, 4, 0, -1], [-1, 5, 1, -1, 2, 4], [2, -1, 3, 5, -1, 0], [4, 0, -1, 1, 3, -1]]
        # 方向の候補配列 //4 上面 %4正面
        regrip_arr = [[21, 5, 9, 17, 20, 13, 10, 3, 4, 12, 18, 0, 23, 19, 11, 7, 8, 15, 22, 1, 16, 14, 6, 2],
                    [4, 8, 16, 20, 12, 9, 2, 23, 15, 17, 3, 7, 18, 10, 6, 22, 14, 21, 0, 11, 13, 5, 1, 19]]
        # 持ち替え手順(4:0と2,左から右 5:1と3 手前から奥)
        regrip_rot = [[[4, TURN_DEG]], [[5, TURN_DEG]]]
        u_face = direction // 4 # 上面どの面が向いてるか
        f_face = f_arr[u_face][direction % 4] # 正面どの面が向いてるか
        r_face = r_arr[u_face][f_face] # 右面どの面が向いてるか
        d_face = (u_face + 3) % 6 # 下面 対面を引く
        b_face = (f_face + 3) % 6 # 後ろ面 対面を引く
        l_face = (r_face + 3) % 6 # 左面 対面を引く
        move_able = [f_face, r_face, b_face, l_face] # 回すことが可能な面
        #デフォルト
        #    B:2
        # L:3   R:1
        #    F:0
        move_face = ans[num] // 3 #動かしたい面(0:U,1:F,2;R,3:D,4:B,5:L)
        if move_face == u_face or move_face == d_face: #動かしたい面が上または下面にある
            rot_tmp = [[i for i in rot] for _ in range(2)] #rotを二つ作る rot_tmp = [rot,rot]
            direction_tmp = [-1, -1] # 方向を一時保存する配列
            num_tmp = [num, num] # 何手目の操作か一時保存する変数
            for j in range(2): # 2通りの持ち替えを試す
                rot_tmp[j].extend(regrip_rot[j]) # 操作配列にx方向とy方向の持ち替えの配列を結合
                direction_tmp[j] = regrip_arr[j][direction] # 方向を保存
                rot_tmp[j], num_tmp[j], direction_tmp[j], _, _ = self.proc_motor(rot_tmp[j], num_tmp[j], direction_tmp[j], ans, ans2) # 再帰
            idx = 0 if len(rot_tmp[0]) < len(rot_tmp[1]) else 1 #長い方(操作できる方)を選択
            rot_res = rot_tmp[idx]
            num_res = num_tmp[idx]
            direction_res = direction_tmp[idx]
        else: # 動かしたい面が動かせる
            move_amount = turn_arr[ans[num] % 3] #移動量の決定
            move_amount2 = turn_arr[ans2[num] % 3]
            tmp = move_able.index(move_face) # 動かしたい面が何番目のモータにあるのか
            rot_res = [i for i in rot]
            if ans2[num] >= 0: # 同時操作の場合
                rot_res.append([tmp, move_amount * MOVE_DEG,(tmp+2)%4, move_amount2 * MOVE_DEG]) # モーター番号と移動量を保存
            else: # 同時操作じゃない場合
                rot_res.append([tmp, move_amount * MOVE_DEG]) # モーター番号と移動量を保存
            rot_res, num_res, direction_res, _, _ = self.proc_motor(rot_res, num + 1, direction, ans, ans2) # 次の移動の再帰
        return rot_res, num_res, direction_res, ans, ans2 # 再帰で返す用

    def run(self, m, pow):
        motor = self.MOVE_MOTOR[m]
        run(self.bricks[motor.brick], motor.ports, pow)

    def arm_setup(self):
        reset(self.bricks[EV3_ARM], ev3.PORT_A+ev3.PORT_B+ev3.PORT_C+ev3.PORT_D)
        for port_num in range(len(self.MOVE_DEGS)):
            self.grip(port_num, self.ARM_DEGS[RELEASE])
            motor = self.MOVE_MOTOR[port_num]
            pow_list = [15, -15, 10, -10]
            clr_list = [[40, 40, 60, 60], [40, 40, 60, 60],[40, 40, 60, 60], [40, 40, 60, 60]]
            for idx, pow in enumerate(pow_list):
                while self.read_color(port_num) < clr_list[port_num][idx]:
                    run(self.bricks[motor.brick], motor.ports, pow)
                stop(self.bricks[motor.brick], motor.ports)
            self.grip(port_num, self.ARM_DEGS[GRIP])
    
    # def arm_setup(self, port_num):
    #     reset(self.bricks[EV3_ARM], ev3.PORT_A+ev3.PORT_B+ev3.PORT_C+ev3.PORT_D)
    #     if self.read_color(port_num) < 20:
    #         self.grip(port_num, self.ARM_DEGS[RELEASE])
    #         # motor = self.MOVE_MOTOR[port_num]
    #         # while self.read_color(port_num) < 60:
    #         #     run(self.bricks[motor.brick], motor.ports, 10)
    #         # stop(self.bricks[motor.brick], motor.ports)
    #         self.grip(port_num, self.ARM_DEGS[GRIP])


if __name__ == "__main__":
    ans = "U3 B3 R2L3 U3 R1L2 D3 R3 F1 U1D3 R2L2 D1 L2 D3 F2 U3 F2B2 U2D3 L2 "

    control = Control()
    control.reset()

    # rot = control.optimize_motor(ans, 0)
    # print(f"{len(ans.split() )} -> {len(rot)}")
    while True:
        if(control.button_pressed()):
            print("pressed!")
            # for i in range(4):
            #     control.arm_setup(i)
            
            control.grip_all()
            control.lift_down()
            # sleep(1)
            while not(control.button_pressed()):
                pass
            # control.arm_setup()
            control.execute(ans, 0)
            control.lift_up()
            control.release_all()
            sleep(3)
        control.reset()
