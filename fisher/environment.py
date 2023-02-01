import numpy as np
import pyautogui
import torch

from utils import mouse_down, mouse_move, mouse_up, cap, psnr, \
    distance, match_img
import cv2
import time
from collections import Counter
import traceback
import os

from utils.config import IMAGE_PATH, IS_DIEYU

class FishFind:
    def __init__(self, predictor, show_det=True):
        self.predictor = predictor
        self.food_imgs = [
            cv2.imread(str(IMAGE_PATH / 'food_gn.png')), # 0, 1, 2, 3, 4
            cv2.imread(str(IMAGE_PATH / 'food_cm.png')),
            cv2.imread(str(IMAGE_PATH / 'food_bug.png')),
            cv2.imread(str(IMAGE_PATH / 'food_fy.png')),
        ]
        # self.food_imgs = [cv2.cvtColor(x, cv2.COLOR_BGR2RGB) for x in self.food_imgs]
        self.ff_dict = {'hua jiang': 0, 'ji yu': 1, 'die yu': 2, 'jia long': 3, 'pao yu': 3, 'yao': 3}
        self.dist_dict = {'hua jiang': 130, 'ji yu': 80, 'die yu': 80, 'jia long': 80, 'pao yu': 80, 'yao': 80}
        self.food_rgn = [580, 400, 740, 220]
        if IS_DIEYU:
            self.last_fish_type = 'die yu'
        else:
            self.last_fish_type = 'hua jiang'
        self.show_det = show_det
        os.makedirs('img_tmp/', exist_ok=True)

    def get_fish_types(self, n=12, rate=0.6):
        counter = Counter()
        fx = lambda x: int(np.sign(np.cos(np.pi * (x / (n // 2)) + 1e-4)))
        mouse_move(0, 200)
        time.sleep(0.2)
        for i in range(n):
            obj_list = self.predictor.image_det(cap())
            if obj_list is None:
                mouse_move(70 * fx(i), 0)
                time.sleep(0.2)
                continue
            cls_list = set([x[0] for x in obj_list])
            counter.update(cls_list)
            mouse_move(70 * fx(i), 0)
            time.sleep(0.2)
        fish_list = [k for k, v in dict(counter).items() if v / n >= rate]
        return fish_list

    def throw_rod(self, fish_type):
        mouse_down(960, 540)
        time.sleep(1)

        def move_func(dist):
            if dist > 100:
                return 50 * np.sign(dist)
            else:
                return (abs(dist) / 2.5 + 10) * np.sign(dist)

        for i in range(50):
            try:
                obj_list, outputs, img_info = self.predictor.image_det(cap(), with_info=True)
                if self.show_det:
                    cv2.imwrite(f'img_tmp/det{i}.png', self.predictor.visual(outputs[0], img_info))

                rod_info = sorted(list(filter(lambda x: x[0] == 'rod', obj_list)), key=lambda x: x[1], reverse=True)
                if len(rod_info) <= 0:
                    mouse_move(np.random.randint(-50, 50), np.random.randint(-50, 50))
                    time.sleep(0.1)
                    continue
                rod_info = rod_info[0]
                rod_cx = (rod_info[2][0] + rod_info[2][2]) / 2
                rod_cy = (rod_info[2][1] + rod_info[2][3]) / 2

                fish_info = min(list(filter(lambda x: x[0] == fish_type, obj_list)),
                                key=lambda x: distance((x[2][0] + x[2][2]) / 2, (x[2][1] + x[2][3]) / 2, rod_cx,
                                                       rod_cy))

                if (fish_info[2][0] + fish_info[2][2]) > (rod_info[2][0] + rod_info[2][2]):
                    # dist = -self.dist_dict[fish_type] * np.sign(fish_info[2][2] - (rod_info[2][0] + rod_info[2][2]) / 2)
                    x_dist = fish_info[2][0] - self.dist_dict[fish_type] - rod_cx
                else:
                    x_dist = fish_info[2][2] + self.dist_dict[fish_type] - rod_cx

                print(x_dist, (fish_info[2][3] + fish_info[2][1]) / 2 - rod_info[2][3])
                if abs(x_dist) < 30 and abs((fish_info[2][3] + fish_info[2][1]) / 2 - rod_info[2][3]) < 30:
                    break

                dx = int(move_func(x_dist))
                dy = int(move_func(((fish_info[2][3]) + fish_info[2][1]) / 2 - rod_info[2][3]))
                mouse_move(dx, dy)
            except Exception as e:
                traceback.print_exc()
            # time.sleep(0.3)
        mouse_up(960, 540)

    def select_food(self, fish_type):
        # pyautogui.press('f')
        # time.sleep(1)
        pyautogui.click(1650, 790, button=pyautogui.SECONDARY)
        time.sleep(0.5)
        # bbox_food = match_img(cap(self.food_rgn, fmt='RGB'), self.food_imgs[self.ff_dict[fish_type]],
        #                       type=cv2.TM_CCORR_NORMED)
        bbox_food = match_img(cap(self.food_rgn, fmt='RGB'), self.food_imgs[self.ff_dict[fish_type]],
                              type=cv2.TM_SQDIFF_NORMED)
        pyautogui.click(bbox_food[4] + self.food_rgn[0], bbox_food[5] + self.food_rgn[1])
        time.sleep(0.5)
        if np.mean(np.abs(cap(self.food_rgn)[219][739] - [48, 43, 41])) < 5:
            pyautogui.click(1300, 756)
            time.sleep(0.1)

        time.sleep(0.1)
        pyautogui.click(1300, 756)

    def do_fish(self, fish_init=True) -> bool:
        if fish_init:
            self.fish_list = self.get_fish_types()

        # return false if fish_list is empty
        if not self.fish_list:
            return False

        if self.fish_list[0] != self.last_fish_type:
            self.select_food(self.fish_list[0])
            self.last_fish_type = self.fish_list[0]
        self.throw_rod(self.fish_list[0])
        return True
