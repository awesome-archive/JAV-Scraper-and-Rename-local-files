import os

from Temp.JsonWorker.Base.Show import show_one_json_by_path

print('****显示某个json的内容****')

path = '../../../【重要须备份】已整理的jsons/'

while 1:
    car_num = input('请输入该json的car_num：')
    print(path)
    if os.path.exists(path):
        print()
        show_one_json_by_path(path)
        print()
    else:
        print('没有整理到这个车牌！\n')
