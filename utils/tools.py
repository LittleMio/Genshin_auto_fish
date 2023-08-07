from pathlib import Path
from typing import Union
from ruamel import yaml


def load_yaml(path: Union[Path, str], encoding: str = 'utf-8'):
    """
    说明：
        读取本地yaml文件，返回字典。
    参数：
        :param path: 文件路径
        :param encoding: 编码，默认为utf-8
        :return: 字典
    """
    if isinstance(path, str):
        path = Path(path)
    return yaml.load(path.read_text(encoding=encoding),
                     Loader=yaml.Loader) if path.exists() else {}


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
        yaml.dump(
            data,
            f,
            indent=2,
            Dumper=yaml.RoundTripDumper,
            allow_unicode=True)