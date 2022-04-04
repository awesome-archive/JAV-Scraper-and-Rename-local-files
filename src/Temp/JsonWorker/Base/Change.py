from typing import Dict

from Classes.Static.Enums import CompletionStatusEnum
from Functions.Utils.JsonUtils import read_json_to_dict, write_json


def replace_old_genre(dict_json: dict, dict_replace: Dict[str, str]):
    """
    新genre替换旧genre

    Args:
        dict_json: json 内容
        dict_replace: 需要替换的genre字典

    Returns:
        如果发生改变，返回True
    """
    has_modify = False

    old_genres = dict_json['Genres']
    new_genres = []

    for genre_old in old_genres:
        # Todo 弄一个删除list
        if genre_old.startswith('AV OPEN') or genre_old in {'限時降價'}:
            has_modify = True
            continue
        try:
            new_genres.append(dict_replace[genre_old])
            has_modify = True
        except KeyError:
            new_genres.append(genre_old)
    dict_json['Genres'] = list(set(new_genres))

    return has_modify


def replace_key_name(path, key_old, key_new):
    dict_json = read_json_to_dict(path)
    if key_old in dict_json:
        print('旧: ', dict_json)
        dict_json[key_new] = dict_json[key_old]
        del dict_json[key_old]
        print('新: ', dict_json)
        write_json(path, dict_json)


def replace_key_name_by_dict(dict_json, key_old, key_new):
    if key_old in dict_json:
        dict_json[key_new] = dict_json[key_old]
        del dict_json[key_old]
    return dict_json


def delete_key(dict_json, key):
    del dict_json[key]
    return dict_json


def add_new_key(dict_json, key_new, value):
    dict_json[key_new] = value
    return dict_json


def parse_string_to_int(dict_json, key):
    dict_json[key] = int(dict_json[key])
    return dict_json


def parse_string_to_float(dict_json, key):
    dict_json[key] = float(dict_json[key])
    return dict_json


def prefect_completion_status(dict_json):
    # sourcery skip: assign-if-exp, merge-else-if-into-elif
    """
    更新一下整理的完成度

    这部影片成功收集到哪几个网站的数据，在整理流程的末尾更新一下标志
    """
    if dict_json['JavDb']:
        if dict_json['JavLibrary']:
            if dict_json['JavBus']:
                completion = CompletionStatusEnum.db_library_bus.value  # 三个网站全部收集整理
            else:
                completion = CompletionStatusEnum.db_library.value
        else:
            if dict_json['JavBus']:
                completion = CompletionStatusEnum.db_bus.value
            else:
                completion = CompletionStatusEnum.only_db.value
    else:
        if dict_json['JavLibrary']:
            if dict_json['JavBus']:
                completion = CompletionStatusEnum.library_bus.value
            else:
                completion = CompletionStatusEnum.only_library.value
        else:
            if dict_json['JavBus']:
                completion = CompletionStatusEnum.only_bus.value
            else:
                completion = CompletionStatusEnum.unknown.value
    dict_json['CompletionStatus'] = completion
