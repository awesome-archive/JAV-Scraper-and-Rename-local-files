import os

from Functions.Utils.JsonUtils import write_json, read_json_to_dict
from Temp.JsonWorker.Base.Change import replace_old_genre
from Functions.Utils.User import choose_directory

root_choose = choose_directory()
list_temp = []
dict_repalce = {
    '觸手': '触手',
    '女主人、女老板': '女主人',
    '蠻橫嬌羞': '蛮横娇羞',
    '性感的': '性感',
    '模特兒': '模特',
    '和服・喪服': '和服·丧服',
}
for root, dirs, files in os.walk(root_choose):
    for file in files:
        if file.endswith('.json'):
            path = f'{root}\\{file}'
            print("当前文件: ", path)

            dict_json = read_json_to_dict(path)
            genres_old = dict_json['Genres']

            if replace_old_genre(dict_json, dict_repalce):
                list_temp.append(path)
                write_json(path, dict_json)
                print('该文件完成')

print('======================OK======================')
for i in list_temp:
    print(i)
print('数量:', len(list_temp))

# dict_repalce = {
#     '倒追': '女方搭讪',
#     '連褲襪': '连裤袜',
#     '泳裝': '泳装',
#     '女醫生': '女医生',
#     '手指插入': '插入手指',
#     '爛醉如泥的': '酒醉',
#     '數位馬賽克': '数位马赛克',
#     '个子高': '高挑',
#     '性騷擾': '性骚扰',
#     '賽車女郎': '赛车女郎',
#     '立即口交': '立即插入',
#     '無毛': '无毛',
#     '淫語': '淫语',
#     '監禁': '监禁',
#     '顏射': '颜射',
#     '艺人': '偶像艺人',
#     '女上位': '骑乘',
#     '業餘': '业余',
#     '合集': '精选综合',
#     'OL': '职业装',
#     '按摩': '大保健',
#     '企畫': '企画',
#     '迷你係列': '娇小',
#     '蕩婦': '荡妇',
#     '處男': '处男',
#     '秘書': '秘书',
#     '各種職業': '各种职业',
#     '4小時以上作品': '4小时+',
#     '女裝人妖': '女装人妖',
#     '折磨': '捆绑',
#     '已婚婦女': '人妻',
#     '亂倫': '乱伦',
#     '處女': '处女',
#     '明星臉': '明星脸',
#     '眼鏡': '眼镜',
#     '科幻': '奇幻',
#     '內衣': '内衣',
#     '玩具': '玩物',
#     '鴨嘴': '肛检',
#     '成熟的女人': '熟女',
# }