# -*- coding:utf-8 -*-
import os
from json import load

from Functions.Utils.User import choose_directory
from Functions.Metadata.Car import extract_pref
from Functions.Utils.Datetime import time_now
from Functions.Utils.FileUtils import confirm_dir_exist
from Functions.Utils.JsonUtils import write_json
from Temp.JsonWorker.Base.Change import prefect_completion_status
from Temp.JsonWorker.Base.Custom import modify_cover_dmm

# Todo 去除标题末尾演员

root_choose = choose_directory()

for root, dirs, files in os.walk(root_choose):
    for file in files:
        if file.endswith('.json'):
            print("当前文件: ", file)
            path = f'{root}\\{file}'
            with open(path, encoding='utf-8') as f:
                dict_old = load(f)

            item_db = dict_old["Javdb"]
            dict_new = {
                'Car': dict_old['Car'],
                'CarOrigin': dict_old['CarOrigin'],
                'Series': dict_old['Series'],
                'Title': dict_old['Title'],
                'TitleZh': dict_old['TitleZh'],
                'Plot': dict_old['Plot'],
                'PlotZh': dict_old['PlotZh'],
                'Review': dict_old['Review'] if 'Review' in dict_old else '',
                'Release': dict_old['Release'],
                'Runtime': int(dict_old['Runtime']),
                'Director': dict_old['Director'],
                'Studio': dict_old['Studio'],
                'Publisher': dict_old['Publisher'],
                'Score': float(dict_old['Score']),
                'CoverDb': f'https://jdbimgs.com/covers/{item_db[:2].lower()}/{item_db}.jpg',
                'CoverLibrary': dict_old['CoverLibrary'],
                'CoverBus': dict_old['CoverBus'],
                'CoverDmm': '',
                'CutType': 3,
                'JavDb': dict_old['Javdb'],
                'JavLibrary': dict_old['Javlibrary'],
                'JavBus': dict_old['Javbus'] if 'Javbus' in dict_old else dict_old['Bus'],
                'Arzon': dict_old['Arzon'],
                # 'CompletionStatus': ,
                'Version': 1,
                'Genres': dict_old['Genres'],
                'Actors': dict_old['Actors'],
                'Init': time_now(),
                'Modify': time_now(),
            }

            # 纠正 cover
            modify_cover_dmm(dict_new)
            # 完善 completion status
            prefect_completion_status(dict_new)

            # 重新写
            car = dict_new['Car']
            pref = extract_pref(car)

            # 新生成的json存放目录
            dir_new = confirm_dir_exist(f'D:\\MyJava\\MyData\\AlreadyJsons\\新生jsons\\{pref}')
            # 新生成的json路径
            path_new = f'{dir_new}\\{car}.json'

            # 重复，不写，移动到失败
            if os.path.exists(path_new):
                folder = '重复jsons'
            else:
                folder = '迁移完成'
                write_json(path_new, dict_new)

            # 旧json 转移至
            dir_transfer = confirm_dir_exist(f'D:\\MyJava\\MyData\\AlreadyJsons\\{folder}\\{pref}')
            # 迁移至路径
            os.rename(path, f'{dir_transfer}\\{file}')
