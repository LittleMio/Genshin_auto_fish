from pathlib import Path
from typing import Union
from ruamel import yaml
import win32api, win32gui, win32con


def load_yaml(path: Union[Path, str], encoding: str = 'utf-8'):
    """
    读取本地yaml文件，返回字典。
    :param path: 文件路径
    :param encoding: 编码，默认为utf-8
    :return: 字典
    """
    if isinstance(path, str):
        path = Path(path)
    return yaml.load(path.read_text(encoding=encoding), Loader=yaml.Loader) if path.exists() else {}


def save_yaml(data: dict, path: Union[Path, str] = None, encoding: str = 'utf-8'):
    """
    保存yaml文件
    :param data: 数据
    :param path: 保存路径
    :param encoding: 编码
    """
    if isinstance(path, str):
        path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding=encoding) as f:
        yaml.dump(data, f, indent=2, Dumper=yaml.RoundTripDumper, allow_unicode=True)


def is_window_fullscreen(hwnd):
    """
    判断窗口是否处于全屏模式。
    :param hwnd: 窗口句柄
    :return: 如果窗口处于全屏模式，则返回 True，否则返回 False。
    """
    rect = win32gui.GetWindowRect(hwnd)
    return (rect[2] - rect[0] == win32api.GetSystemMetrics(win32con.SM_CXSCREEN)) and (
        rect[3] - rect[1] == win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
    )
