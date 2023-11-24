import cv2
import time
import argparse
import numpy as np
import win32api, win32con, win32gui, win32ui

from utils.config import GAME_HEIGHT, GAME_WIDTH, config

MOUSE_LEFT = 0
MOUSE_MID = 1
MOUSE_RIGHT = 2

mouse_list_down = [win32con.MOUSEEVENTF_LEFTDOWN, win32con.MOUSEEVENTF_MIDDLEDOWN, win32con.MOUSEEVENTF_RIGHTDOWN]
mouse_list_up = [win32con.MOUSEEVENTF_LEFTUP, win32con.MOUSEEVENTF_MIDDLEUP, win32con.MOUSEEVENTF_RIGHTUP]

gvars = argparse.Namespace()
hwnd = win32gui.FindWindow(None, config.window_name)
gvars.genshin_window_rect = win32gui.GetWindowRect(hwnd)
gvars.genshin_window_rect_img = (11, 45, GAME_WIDTH, GAME_HEIGHT)


def cap(region=None, fmt='RGB'):
    """
    获取游戏窗口区域的屏幕截图。
    :param region: 指定截图区域的左上角和右下角坐标 (left, top, right, bottom)。如果为 None，则截取整个游戏窗口。
    :param fmt: 指定返回图像的颜色格式 ('RGB' 或 'BGR')，默认为 'RGB'。
    :return: 屏幕截图的图像数据。
    """
    return cap_raw(
        gvars.genshin_window_rect_img
        if region is None
        else (region[0] + gvars.genshin_window_rect_img[0], region[1] + gvars.genshin_window_rect_img[1], region[2], region[3]),
        fmt=fmt,
    )


def cap_raw(region=None, fmt='RGB'):
    """
    获取指定区域的屏幕截图。
    :param region: 指定截图区域的左上角和右下角坐标 (left, top, right, bottom)。如果为 None，则使用默认的游戏窗口大小和位置。

    :param fmt: 指定返回图像的颜色格式 ('RGB' 或 'BGR')，默认为 'RGB'。


    :return: 屏幕截图的图像数据。
    """
    if region is not None:
        left, top, w, h = region
    else:
        w = GAME_WIDTH
        h = GAME_HEIGHT
        left = 11
        top = 45

    hwnd = win32gui.FindWindow(None, config.window_name)
    wDC = win32gui.GetWindowDC(hwnd)
    dcObj = win32ui.CreateDCFromHandle(wDC)
    cDC = dcObj.CreateCompatibleDC()
    dataBitMap = win32ui.CreateBitmap()

    dataBitMap.CreateCompatibleBitmap(dcObj, w, h)

    cDC.SelectObject(dataBitMap)
    cDC.BitBlt((0, 0), (w, h), dcObj, (left, top), win32con.SRCCOPY)
    signedIntsArray = dataBitMap.GetBitmapBits(True)
    img = np.fromstring(signedIntsArray, dtype="uint8")
    img.shape = (h, w, 4)

    # Free Resources
    dcObj.DeleteDC()
    cDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, wDC)
    win32gui.DeleteObject(dataBitMap.GetHandle())

    if fmt == 'BGR':
        return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGBA2BGR)
    if fmt == 'RGB':
        return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGBA2RGB)
    else:
        raise ValueError('Cannot indetify this fmt')



def mouse_down(x, y, button=MOUSE_LEFT):
    """
    模拟鼠标按下事件。
    :param x: 鼠标按下位置的 x 坐标
    :param y: 鼠标按下位置的 y 坐标
    :param button: 鼠标按钮 (MOUSE_LEFT, MOUSE_RIGHT, MOUSE_MIDDLE)，默认为 MOUSE_LEFT
    """
    time.sleep(0.1)
    xx, yy = x + gvars.genshin_window_rect[0], y + gvars.genshin_window_rect[1]
    win32api.SetCursorPos((xx, yy))
    win32api.mouse_event(mouse_list_down[button], xx, yy, 0, 0)


def mouse_move(dx, dy):
    """
    模拟鼠标移动事件。
    :param dx: 鼠标水平移动的距离
    :param dy: 鼠标垂直移动的距离
    """
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, dx, dy, 0, 0)


