import win32gui
from pathlib import Path
from ruamel import yaml

with open(str(Path(__file__).parent.parent / "config.yaml"), encoding='utf-8') as f:
    result = yaml.safe_load(f)

IMAGE_PATH = Path(__file__).parent.parent / "images"

WINDOW_NAME = result['windows']['window_name']
hWnd = win32gui.FindWindow(None, WINDOW_NAME)
MONITOR_WIDTH, MONITOR_HEIGHT = win32gui.GetClientRect(hWnd)[2:]

READY_RECT = result['windows']['ready_rect']
POS_DECT = result['windows']['pos_rect']

IS_DIEYU = result['fishing']['is_dieyu']
TIME_OUT = result['fishing']['time_out']
SHOW_LOG = result['fishing']['show_log']
SHOW_CUR = result['fishing']['show_cur']

# RATIO = MONITOR_WIDTH / MONITOR_HEIGHT
RATIO = 1366 / 768
print(RATIO)
# 16:9
if 1.8 > RATIO > 1.7:
    pass