import re
import sys
import loguru
import torch
import ctypes
import win32gui, win32api, win32con, win32print
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Dict
from .tools import load_yaml, save_yaml

FISH_CONFIG = Path(__file__).parent.parent / "config.yaml"

IMAGE_PATH = Path(__file__).parent.parent / "images"


class ConfigModel(BaseModel):
    window_name: str = Field('原神', alias='窗口名称')
    """窗口名称"""
    pos_dect: List[int] = Field([470, 44, 810, 135], alias='游标区')
    """鱼类上钩后的游标区域"""
    ready_rect: List[int] = Field([1020, 639, 1110, 682], alias='准备区')
    """等待时的按钮区"""
    is_dieyu: bool = Field(False, alias='钓雷鸣仙')
    """钓雷鸣仙模式"""
    time_out: int = Field(15, alias='等待时间')
    """抛竿后的等待时间"""
    show_cur: bool = Field(True, alias='显示游标')
    """命令窗口打印游标"""
    show_log: bool = Field(True, alias='显示日志')
    """命令窗口打印运行日志"""
    is_debug: bool = Field(False, alias='调试模式')



class FishConfigManager:
    if FISH_CONFIG.exists():
        config = ConfigModel.parse_obj(load_yaml(FISH_CONFIG))
    else:
        config = ConfigModel()
        save_yaml(config.dict(by_alias=True), FISH_CONFIG)

    @classmethod
    def save(cls):
        save_yaml(cls.config.dict(by_alias=True), FISH_CONFIG)

config = FishConfigManager.config

# """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

logger_log = loguru.logger
logger_log.remove()
logger_log.add(sys.stdout, format="{message}", level="INFO")
logger_log.add(sys.stdout, format="{message}", level="SUCCESS")
logger_log.add(sys.stdout, format="{message}", level="WARNING")
logger_log.add(sys.stdout, format="{message}", level="ERROR")

def escape_tag(s: str) -> str:
    """用于记录带颜色日志时转义 `<tag>` 类型特殊标签

    参考: [loguru color 标签](https://loguru.readthedocs.io/en/stable/api/logger.html#color)

    参数:
        s: 需要转义的字符串
    """
    return re.sub(r"</?((?:[fb]g\s)?[^<>\s]*)>", r"\\\g<0>", s)


class logger:
    @staticmethod
    def info(info: str = '', param: Dict[str, any] = None, result: str = '', result_type: bool = True):
        param_str = ' '.join([f'{k}<m>{escape_tag(str(v))}</m>' for k, v in param.items()]) if param else ''
        result_str = f'<g>{escape_tag(result)}</g>' if result_type else f'<r>{escape_tag(result)}</r>' if result else ''
        if config.show_log:
            logger_log.opt(colors=True).info(f'{info}{param_str}{result_str}')

    @staticmethod
    def success(info: str = '', param: Dict[str, any] = None, result: str = ''):
        param_str = ' '.join([f'{k}<m>{escape_tag(str(v))}</m>' for k, v in param.items()]) if param else ''
        result_str = f'<g>{escape_tag(result)}</g>' if result else ''
        if config.show_log:
            logger_log.opt(colors=True).success(f'{info}{param_str}{result_str}')

    @staticmethod
    def warning(info: str = '', action: str = ''):
        if config.show_log:
            logger_log.opt(colors=True).warning(f'<y>{escape_tag(info)}</y><m>{escape_tag(action)}</m>')

    @staticmethod
    def error(info: str = '', action: str = ''):
        if config.show_log:
            logger_log.opt(colors=True).error(f'{escape_tag(info)}<m>{escape_tag(action)}</m>')

# """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


logger.info('''<g>
    ██████╗ ███████╗███╗   ██╗███████╗██╗  ██╗██╗███╗   ██╗
   ██╔════╝ ██╔════╝████╗  ██║██╔════╝██║  ██║██║████╗  ██║
   ██║  ███╗█████╗  ██╔██╗ ██║███████╗███████║██║██╔██╗ ██║
   ██║   ██║██╔══╝  ██║╚██╗██║╚════██║██╔══██║██║██║╚██╗██║
   ╚██████╔╝███████╗██║ ╚████║███████║██║  ██║██║██║ ╚████║
    ╚═════╝ ╚══════╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝
 █████╗ ██╗   ██╗████████╗ ██████╗ ███████╗██╗███████╗██╗  ██╗
██╔══██╗██║   ██║╚══██╔══╝██╔═══██╗██╔════╝██║██╔════╝██║  ██║
███████║██║   ██║   ██║   ██║   ██║█████╗  ██║███████╗███████║
██╔══██║██║   ██║   ██║   ██║   ██║██╔══╝  ██║╚════██║██╔══██║
██║  ██║╚██████╔╝   ██║   ╚██████╔╝██║     ██║███████║██║  ██║
╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝
</g>''')

if not ctypes.windll.shell32.IsUserAnAdmin():
    logger.warning("当前不是以管理员身份运行， 请使用拥有管理员身份的终端重新运行")
    exit()
hDC = win32gui.GetDC(0)
hWnd = win32gui.FindWindow('UnityWndClass', config.window_name)
if win32gui.IsIconic(hWnd):
    logger.info(f"<g>检测到</g> <y>{config.window_name}</y> <g>已最小化，已自动处理</g>")
    win32gui.SendMessage(hWnd, win32con.WM_SYSCOMMAND, win32con.SC_RESTORE, 0)
SCALE = round(win32print.GetDeviceCaps(hDC, win32con.DESKTOPHORZRES) / win32api.GetSystemMetrics(0), 2)
MONITOR_WIDTH, MONITOR_HEIGHT = int(win32gui.GetClientRect(hWnd)[2] * SCALE), int(win32gui.GetClientRect(hWnd)[3] * SCALE)
logger.info(f"当前游戏分辨率为：{MONITOR_WIDTH} x {MONITOR_HEIGHT}")
RATIO = MONITOR_WIDTH / MONITOR_HEIGHT

# TODO: Add multi-resolution adaptation
if 1.8 > RATIO > 1.7:
    pass