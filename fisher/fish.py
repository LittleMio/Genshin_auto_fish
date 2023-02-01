
import time

import cv2
import ctypes
import numpy
import win32api
import win32con
import win32gui
import win32ui

from utils.config import IMAGE_PATH

ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))

class Window:
    def __init__(self, name, cls=None):
        self.hWnd = win32gui.FindWindow(cls, name)
        assert self.hWnd
        self.hWndDC = win32gui.GetDC(self.hWnd)
        self.hMfcDc = win32ui.CreateDCFromHandle(self.hWndDC)
        self.hMemDc = self.hMfcDc.CreateCompatibleDC()

    def capture(self):
        self.width, self.height = win32gui.GetClientRect(self.hWnd)[2:]
        hBmp = win32ui.CreateBitmap()
        hBmp.CreateCompatibleBitmap(self.hMfcDc, self.width, self.height)
        self.hMemDc.SelectObject(hBmp)
        self.hMemDc.BitBlt((0, 0), (self.width, self.height), self.hMfcDc, (0, 0), win32con.SRCCOPY)
        result = numpy.frombuffer(hBmp.GetBitmapBits(True), dtype=numpy.uint8).reshape(self.height, self.width, 4)
        win32gui.DeleteObject(hBmp.GetHandle())
        return result

    def click(self, hold=0):
        win32api.PostMessage(self.hWnd, win32con.WM_LBUTTONDOWN, 0, 0)
        time.sleep(hold)
        win32api.PostMessage(self.hWnd, win32con.WM_LBUTTONUP, 0, 0)

    def __del__(self):
        self.hMemDc.DeleteDC()
        self.hMfcDc.DeleteDC()
        win32gui.ReleaseDC(self.hWnd, self.hWndDC)


FISHING = cv2.imread(str(IMAGE_PATH / 'fishing.png'))
TARGETLEFT = cv2.imread(str(IMAGE_PATH / 'target_left.png'))
TARGETRIGHT = cv2.imread(str(IMAGE_PATH / 'target_right.png'))
CUR = cv2.imread(str(IMAGE_PATH / 'cur.png'))
FISHINGMASK = cv2.imread(str(IMAGE_PATH / 'fishing_mask.png')) >> 7
TARGETLEFTMASK = cv2.imread(str(IMAGE_PATH / 'target_left_mask.png')) >> 7
TARGETRIGHTMASK = cv2.imread(str(IMAGE_PATH / 'target_right_mask.png')) >> 7
CURMASK = cv2.imread(str(IMAGE_PATH / 'cur_mask.png')) >> 7


class Check:
    @classmethod
    def setup(cls, capture, readyRect, posRect):
        cls.capture = capture
        cls.readySlice = (slice(readyRect[1], readyRect[3]), slice(readyRect[0], readyRect[2]))
        cls.posSlice = (slice(posRect[1], posRect[3]), slice(posRect[0], posRect[2]))

    def __init__(self, im=None):
        try:
            im = self.capture() if im is None else im
            size = (1280, round(im.shape[0] * 1280 // im.shape[1])) \
                if im.shape[0] * 16 > im.shape[1] * 9 else (round(im.shape[1] * 720 / im.shape[0]), 720)
            self.im = cv2.resize(im, size, interpolation=cv2.INTER_CUBIC)
            self.im = numpy.vstack([self.im[:360, size[0]//2-640:size[0]//2+640],self.im[-360:, -1280:]])
        except:
            self.im = numpy.zeros((720, 1280, 4), dtype=numpy.uint8)

    def wrapAlpha(self, im):
        im, alpha = im[..., :3]>>4, im[..., 3] >> 4
        for i in range(3):
            im[..., i] *= alpha
        return im

    def isReady(self):
        return .2 > cv2.minMaxLoc(cv2.matchTemplate(
            self.wrapAlpha(self.im[self.readySlice]), FISHING, cv2.TM_SQDIFF_NORMED, mask=FISHINGMASK))[0]

    def getPos(self):
        img = self.wrapAlpha(self.im[self.posSlice])
        loc = cv2.minMaxLoc(cv2.matchTemplate(img, CUR, cv2.TM_SQDIFF_NORMED, mask=CURMASK))
        if loc[0] > .2:
            return None
        return (loc[2][0],
            cv2.minMaxLoc(cv2.matchTemplate(img, TARGETLEFT, cv2.TM_SQDIFF_NORMED, mask=TARGETLEFTMASK))[2][0],
            cv2.minMaxLoc(cv2.matchTemplate(img, TARGETRIGHT, cv2.TM_SQDIFF_NORMED, mask=TARGETRIGHTMASK))[2][0])
