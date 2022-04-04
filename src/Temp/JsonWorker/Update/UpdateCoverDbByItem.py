import os

from Functions.Utils.JsonUtils import read_json_to_dict, write_json


def upate_cover_db(dir_choose):
    for root, dirs, files in os.walk(dir_choose):
        for file in files:
            if file.endswith(('.json',)):
                path = f'{root}\\{file}'
                dict_json = read_json_to_dict(path)
                item = dict_json['JavDb']
                if item:
                    print('有了', item)
                dict_json['CoverDb'] = f'https://jdbimgs.com/covers/{item[:2].lower()}/{item}.jpg'
                print(dict_json['CoverDb'])
                write_json(path, dict_json)
