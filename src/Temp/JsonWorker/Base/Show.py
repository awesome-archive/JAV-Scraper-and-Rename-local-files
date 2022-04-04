# -*- coding:utf-8 -*-
from Functions.Utils.JsonUtils import read_json_to_dict


def show_one_json_by_path(path: str):
    """
    print显示json的每一项

    Args:
        path: json路径
    """
    dict_json = read_json_to_dict(path)
    for i in dict_json:
        print(i, ':', dict_json[i])


def show_one_json(dict_json: dict):
    """
    print显示json的每一项

    Args:
        dict_json: json 内容
    """
    for i in dict_json:
        print(i, ':', dict_json[i])


def show_json_one_key(dict_json: dict, key: str):
    """
    展示指定json中的某一项

    Args:
        dict_json: json 内容
        key: 某一项key

    Returns:
        是否包含该key
    """
    try:
        print('它的key', dict_json[key])
        return True
    except KeyError:
        print('无')
        return False
