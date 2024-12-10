# cv2のインポート前にカメラに関する設定を行う
# カメラの起動を高速化する
# https://github.com/opencv/opencv/issues/17687
import os 
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"

import cv2 #画像認識のためにopencvをインポート
import numpy as np
import keyboard
import datetime
import cube_config as config
from time import sleep

capture = cv2.VideoCapture(0)

##############################################
# opencv
# 画像の取得→色の配列['w','y','g','r','b','o']
##############################################
class Capture:
    def __init__(self, path = '.'):
        self.color_list = ['w','y','g','r','b','o'] # 色のデータとして格納する値
        self.color_map = [0,2,8,6,1,5,7,3,4] # ソート順からキューブ配列の変換キー
        self.color_min = [[config.w_h_min, config.w_s_min, config.w_v_min], 
                          [config.y_h_min, config.y_s_min, config.y_v_min],  
                          [config.g_h_min, config.g_s_min, config.g_v_min], 
                          [config.r_h_min, config.r_s_min, config.r_v_min],
                          [config.b_h_min, config.b_s_min, config.b_v_min],
                          [config.o_h_min, config.o_s_min, config.o_v_min]]
        self.color_max = [[config.w_h_max, config.w_s_max, config.w_v_max],
                          [config.y_h_max, config.y_s_max, config.y_v_max],  
                          [config.g_h_max, config.g_s_max, config.g_v_max], 
                          [config.r_h_max, config.r_s_max, config.r_v_max],
                          [config.b_h_max, config.b_s_max, config.b_v_max],
                          [config.o_h_max, config.o_s_max, config.o_v_max]]
        self.circlecolor = [(255, 255, 255), (0, 255, 255), (0, 255, 0), (0, 0, 255), (255, 0, 0), (0, 170, 255)]
        # self.capture = cv2.VideoCapture(0) # 写真を撮る
        self.color_num = [[i for _ in range(9)] for i in range(6)]
        self.save_flag = False
        self.path = path
        self.date_now = datetime.datetime.now()
        if self.path[-1] == '/': # パスの末尾は/無しに統一
            self.path = self.path[:-1]
    
    def set_date_now(self):
        self.date_now = datetime.datetime.now()

    def find_color(self, phase):
        self.save_flag = True
        while not(keyboard.is_pressed("escape")): # escapeキーが押されると中断(強制停止)
            target_colors = self.find_rect_of_target_color(phase)
            if target_colors:
                # print(target_colors)
                for i in range(9):
                    self.color_num[phase][i] = target_colors[i] # 面の色を保存
                break
        cv2.destroyAllWindows()
        return target_colors

    def find_rect_of_target_color(self, phase):
        # self.capture = cv2.VideoCapture(0) # 写真を撮る
        ret, frame = capture.read()
        if not(ret):
            return 
        frame = frame[50:-50:,50:-50] # トリミング
        grayFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # グレー画像にする
        frame_mean = np.array(grayFrame).flatten().mean()
        if frame_mean > config.white_frame: # 全体が白みがかっている画像はスキップ
            print(f"frame_mean:{frame_mean:.1f} < {config.white_frame}")
            return
        blurredFrame = cv2.blur(grayFrame, (3, 3)) # 平滑化(ノイズ除去)
        cannyFrame = cv2.Canny(blurredFrame, 20, 40, 3) # エッジ検出
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9)) # モルフォロジー演算用のカーネル生成
        dilatedFrame = cv2.dilate(cannyFrame, kernel) # エッジの膨張(線を太くして途切れた部分を繋げる)
        edge_mask = cv2.bitwise_not(cv2.cvtColor(dilatedFrame, cv2.COLOR_GRAY2RGB)) # マスク画像の生成(白黒が逆なので反転)
        masked_frame = cv2.bitwise_and(frame,edge_mask) # 元画像にマスクをかける

        hsv = cv2.cvtColor(masked_frame, cv2.COLOR_BGR2HSV_FULL) # 色空間をRGBからHSVに変更
        h = hsv[:, :, 0]
        s = hsv[:, :, 1]
        v = hsv[:, :, 2]
        rects = []
        for i in range(6):
            mask = np.zeros(h.shape, dtype=np.uint8)
            mask[(((self.color_min[i][0] <= self.color_max[i][0]) & (h >= self.color_min[i][0]) & (h <= self.color_max[i][0])) | 
                  ((self.color_min[i][0] >= self.color_max[i][0]) & ((h >= self.color_min[i][0]) | (h <= self.color_max[i][0])))) & 
                 ((s >= self.color_min[i][1]) & (s <= self.color_max[i][1])) &
                 (v >= self.color_min[i][2])] = 255
            # 領域を検出
            contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            # 一定値以上の領域の始点、終点、色番号をrectに保存
            for contour in contours:
                # 検出した領域の形式を変換
                approx = cv2.convexHull(contour)
                [x,y,width,height] = (cv2.boundingRect(approx))
                if width * height > 4000 and width * height < 20000:
                    # 検出した領域を画像に描画
                    # cv2.rectangle(frame, pt1=(x,y), pt2=(x + width, y + height), color=circlecolor[i], thickness=2)
                    # print(i, width * height) # デバッグ用　面積表示
                    rects.append([x,y,width,height,i,np.array((x+width/2,y+height/2))])
        # デバッグ用　画像表示
        dell_rect = None
        for i in range(len(rects)):
            for j in range(i + 1,len(rects)):
                dist = np.linalg.norm(rects[i][5] - rects[j][5])
                if dist < 75: # 領域の中心が近い場合、面積が大きい方を採用
                    dell_rect = j if rects[i][2]*rects[i][3] > rects[j][2]*rects[j][3] else i
        if dell_rect:
            del rects[dell_rect]
        for rect in rects:
            x,y,width,height,i,_ = rect
            cv2.rectangle(frame, pt1=(x,y), pt2=(x + width, y + height), color=self.circlecolor[i], thickness=2)
        cv2.imshow('frame'+str(phase), frame)
        # cv2.imshow("cannyFrame",cannyFrame)
        # cv2.imshow("dilatedFrame",dilatedFrame)
        # cv2.imshow("masked_frame",masked_frame)
        key = cv2.waitKey(1)
        # 見つかった領域が9個じゃなければ何も返さず終了
        if len(rects) != 9:
            print(f"find cells = {len(rects)}")
            return
        # 画像の保存
        if self.save_flag:
            # 例:20241019_frame1.jpg
            cv2.imwrite(self.path +'/'+ self.date_now.strftime('%Y%m%d_%H%M%S') +'frame'+str(phase)+'.jpg',frame)

        # 検出した領域をy座標でソート
        y_sorted = sorted(rects, key=lambda item: item[1])
        # y座標順3つごとにx座標でソート
        top_row = sorted(y_sorted[0:3], key=lambda item: item[0]) 
        middle_row = sorted(y_sorted[3:6], key=lambda item: item[0])
        bottom_row = sorted(y_sorted[6:9], key=lambda item: item[0])
        # 色番号を抜き出す
        sorted_contours = top_row + middle_row + bottom_row
        sorted_color_num = [sorted_contours[i][4] for i in range(9)]
        # ソート順配列からキューブ配列に変換
        # 0 1 2   0 4 1
        # 3 4 5 → 7 8 5
        # 6 7 8   3 6 2
        return [sorted_color_num[self.color_map[i]] for i in range(9)]
    
    def test_capture(self):
        self.save_flag = False
        while True:
            self.find_rect_of_target_color(0)
            key = cv2.waitKey(1)
            if key == config.escape_key:
                # capture.release()
                cv2.destroyAllWindows()
                break
        # self.save_flag = True

