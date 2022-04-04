# -*- coding:utf-8 -*-
from json import load, dump


def read_json_to_dict(path: str):
    """
    提供json路径读取为dict

    Args:
        path: json路径
    """
    with open(path, encoding='utf-8') as f:
        dict_json = load(f)
    return dict_json


def write_json(path: str, dict_json):
    """
    写json

    Args:
        path: json路径
        dict_json: 内容dict
    """
    with open(path, 'w', encoding='utf-8') as f:
        dump(dict_json, f, indent=4)
