# -*- coding:utf-8 -*-
import os
from json import load, dump

from Functions.Utils.User import choose_directory

print('请选择要整理的文件夹：')
root_choose = choose_directory()
for root, dirs, files in os.walk(root_choose):
    for file in files:
        if file.endswith('.json'):
            print("当前文件: ", file)
            path = f'{root}\\{file}'
            with open(path, encoding='utf-8') as f:
                dict_old = load(f)

            dict_new = {
                'Car': dict_old['Car'],
                'carOriginLibrary': dict_old['lib_dmm'] or dict_old['db_dmm'],
                'Series': dict_old['series'],
                'Title': dict_old['title'],
                'TitleZh': dict_old['zh_title'],
                'Plot': dict_old['plot'],
                'PlotZh': dict_old['zh_plot'],
                'Release': dict_old['premiered'],
                'Runtime': dict_old['runtime'],
                'Director': dict_old['director'],
                'Studio': dict_old['studio'],
                'Publisher': dict_old['publisher'],
                'Score': dict_old['score_lib'],
                'Genres': dict_old['genres'],
                'Actors': dict_old['actors'],
                'Javdb': dict_old['db_id'],
                'Javlibrary': dict_old['lib_id'],
                'Arzon': dict_old['arzon_id'],
                'CoverDb': dict_old['cover_db'],
                'CoverLibrary': dict_old['cover_lib'],
                'Bus': dict_old['bus_id'],
                'CoverBus': dict_old['cover_bus'],
            }

            print(dict_old)
            print(dict_new)
            # 重新写
            with open(path, 'w', encoding='utf-8') as f:
                dump(dict_new, f, indent=4)
