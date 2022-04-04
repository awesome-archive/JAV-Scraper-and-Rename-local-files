import os

from Temp.JsonWorker.Base.Change import replace_key_name
from Functions.Utils.User import choose_directory

print('请选择要整理的文件夹：')

list_jsons = []
root_choose = choose_directory()

for root, dirs, files in os.walk(root_choose):
    for file in files:
        if file.endswith('.json'):
            print("当前文件: ", file)
            path = f'{root}\\{file}'
            replace_key_name(path, 'carOriginLibrary', 'CarOrigin')
print('改变:', list_jsons)
