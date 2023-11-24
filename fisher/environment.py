import numpy as np
import pyautogui

from utils import mouse_click, mouse_down, mouse_move, mouse_up, cap, distance, match_img
import cv2
import time
from collections import Counter
import traceback
import os

from utils.config import config, IMAGE_PATH, GAME_WIDTH, GAME_HEIGHT


class FishFind:
    def __init__(self, predictor, show_det=True):
        """
        初始化垂钓类的实例。
        :param predictor: 用于垂钓场景检测的预测器。
        :param show_det (bool): 是否显示检测结果的标志。

        :attributes:
            - predictor: 用于垂钓场景检测的预测器。
            - food_imgs (list): 包含不同鱼饵图像的列表。
            - ff_dict (dict): 将鱼的类型映射到对应鱼饵索引的字典。
            - dist_dict (dict): 鱼漂落点偏移量的字典。
            - food_rgn (list): 食物区域的坐标范围。
            - last_fish_type (str): 上一次使用的鱼的类型。
            - show_det (bool): 是否显示检测结果的标志。
        """
        self.predictor = predictor

        # 预加载不同鱼饵的图像
        self.food_imgs = [
            cv2.imread(str(IMAGE_PATH / 'food_gn.png')),  # 果酿饵：0
            cv2.imread(str(IMAGE_PATH / 'food_cm.png')),  # 赤糜饵：1
            cv2.imread(str(IMAGE_PATH / 'food_bug.png')),  # 蠕虫假饵：2
            cv2.imread(str(IMAGE_PATH / 'food_fy.png')),  # 飞蝇假饵：3
            cv2.imread(str(IMAGE_PATH / 'food_gl.png')),  # 甘露饵：4
        ]

        # 将鱼的类型映射到对应鱼饵索引的字典
        self.ff_dict = {
            'hua jiang': 0,
            'ji yu': 1,
            'die yu': 2,
            'jia long': 3,
            'pao yu': 3,
            'yao yu': 3,
            'qiang yu': 4,
            'jiao tun': 4,
        }

        # 鱼漂落点偏移量的字典
        self.dist_dict = {
            'hua jiang': 130,
            'ji yu': 80,
            'die yu': 80,
            'jia long': 80,
            'pao yu': 80,
            'yao yu': 80,
            'qiang yu': 80,
            'jiao tun': 80,
        }

        # 食物区域的坐标范围
        self.food_rgn = [580, 400, 740, 220]

        # 上一次使用的鱼的类型，默认为 'hua jiang'
        if config.is_dieyu:
            self.last_fish_type = 'die yu'
        else:
            self.last_fish_type = 'hua jiang'

        # 是否显示检测结果的标志
        self.show_det = show_det

        # 创建用于保存检测结果图片的目录
        os.makedirs('img_tmp/', exist_ok=True)


    def get_fish_types(self, n=12, rate=0.6):
        """
        获取垂钓场景中鱼的类型列表。
        :param n : 在水平方向上移动的次数，用于扫描鱼的类型。
        :param rate : 判定一种鱼是否存在的阈值，如果出现的次数占比超过这个阈值，则被认为是有效的鱼类。
        :return: 包含垂钓场景中有效鱼类类型的列表。

        :notes:
            - 该方法通过模拟鼠标在水平方向上的移动，扫描不同位置的垂钓场景，统计各种鱼类的出现次数。
            - 返回的鱼类列表是根据出现频率排序的，只包含出现次数占比超过阈值的鱼类。
        """
        counter = Counter()

        # 定义函数 fx 用于确定鼠标水平方向上的移动方向
        fx = lambda x: int(np.sign(np.cos(np.pi * (x / (n // 2)) + 1e-4)))

        # 移动鼠标并扫描鱼的类型
        mouse_move(0, 200)
        time.sleep(0.2)
        for i in range(n):
            obj_list = self.predictor.image_det(cap())

            # 如果没有检测到对象，移动鼠标并继续
            if obj_list is None:
                mouse_move(70 * fx(i), 0)
                time.sleep(0.2)
                continue

            # 统计各种鱼类的出现次数
            cls_list = set([x[0] for x in obj_list])
            counter.update(cls_list)

            # 移动鼠标到下一个位置
            mouse_move(70 * fx(i), 0)
            time.sleep(0.2)

        # 根据出现次数占比筛选有效鱼类并返回
        fish_list = [k for k, v in dict(counter).items() if v / n >= rate]
        return fish_list

    def throw_rod(self, fish_type):
        # 在抛竿前等待一小段时间
        time.sleep(0.5)

        # 模拟鼠标点击开始垂钓
        mouse_down(int(GAME_WIDTH / 2), int(GAME_HEIGHT / 2))
        time.sleep(1)  # 在抛竿后等待一会儿

        # 定义一个函数，根据与目标的距离确定鼠标移动距离
        def move_func(dist):
            if dist > 100:
                return 50 * np.sign(dist)
            else:
                return (abs(dist) / 2.5 + 10) * np.sign(dist)

        # 限定次数的循环（50次）
        for i in range(50):
            try:
                # 使用预测器检测垂钓场景中的对象
                obj_list, outputs, img_info = self.predictor.image_det(cap(), with_info=True)

                # 可选：将检测结果保存到文件以进行调试
                if self.show_det:
                    cv2.imwrite(f'img_tmp/det{i}.png', self.predictor.visual(outputs[0], img_info))

                # 提取场景中垂钓竿的信息
                rod_info = sorted(list(filter(lambda x: x[0] == 'rod', obj_list)), key=lambda x: x[1], reverse=True)

                # 如果未检测到垂钓竿，随机移动鼠标并继续循环
                if len(rod_info) <= 0:
                    mouse_move(np.random.randint(-50, 50), np.random.randint(-50, 50))
                    time.sleep(0.1)
                    continue

                rod_info = rod_info[0]
                rod_cx = (rod_info[2][0] + rod_info[2][2]) / 2
                rod_cy = (rod_info[2][1] + rod_info[2][3]) / 2

                # 根据类型找到目标鱼
                fish_info = min(
                    list(filter(lambda x: x[0] == fish_type, obj_list)),
                    key=lambda x: distance((x[2][0] + x[2][2]) / 2, (x[2][1] + x[2][3]) / 2, rod_cx, rod_cy),
                )

                # 计算垂钓竿与目标鱼之间的水平距离
                if (fish_info[2][0] + fish_info[2][2]) > (rod_info[2][0] + rod_info[2][2]):
                    x_dist = fish_info[2][0] - self.dist_dict[fish_type] - rod_cx
                else:
                    x_dist = fish_info[2][2] + self.dist_dict[fish_type] - rod_cx

                # 打印水平和垂直距离以进行调试
                print(x_dist, (fish_info[2][3] + fish_info[2][1]) / 2 - rod_info[2][3])

                # 检查鼠标是否足够接近目标
                if abs(x_dist) < 30 and abs((fish_info[2][3] + fish_info[2][1]) / 2 - rod_info[2][3]) < 30:
                    break  # 如果鼠标足够接近目标，则退出循环

                # 根据定义的函数计算移动距离
                dx = int(move_func(x_dist))
                dy = int(move_func(((fish_info[2][3]) + fish_info[2][1]) / 2 - rod_info[2][3]))

                # 根据计算的距离移动鼠标
                mouse_move(dx, dy)
            except Exception as e:
                # 可选：处理异常或打印跟踪以进行调试
                # traceback.print_exc()
                pass

        # 在循环后释放鼠标点击
        mouse_up(int(GAME_WIDTH / 2), int(GAME_HEIGHT / 2))

    # def select_food(self, fish_type):
    #     # 模拟右键点击
    #     pyautogui.click(button=pyautogui.SECONDARY)
    #     time.sleep(0.5)

    #     # 在食物区域中匹配指定类型的食物图像
    #     bbox_food = match_img(cap(self.food_rgn, fmt='RGB'), self.food_imgs[self.ff_dict[fish_type]], type=cv2.TM_SQDIFF_NORMED)
    #     img = cap(self.food_rgn, fmt='RGB')
    #     print(bbox_food)
    #     print("点击位置", bbox_food[4] + self.food_rgn[0], bbox_food[5] + self.food_rgn[1])

    #     # 在图像上标记匹配位置
    #     cv2.circle(img, (bbox_food[4], bbox_food[5]), 1, (0, 255, 0), 4)
    #     cv2.imwrite('out.png', img)
    #     print(bbox_food[4], bbox_food[5])
    #     print(self.food_rgn[0], self.food_rgn[1])

    #     # 模拟点击匹配位置
    #     # pyautogui.click(bbox_food[4], bbox_food[5])
    #     time.sleep(0.5)
    #     pyautogui.click(int(GAME_WIDTH / 2), int(GAME_HEIGHT / 2))

    #     # 如果检测到需要放下鱼饵的情况，模拟点击放下鱼饵
    #     if np.mean(np.abs(cap(self.food_rgn)[219][739] - [48, 43, 41])) < 5:
    #         pyautogui.click(1330, 860)
    #         time.sleep(0.1)

    #     time.sleep(0.1)

    #     # 模拟点击确定
    #     pyautogui.click(1330, 860)

    def select_food(self, fish_type):
        pyautogui.click(button=pyautogui.SECONDARY)
        time.sleep(0.5)
        img=cap(self.food_rgn, fmt='RGB')
        bbox_food = match_img(img, self.food_imgs[self.ff_dict[fish_type]], type=cv2.TM_SQDIFF_NORMED)
        mouse_click(bbox_food[4]+self.food_rgn[0], bbox_food[5]+self.food_rgn[1])

        # 如果检测到需要放下鱼饵的情况，模拟点击放下鱼饵
        time.sleep(1)
        print(np.abs(cap(self.food_rgn)[100][400] - [216, 229, 236]))
        print(np.abs(cap(self.food_rgn)[140][590]))
        print(np.mean(np.abs(cap(self.food_rgn)[100][400] - [216, 229, 236])))
        # if np.mean(np.abs(cap(self.food_rgn)[219][739] - [48, 43, 41])) < 5:
        if np.mean(np.abs(cap(self.food_rgn)[100][400] - [216, 229, 236])) < 5:
            pyautogui.click(1380, 820)
            time.sleep(0.1)
        time.sleep(0.5)
        pyautogui.click(1380, 820)

    def do_fish(self, fish_init=True) -> bool:
        # 如果是首次垂钓，获取可垂钓的鱼的类型列表
        if fish_init:
            self.fish_list = self.get_fish_types()

        # 如果鱼的类型列表为空，返回 False
        if not self.fish_list:
            return False

        # 如果当前垂钓的鱼的类型与上一次不同，选择对应的鱼饵
        if self.fish_list[0] != self.last_fish_type:
            self.select_food(self.fish_list[0])
            self.last_fish_type = self.fish_list[0]

        # 进行垂钓操作
        self.throw_rod(self.fish_list[0])
        return True

