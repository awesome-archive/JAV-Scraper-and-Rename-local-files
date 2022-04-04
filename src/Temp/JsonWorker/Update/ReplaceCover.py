import os

from Functions.Utils.JsonUtils import read_json_to_dict, write_json


def replace_cover(dir_choose):
    """
    【定制】修正library的dmm图片到CoverDmm

    Args:
        dir_choose:

    Returns:

    """
    for root, dirs, files in os.walk(dir_choose):
        for file in files:
            if file.endswith(('.json',)):
                path = f'{root}\\{file}'
                print(path)
                dict_json = read_json_to_dict(path)
                if not dict_json['CoverLibrary']:
                    dict_json['CoverDmm'] = ''
                elif not dict_json['CoverLibrary'].startswith('http'):
                    print('特殊:', dict_json['CoverLibrary'])
                    dict_json['CoverDmm'] = ''
                elif 'dmm.co.jp' in dict_json['CoverLibrary']:
                    dict_json['CoverDmm'] = dict_json['CoverLibrary']
                    dict_json['CoverLibrary'] = ''
                write_json(path, dict_json)
