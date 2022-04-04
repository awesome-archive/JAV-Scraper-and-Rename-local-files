from typing import List


def find_json_contain_genre(dict_json: dict, genre: str):
    """
    当前json.genres是否包含某个genre

    Args:
        dict_json: json 内容
        genre: 指定genre

    Returns:
        bool
    """
    if genre in dict_json['Genres']:
        print('找到了', dict_json['Genres'])
        return True
    else:
        print('无')
        return False


def find_json_contain_key(dict_json: dict, key: str):
    """
    当前json是否包含某个key

    Args:
        dict_json: json 内容
        key: 指定key

    Returns:
        bool
    """
    try:
        print('找到了', dict_json[key])
        return True
    except KeyError:
        print('无')
        return False


def find_json_special_key(dict_json: dict, key: str, special_method):
    """
    当前json是否包含某个key

    Args:
        dict_json: json 内容
        key: 指定key
        special_method: 判定key特殊的方法

    Returns:
        bool
    """
    try:
        print('找到了', dict_json[key], end=' ')
        if special_method(dict_json):
            print('满足条件')
            return True
        else:
            print('不符合')
            return False
    except KeyError:
        print('无')
        return False


def find_wrong_genre(dict_json: dict, list_genres: List[str]):
    return next(
        (genre
         for genre in dict_json['Genres']
         if genre not in list_genres),
        '',
    )
