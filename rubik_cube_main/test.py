import os 
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"

import cv2 #画像認識のためにopencvをインポート
import numpy as np

path = './'

for i in range(6):
    frame = cv2.imread(path + 'frame' + str(i) + '.jpg')
    grayFrame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    frame_mean = np.array(grayFrame).flatten().mean()

    print(f"{i} : {frame_mean}", {cv2.mean(frame)})