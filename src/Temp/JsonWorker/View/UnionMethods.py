import os

from Functions.Utils.User import choose_directory
from Functions.Utils.JsonUtils import read_json_to_dict, write_json
from Temp.JsonWorker.Base.Custom import modify_cover_dmm, big_ten_cover_dmm
from Temp.JsonWorker.Base.Find import find_json_contain_key, find_json_special_key, find_json_contain_genre
from Temp.JsonWorker.Base.Show import show_json_one_key

dir_choose = choose_directory()

list_temp = []
for root, dirs, files in os.walk(dir_choose):
    for file in files:
        if file.endswith(('.json',)):
            path = f'{root}\\{file}'
            dict_json = read_json_to_dict(path)
            print('正在检查: ', path, end=' ')

            # 1 展示json的一个指定key
            # show_json_one_key(dict_json, 'CoverBus')

            # 2 检查jsons是否包含某一个指定key
            # find_json_contain_key(dict_json, 'Modify')

            # 3 检查jsons是否包含某一个指定genre
            # if find_json_contain_genre(dict_json, '業餘'):
            #     list_temp.append(path)

            # 98 将score扩大10倍
            # big_ten_cover_dmm(dict_json)
            # write_json(path, dict_json)

            # 99 找出满足条件的特殊json，进行相关修改
            # result = find_json_special_key(dict_json, 'CoverLibrary', check_cover_library)
            # if result:
            #     modify_cover_dmm(dict_json)
            #     print(dict_json)

print('======================OK======================')
for i in list_temp:
    print(i)
print('数量:', len(list_temp))