def mouse_up(x, y, button=MOUSE_LEFT):
    """
    模拟鼠标释放事件。
    :param x: 鼠标释放位置的 x 坐标
    :param y: 鼠标释放位置的 y 坐标
    :param button: 鼠标按钮 (MOUSE_LEFT, MOUSE_RIGHT, MOUSE_MIDDLE)，默认为 MOUSE_LEFT
    """
    time.sleep(0.1)
    xx, yy = x + gvars.genshin_window_rect[0], y + gvars.genshin_window_rect[1]
    win32api.SetCursorPos((xx, yy))
    win32api.mouse_event(mouse_list_up[button], xx, yy, 0, 0)


def mouse_click(x, y, button=MOUSE_LEFT):
    """
    模拟鼠标点击事件，包括按下和释放。
    :param x: 鼠标点击位置的 x 坐标
    :param y: 鼠标点击位置的 y 坐标
    :param button: 鼠标按钮 (MOUSE_LEFT, MOUSE_RIGHT, MOUSE_MIDDLE)，默认为 MOUSE_LEFT
    """
    mouse_down(x, y, button)
    mouse_up(x, y, button)


def mouse_down_raw(x, y, button=MOUSE_LEFT):
    """
    模拟鼠标按下事件（无暂停）。
    :param x: 鼠标按下位置的 x 坐标
    :param y: 鼠标按下位置的 y 坐标
    :param button: 鼠标按钮 (MOUSE_LEFT, MOUSE_RIGHT, MOUSE_MIDDLE)，默认为 MOUSE_LEFT
    """
    xx, yy = x + gvars.genshin_window_rect[0], y + gvars.genshin_window_rect[1]
    win32api.mouse_event(mouse_list_down[button], xx, yy, 0, 0)


def mouse_up_raw(x, y, button=MOUSE_LEFT):
    """
    模拟鼠标释放事件（无暂停）。
    :param x: 鼠标释放位置的 x 坐标
    :param y: 鼠标释放位置的 y 坐标
    :param button: 鼠标按钮 (MOUSE_LEFT, MOUSE_RIGHT, MOUSE_MIDDLE)，默认为 MOUSE_LEFT
    """
    xx, yy = x + gvars.genshin_window_rect[0], y + gvars.genshin_window_rect[1]
    win32api.mouse_event(mouse_list_up[button], xx, yy, 0, 0)



def mouse_click_raw(x, y, button=MOUSE_LEFT):
    """
    模拟鼠标点击事件，包括按下和释放。
    :param x: 鼠标点击位置的 x 坐标
    :param y: 鼠标点击位置的 y 坐标
    :param button: 鼠标按钮 (MOUSE_LEFT, MOUSE_RIGHT, MOUSE_MIDDLE)，默认为 MOUSE_LEFT
    """
    mouse_down_raw(x, y, button)
    mouse_up_raw(x, y, button)



def match_img(img, target, type=cv2.TM_CCOEFF):
    """
    在图像中匹配目标图像，返回匹配位置的坐标信息。
    :param img: 输入图像
    :param target: 目标图像
    :param type: 匹配方法 (cv2.TM_CCOEFF, cv2.TM_CCOEFF_NORMED, cv2.TM_CCORR, cv2.TM_CCORR_NORMED, cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED)
        默认为 cv2.TM_CCOEFF
    :return:
        如果匹配方法为 TM_SQDIFF 或 TM_SQDIFF_NORMED，则返回一个包含匹配位置的元组：
            (左上角 x 坐标, 左上角 y 坐标, 右下角 x 坐标, 右下角 y 坐标, 中心 x 坐标, 中心 y 坐标)
        否则，返回一个包含匹配位置的元组：
            (左上角 x 坐标, 左上角 y 坐标, 右下角 x 坐标, 右下角 y 坐标, 中心 x 坐标, 中心 y 坐标)
    """
    h, w = target.shape[:2]
    res = cv2.matchTemplate(img, target, type)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    if type in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
        return (
            *min_loc,
            min_loc[0] + w,
            min_loc[1] + h,
            min_loc[0] + w // 2,
            min_loc[1] + h // 2,
        )
    else:
        return (
            *max_loc,
            max_loc[0] + w,
            max_loc[1] + h,
            max_loc[0] + w // 2,
            max_loc[1] + h // 2,
        )


def distance(x1, y1, x2, y2):
    """
    计算两点之间的欧几里德距离。
    :param x1: 第一个点的 x 坐标。
    :param y1: 第一个点的 y 坐标。
    :param x2: 第二个点的 x 坐标。
    :param y2: 第二个点的 y 坐标。
    :return: 两点之间的欧几里德距离。
    """
    return np.sqrt(np.square(x1 - x2) + np.square(y1 - y2))

