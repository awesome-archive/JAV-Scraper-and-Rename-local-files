# -*- coding:utf-8 -*-
import os, time, re
from time import sleep
from re import findall
from re import search
from configparser import RawConfigParser
from traceback import format_exc
from functions import *
from shutil import copyfile


#  main开始
print('1、请开启代理，建议美国节点，访问“https://www.jav321.com/”\n'
      '2、影片信息没有导演，没有演员头像，可能没有演员姓名\n'
      '3、只能处理列出车牌的素人影片\n'
      '4、如有素人车牌识别不出，请在ini中添加该车牌\n')
# 读取配置文件，这个ini文件用来给用户设置
print('正在读取ini中的设置...', end='')
try:
    config_settings = RawConfigParser()
    config_settings.read('【点我设置整理规则】.ini', encoding='utf-8-sig')
    # 是否 收集nfo
    bool_nfo = True if config_settings.get("收集nfo", "是否收集nfo？") == '是' else False
    # 是否 跳过已存在nfo的文件夹，不整理已有nfo的文件夹
    bool_skip = True if config_settings.get("收集nfo", "是否跳过已存在nfo的文件夹？") == '是' else False
    # nfo中title的格式
    custom_nfo_title = config_settings.get("收集nfo", "nfo中title的格式")
    # 是否 是否将 片商 作为特征
    bool_nfo_maker = True if config_settings.get("收集nfo", "是否将片商作为特征？") == '是' else False
    # 有些用户想把“发行年份”“影片类型”作为特征
    custom_genres = config_settings.get("收集nfo", "额外将以下元素添加到特征中")
    # 是否 重命名 视频
    bool_rename_mp4 = True if config_settings.get("重命名影片", "是否重命名影片？") == '是' else False
    # 新命名 视频
    custom_video = config_settings.get("重命名影片", "重命名影片的格式")
    # 是否 重命名视频所在文件夹，或者为它创建独立文件夹
    bool_rename_folder = True if config_settings.get("修改文件夹", "是否重命名或创建独立文件夹？") == '是' else False
    # 新命名 文件夹
    custom_folder = config_settings.get("修改文件夹", "新文件夹的格式")
    # 是否 重命名用户已拥有的字幕
    bool_rename_subt = True if config_settings.get("字幕文件", "是否重命名已有的字幕文件？") == '是' else False
    # 如果旧的nfo包含这些字符，则判定影片是“中字”
    custom_subt_nfo = config_settings.get("字幕文件", "已有字幕即nfo包含")
    # 是否 归类jav
    bool_classify = True if config_settings.get("归类影片", "是否归类影片？") == '是' else False
    # 是否 针对“文件夹”归类jav，“否”即针对“文件”
    bool_classify_folder = True if config_settings.get("归类影片", "针对文件还是文件夹？") == '文件夹' else False
    # 路径 归类的jav放到哪
    custom_root = config_settings.get("归类影片", "归类的根目录")
    # 路径 jav按什么类别来归类
    custom_classify_basis = config_settings.get("归类影片", "归类的标准")
    # 是否 下载图片
    bool_jpg = True if config_settings.get("下载封面", "是否下载封面海报？") == '是' else False
    # 命名 大封面fanart
    custom_fanart = config_settings.get("下载封面", "DVD封面的格式")
    # 命名 小封面poster
    custom_poster = config_settings.get("下载封面", "海报的格式")
    # 是否 使用代理
    bool_proxy = True if config_settings.get("代理", "是否使用代理？") == '是' else False
    # IP端口 代理
    proxy = config_settings.get("代理", "代理IP及端口")
    # 是否 使用简体中文 简介翻译的结果和jav特征会变成“简体”还是“繁体”
    bool_zh = True if config_settings.get("其他设置", "简繁中文？") == '简' else False
    # 素人车牌 如果用户的视频名，在这些车牌中，才会去“jav321.com"整理
    custom_suren_pref = config_settings.get("信息来源", "列出车牌(素人为主，可自行添加)")
    # 文件类型 只有列举出的视频文件类型，才会被处理
    custom_file_type = config_settings.get("其他设置", "扫描文件类型")
    # 命名格式中“标题”的长度 windows只允许255字符，所以限制长度，但nfo中的标题是全部
    int_title_len = int(config_settings.get("其他设置", "重命名中的标题长度（50~150）"))
    # 原影片性质 影片有中文，体现在视频名称中包含这些字符
    custom_subt_video = config_settings.get("原影片文件的性质", "是否中字即文件名包含")
    # 是否中字 这个元素的表现形式
    custom_subt_expression = config_settings.get("原影片文件的性质", "是否中字的表现形式")
    # 原影片性质 影片有xx的性质，体现在视频名称中包含这些字符
    custom_xx_words = config_settings.get("原影片文件的性质", "是否xx即文件名包含")
    # 是否xx 这个元素的表现形式
    custom_xx_expression = config_settings.get("原影片文件的性质", "是否xx的表现形式")
    ######################################## 不同 ####################################################
    # 原影片性质 马场
    custom_movie_type = config_settings.get("原影片文件的性质", "素人")
    # 把日语简介翻译为中文
    bool_tran = True if config_settings.get("百度翻译API", "是否翻译为中文？") == '是' else False
    # 账户 百度翻译api
    ID = config_settings.get("百度翻译API", "APP ID")
    SK = config_settings.get("百度翻译API", "密钥")
except:
    print(format_exc())
    print('\n无法读取ini文件，请修改它为正确格式，或者打开“【ini】重新创建ini.exe”创建全新的ini！')
    os.system('pause')

print('\n读取ini文件成功!')
# 确认：简/繁中文，影响影片特征和简介
if bool_zh:
    url_search = 'https://www.jav321.com/search'
    url_web = 'https://www.jav321.com/'
    t_lang = 'zh'  # 百度翻译，日译简中
else:
    url_search = 'https://tw.jav321.com/search'
    url_web = 'https://tw.jav321.com/'
    t_lang = 'cht'
# 代理设置
proxies = {"http": "http://" + proxy, "https": "https://" + proxy}
# 确认：代理哪些站点
if bool_proxy and proxy != '':      # 是否需要代理，设置请求时的状态
    list_jav = [0, '', '', proxies]              # 代理jav等网站
    list_cover = [0, '', '', proxies]            # 代理dmm图片原
    list_search = [0, '', '', {}, proxies]       # 代理jav等网站
else:
    list_jav = [0, '', '']
    list_cover = [0, '', '']
    list_search = [0, '', '', {}]
# 确认：归类影片本身还是它所在的文件夹，归类“文件（夹）”具有最高决定权
if bool_classify:            # 如果需要归类
    if bool_classify_folder:    # 并且是针对文件夹
        bool_rename_folder = True           # 那么必须重命名文件夹或者创建新的文件夹
    else:
        bool_rename_folder = False           # 否则不会操作新文件夹
# 初始化其他
sep = os.sep  # 当前系统的路径分隔符 windows是“\”，linux和mac是“/”
# 存放影片信息，演员，标题等
dict_nfo = {'空格': ' ', '车牌': 'ABC-123', '标题': '素人标题', '完整标题': '完整标题', '导演': '素人导演',
            '发行年月日': '1970-01-01', '发行年份': '1970', '月': '01', '日': '01',
            '片商': '素人片商', '评分': '0', '首个演员': '素人', '全部演员': '素人',
            '片长': '0', '\\': sep, '/': sep, '是否中字': '', '视频': 'ABC-123', '车牌前缀': 'ABC',
            '是否xx': '', '影片类型': custom_movie_type, '系列': '素人系列',
            '原文件名': 'ABC-123', '原文件夹名': 'ABC-123', }
list_extra_genres = custom_genres.split('、') if custom_genres != '' else []  # 需要的额外特征
list_suren_num = custom_suren_pref.split('、')          # 素人番号的列表
list_rename_video = custom_video.split('+')             # 重命名视频的格式
list_rename_folder = custom_folder.split('+')           # 重命名文件夹的格式
tuple_type = tuple(custom_file_type.split('、'))        # 需要扫描的文件的类型
list_name_nfo_title = custom_nfo_title.replace('标题', '完整标题', 1).split('+')  # nfo中title的写法
list_name_fanart = custom_fanart.split('+')            # fanart的格式
list_name_poster = custom_poster.split('+')            # poster的格式
list_subt_video = custom_subt_video.split('、')      # 包含哪些特殊含义的文字，判断是否中字
list_include_xx = custom_xx_words.split('、')          # 包含哪些特殊含义的文字，判断是否xx
list_subt_nfo = custom_subt_nfo.split('、')      # 包含哪些特殊含义的文字，判断是否中字
# 七个for，如果有什么高效简介的办法，请告诉我
for j in list_extra_genres:
    if j not in dict_nfo:
        dict_nfo[j] = j
for j in list_rename_video:
    if j not in dict_nfo:
        dict_nfo[j] = j
for j in list_rename_folder:
    if j not in dict_nfo:
        dict_nfo[j] = j
list_classify_basis = []
for i in custom_classify_basis.split('\\'):   # 归类标准，归类到哪个文件夹。不管是什么操作系统，用户写归类的规则，用“\”连接
    for j in i.split('+'):
        if j not in dict_nfo:
            dict_nfo[j] = j
        list_classify_basis.append(j)
    list_classify_basis.append(sep)
for j in list_name_nfo_title:
    if j not in dict_nfo:
        dict_nfo[j] = j
for j in list_name_fanart:
    if j not in dict_nfo:
        dict_nfo[j] = j
for j in list_name_poster:
    if j not in dict_nfo:
        dict_nfo[j] = j

# 用户输入“回车”就继续选择文件夹整理
input_start_key = ''
while input_start_key == '':
    # 用户选择文件夹
    print('请选择要整理的文件夹：', end='')
    root_choose = get_directory()  # 用户选择的文件夹
    print(root_choose)
    # 在txt中记录一下用户的这次操作
    record_txt = open('【记得清理它】失败记录.txt', 'a', encoding="utf-8")
    record_txt.write('已选择文件夹：' + root_choose + ' ' + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) + '\n')
    record_txt.close()
    print('...文件扫描开始...如果时间过长...请避开中午夜晚高峰期...\n')
    # 确认：归类根目录
    if bool_classify:
        custom_root = custom_root.rstrip(sep)
        if custom_root != '所选文件夹':
            if custom_root != root_choose:  # 归类根目录是用户输入的路径，继续核实合法性
                if custom_root[:2] != root_choose[:2]:
                    print('归类的根目录“', custom_root, '”和所选文件夹不在同一磁盘无法归类！请修正！')
                    os.system('pause')
                if not os.path.exists(custom_root):
                    print('归类的根目录“', custom_root, '”不存在！无法归类！请修正！')
                    os.system('pause')
                root_classify = custom_root.rstrip(sep)
            else:  # 归类根目录就是用户所选的路径
                root_classify = root_choose + sep + '归类完成'
        else:
            root_classify = root_choose + sep + '归类完成'
    # 初始化“失败信息”
    num_fail = 0                             # 计数 错误信息
    # root【当前根目录】 dirs【子目录】 files【文件】，root是字符串，后两个是list
    for root, dirs, files in os.walk(root_choose):
        if not files:
            continue
        if '归类完成' in root.replace(root_choose, ''):  # “当前目录”在“目标归类目录”中
            # print('>>该文件夹在归类的根目录中，跳过处理...', root)
            continue      # 跳出此次root, dirs, files
        if bool_skip and len(files) > 1 and (files[-1].endswith('nfo') or files[-2].endswith('nfo')):
            # print(root+'sep+files[-1])      整理要跳过已存在nfo的文件夹，判断这一层文件夹最后两个文件是不是nfo
            continue     # 跳出此次root, dirs, files
        # 对这一层文件夹进行评估,有多少视频，有多少同车牌视频，是不是独立文件夹
        list_jav_videos = []        # 存放：需要整理的jav的结构体
        dict_car_pref = {}           # 存放：这一层目录下的几个车牌 abp avop snis。。。{'abp': 1, avop': 2} abp只有一集，avop有cd1、cd2
        num_videos_include = 0          # 当前文件夹中视频的数量，可能有视频不是jav
        dict_subt_files = {}        # 存放：jav的字幕文件 {'c:\a\abc_123.srt': 'abc-123'}
        # 判断文件是不是字幕文件
        for file_raw in files:
            if file_raw.endswith(('.srt', '.vtt', '.ass', '.ssa', '.sub', '.smi',)):
                subt_num = search(r'([a-zA-Z]{2,7})[-_ ]*(\d{2,6})', file_raw)  # 字幕中含有的车牌，字幕车牌 和 视频车牌要配对
                if str(subt_num) != 'None':
                    jav_pref = subt_num.group(1).upper()
                    if jav_pref not in list_suren_num and '三二一' not in file_raw:
                        continue     # 跳出此次file_raw
                    jav_suf = subt_num.group(2)
                    jav_num = jav_pref + '-' + jav_suf
                    dict_subt_files[file_raw] = jav_num
        # print(dict_subt_files)
        # 判断文件是不是视频，得到车牌号
        for file_raw in files:
            if file_raw.endswith(tuple_type) and not file_raw.startswith('.'):
                num_videos_include += 1
                video_numg = search(r'([a-zA-Z]{2,7})[-_ ]*(\d{2,6})', file_raw)    # 这个正则表达式匹配“车牌号”可能有点奇怪，
                if str(video_numg) != 'None':                               # 如果你下过上千部片，各种参差不齐的命名，你就会理解我了。
                    jav_pref = video_numg.group(1).upper()
                    # jav321只用来处理素人或其他列出的车牌
                    if jav_pref not in list_suren_num and '三二一' not in file_raw:
                        continue     # 跳出此次file_raw
                    # 是素人影片，继续
                    jav_suf = video_numg.group(2)
                    # 去掉太多的0，avop00127
                    if len(jav_suf) > 3:
                        jav_suf = jav_suf[:-3].lstrip('0') + jav_suf[-3:]
                    # jav_num 车牌
                    jav_num = jav_pref + '-' + jav_suf
                    # 这个车牌有几集？
                    try:
                        dict_car_pref[jav_num] += 1  # 已经有这个车牌了，加一集cd
                    except KeyError:
                        dict_car_pref[jav_num] = 1  # 这个新车牌有了第一集
                    # 把这个jav的各种属性打包好
                    jav_struct = JavFile()
                    jav_struct.num = jav_num           # 车牌
                    jav_struct.file = file_raw         # 原文件名
                    jav_struct.episodes = dict_car_pref[jav_num]  # 这个jav视频，是第几集  {'abp': 1, avop': 2}
                    if jav_num in dict_subt_files.values():
                        jav_struct.subt = list(dict_subt_files.keys())[list(dict_subt_files.values()).index(jav_num)]
                        del dict_subt_files[jav_struct.subt]
                    list_jav_videos.append(jav_struct)
                else:
                    continue     # 跳出此次file_raw
        # 判定影片所在文件夹是否是独立文件夹
        if dict_car_pref:  # 这一层文件夹下有jav
            if len(dict_car_pref) > 1 or num_videos_include > len(list_jav_videos) or exist_other_folders(dirs):
                # 当前文件夹下，车牌不止一个；还有其他非jav视频；有其他文件夹，除了演员头像文件夹“.actors”和额外剧照文件夹“extrafanart”；
                bool_separate_folder = False   # 不是独立的文件夹
            else:
                bool_separate_folder = True    # 这一层文件夹是这部jav的独立文件夹
        else:
            continue       # 跳出此次root, dirs, files

        # 正式开始
        # 这个车牌的信息还未查找
        bool_already = False
        for jav in list_jav_videos:
            jav_raw_num = jav.num  # 车牌  abc-123
            jav_file = jav.file    # 完整的原文件名  abc-123.mp4
            jav_epi = jav.episodes
            num_all_episodes = dict_car_pref[jav_raw_num]
            path_jav = root + sep + jav_file  # jav的起始路径
            path_relative = sep + path_jav.replace(root_choose, '')   # 影片的相对于所选文件夹的路径，用于报错
            print('>>正在搜索：', jav_file)
            # 视频本身的一些属性
            video_type = '.' + jav_file.split('.')[-1]  # 文件类型，如：.mp4
            jav_name = jav_file[:-len(video_type)]  # 不带视频类型的文件名
            subt_file = jav.subt  # 与当前影片配对的字幕的文件名 abc-123.srt
            # 判断是否有中字
            bool_subt = False  # 有没有字幕
            dict_nfo['是否中字'] = ''
            # 有外挂字幕
            if subt_file:
                bool_subt = True
                dict_nfo['是否中字'] = custom_subt_expression
                subt_type = '.' + subt_file.split('.')[-1]  # 字幕类型，如：.srt
            # 原文件名包含“-c、-C、中字”这些字符
            if not bool_subt:
                name_no_cd = jav_name.replace('-cd', '')
                for i in list_subt_video:
                    if i in name_no_cd:
                        bool_subt = True
                        dict_nfo['是否中字'] = custom_subt_expression
                        break
            # 先前的nfo中的“标题”、“标签”有中文
            if not bool_subt:
                path_nfo_temp = root + sep + jav_name + '.nfo'
                if os.path.exists(path_nfo_temp):
                    if if_word_nfo(list_subt_nfo, path_nfo_temp):
                        bool_subt = True
                        dict_nfo['是否中字'] = custom_subt_expression
            # 判断是否xx
            dict_nfo['是否xx'] = ''
            for i in list_include_xx:
                if i in jav_name:
                    dict_nfo['是否xx'] = custom_xx_expression
                    break

            try:
                # 获取nfo信息的javlibrary网页
                if '三二一' in jav_file:
                    url_appointg = search(r'三二一(.+?)\.', jav_file)
                    if str(url_appointg) != 'None':
                        url_on_web = url_web + 'video/' + url_appointg.group(1)
                        list_jav[0] = 0
                        list_jav[1] = '    >打开jav321上的网页失败，正在重新尝试...'
                        list_jav[2] = url_on_web
                        html_web = get_321_html(list_jav)
                        # 尝试找标题，jav321上的标题不包含车牌，title_only表示单纯的标题
                        titleg = search(r'<h3>(.+?) <small>', html_web)  # 匹配处理“标题”
                        # 搜索结果就是AV的页面
                        if str(titleg) != 'None':
                            title_only = titleg.group(1)
                            print(title_only)
                        # 找不到标题，jav321找不到影片
                        else:
                            print(html_web)
                            num_fail += 1
                            record_fail('    >第' + str(num_fail) + '个失败！找不到该车牌的影片：' + path_relative + '\n')
                            continue
                    else:
                        num_fail += 1
                        record_fail('    >第' + str(num_fail) + '个失败！你指定的jav321网址有错误：' + path_relative + '\n')
                        continue        # 跳出这次整理
                # 正常的搜索
                else:
                    # 0尝试次数  1报错信息   2url  3data  4proxy
                    list_search[0] = 0
                    list_search[1] = '    >打开jav321搜索页面失败，正在重新尝试...'
                    list_search[2] = url_search
                    list_search[3] = {'sn': jav_raw_num}
                    # 得到javlibrary搜索网页html
                    html_web = post_321_html(list_search)
                    # 搜索结果的网页，大部分情况就是这个影片的网页，也有可能是多个结果的网页
                    # 尝试找标题，第一种情况：找得到，就是这个影片的网页
                    titleg = search(r'h3>(.+?) <small>', html_web)  # 匹配处理“标题”
                    # 搜索结果就是AV的页面
                    if str(titleg) != 'None':
                        title_only = titleg.group(1)
                        # print(title_only)
                    # 找不到标题，jav321找不到影片
                    else:
                        num_fail += 1
                        record_fail('    >第' + str(num_fail) + '个失败！找不到该车牌的影片：' + path_relative + '\n')
                        continue


                # 替换xml中的不允许的特殊字符 .replace('\'', '&apos;').replace('\"', '&quot;')
                # .replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')  nfo基于xml中不允许这5个字符，但实际测试只不允许左边3个
                title_only = title_only.replace('&', '和').replace("<", "[").replace(">", "]") \
                    .replace("\\", "#").replace("/", "#").replace(":", "：").replace("*", "#") \
                    .replace("?", "？").replace("\"", "#").replace("|", "#").replace('\n', '') \
                    .replace('\t', '').replace('\r', '').rstrip()  # 替换windows路径不允许的特殊字符 \/:*?"<>|
                # 正则匹配 影片信息 开始！
                # 有大部分信息的html_web
                html_web = search(r'(h3>.+?)async', html_web).group(1)
                # 车牌
                try:
                    dict_nfo['车牌'] = jav_num = search(r'番.</b>: (.+?)<br>', html_web).group(1).upper()
                except:
                    print(html_web)
                    os.system('pause')
                dict_nfo['车牌前缀'] = jav_num.split('-')[0]
                # 素人的title开头不是车牌
                title = jav_num + ' ' + title_only
                # 给用户重命名用的标题是 短的title，nfo中是“完整标题”，但用户在ini中只用写“标题”
                dict_nfo['完整标题'] = title_only
                # 处理影片的标题过长
                if len(title_only) > int_title_len:
                    dict_nfo['标题'] = title_only[:int_title_len]
                else:
                    dict_nfo['标题'] = title_only
                print('    >开始处理：', title)
                # DVD封面cover
                coverg = search(r'poster="(.+?)"><source', html_web)  # 封面图片的正则对象
                if str(coverg) != 'None':
                    url_cover = coverg.group(1)
                else:  # src="http://pics.dmm.co.jp/digital/amateur/scute530/scute530jp-001.jpg"
                    coverg = search(r'img-responsive" src="(.+?)"', html_web)  # 封面图片的正则对象
                    if str(coverg) != 'None':
                        url_cover = coverg.group(1)
                    else:  # src="http://pics.dmm.co.jp/digital/amateur/scute530/scute530jp-001.jpg"
                        coverg = search(r'src="(.+?)"', html_web)  # 封面图片的正则对象
                        if str(coverg) != 'None':
                            url_cover = coverg.group(1)
                        else:
                            url_cover = ''
                # 下载海报 poster
                posterg = search(r'img-responsive" src="(.+?)"', html_web)  # 封面图片的正则对象
                if str(posterg) != 'None':
                    url_poster = posterg.group(1)
                else:
                    url_poster = ''
                # 发行日期
                premieredg = search(r'日期</b>: (\d\d\d\d-\d\d-\d\d)<br>', html_web)
                if str(premieredg) != 'None':
                    dict_nfo['发行年月日'] = time_premiered = premieredg.group(1)
                    dict_nfo['发行年份'] = time_premiered[0:4]
                    dict_nfo['月'] = time_premiered[5:7]
                    dict_nfo['日'] = time_premiered[8:10]
                else:
                    dict_nfo['发行年月日'] = time_premiered = '1970-01-01'
                    dict_nfo['发行年份'] = '1970'
                    dict_nfo['月'] = '01'
                    dict_nfo['日'] = '01'
                # 片长 <td><span class="text">150</span> 分钟</td>
                runtimeg = search(r'播放..</b>: (\d+)', html_web)
                if str(runtimeg) != 'None':
                    dict_nfo['片长'] = runtimeg.group(1)
                else:
                    dict_nfo['片长'] = '0'
                # 片商</b>: <a href="/company/%E83%A0%28PRESTIGE+PREMIUM%29/1">プレステージプレミアム(PRESTIGE PREMIUM)</a>
                studio = ''
                studiog = search(r'片商</b>: <a href="/company.+?">(.+?)</a>', html_web)
                if str(studiog) != 'None':
                    dict_nfo['片商'] = studio = studiog.group(1).replace("\\", "#").replace("/", "#").replace(":", "：")\
                        .replace("*", "#").replace("?", "？").replace("\"", "#")
                else:
                    dict_nfo['片商'] = '素人片商'
                # 演员们 和 # 第一个演员   演员</b>: 花音さん 21歳 床屋さん(家族経営) &nbsp
                actorg = search(r'small>(.+?)</small>', html_web)
                if str(actorg) != 'None':
                    actor_only = actorg.group(1)
                    list_actor = actor_only.replace('/', ' ').split(' ')  # <small>luxu-071 松波優 29歳 システムエンジニア</small>
                    list_actor = [i for i in list_actor if i != '']
                    if len(list_actor) > 3:
                        dict_nfo['首个演员'] = list_actor[1] + ' ' + list_actor[2] + ' ' + list_actor[3]
                    elif len(list_actor) > 1:
                        del list_actor[0]
                        dict_nfo['首个演员'] = ' '.join(list_actor)
                    else:
                        dict_nfo['首个演员'] = '素人'
                    dict_nfo['全部演员'] = dict_nfo['首个演员']
                else:
                    dict_nfo['首个演员'] = dict_nfo['全部演员'] = '素人'
                # 特点
                genres = findall(r'genre.+?">(.+?)</a>', html_web)
                genres = [i for i in genres if i != '标签' and i != '標籤' and i != '素人']
                if bool_subt:  # 有“中字“，加上特征”中文字幕”
                    genres.append('中文字幕')
                if dict_nfo['是否xx']:   # 有xx，加上特征custom_xx_expression
                    genres.append(custom_xx_expression)
                # print(genres)
                # 评分
                scoreg = search(r'评分</b>: (\d\.\d)<br>', html_web)
                if str(scoreg) != 'None':
                    float_score = float(scoreg.group(1))
                    float_score = (float_score - 2) * 10 / 3
                    if float_score >= 0:
                        score = '%.1f' % float_score
                    else:
                        score = '0'
                else:
                    scoreg = search(r'"img/(\d\d)\.gif', html_web)
                    if str(scoreg) != 'None':
                        float_score = float(scoreg.group(1)) / 10
                        float_score = (float_score - 2) * 10 / 3
                        if float_score >= 0:
                            score = '%.1f' % float_score
                        else:
                            score = '0'
                    else:
                        score = '0'
                dict_nfo['评分'] = score
                # 烂番茄评分 用上面的评分*10
                criticrating = str(float(dict_nfo['评分']) * 10)
                #######################################################################
                # 简介
                plotg = search(r'md-12">([^<].+?)</div>', html_web)
                if str(plotg) != 'None':
                    plot = plotg.group(1)
                    plot = plot.replace('&', '和').replace('<', '[').replace('>', ']') \
                           .replace('\n', '').replace('\t', '').replace('\r', '')
                else:
                    plot = title_only
                if bool_tran:
                    plot = tran(ID, SK, plot, t_lang, 0)
                    if plot.startswith('【百度'):
                        num_fail += 1
                        record_fail('    >第' + str(num_fail) + '个失败！翻译简介失败：' + path_relative + '\n')
                # print(plot)
                ##################################################################################################
                # jav_name 是自始至终的 文件名（不带文件类型）  jav_file是自始至终的 文件名（完整带文件类型） root是原所在文件夹的路径  root_now 是现在（新）所在文件夹的路径
                # path_jav 是现在视频路径   path_subt是现在字幕路径   subt_file是 自始至终的 字幕文件名（带文件类型）  jav_folder是自始至终的 所在文件夹名（不是路径）
                dict_nfo['视频'] = dict_nfo['原文件名'] = jav_name                    # 【发生变化】 dict_nfo['视频']
                jav_folder = dict_nfo['原文件夹名'] = root.split(sep)[-1]  # 当前影片的目录名称，在下面的重命名操作中即将发生变化
                path_subt = root + sep + subt_file             # 字幕的起始路径
                root_now = root                                # 当前影片的目录路径，【即将变化】
                # 是CD1还是CDn？
                str_cd = ''
                if num_all_episodes > 1:
                    str_cd = '-cd' + str(jav_epi)

                # 1重命名视频
                if bool_rename_mp4:
                    # 构造新文件名
                    jav_name = ''
                    for j in list_rename_video:
                        jav_name += dict_nfo[j]
                    jav_name = jav_name.rstrip() + str_cd        # 【发生变化】jav_name  去除末尾空格，否则windows会自动删除空格，导致程序仍以为带空格
                    # 新的完整文件名，新的路径
                    dict_nfo['视频'] = jav_name             # 【发生变化】 dict_nfo['视频']
                    jav_file = jav_name + video_type             # 【发生变化】jav_file
                    path_jav_new = root_now + sep + jav_file
                    if not os.path.exists(path_jav_new):        # 【防止错误】 还不存在目标文件
                        # 重命名视频
                        os.rename(path_jav, path_jav_new)
                        path_jav = path_jav_new                  # 【发生变化】 path_jav
                    elif path_jav.upper() == path_jav_new.upper():  # 【防止错误】 存在目标文件，但就是现在的文件
                        try:
                            os.rename(path_jav, path_jav_new)
                            path_jav = path_jav_new  # 【发生变化】 path_jav
                        except:
                            num_fail += 1
                            record_fail('    >第' + str(num_fail) + '个失败！请自行重命名：' + path_relative + '\n')
                    # 存在目标文件，不是现在的文件。
                    else:  # 【防止错误】存在目标文件，不是现在的文件。
                        num_fail += 1
                        record_fail(
                            '    >第' + str(num_fail) + '个失败！重命名影片失败，重复的影片，已经有相同文件名的视频了：' + path_jav_new + '\n')
                        continue  # 退出对该jav的整理
                    print('    >修改文件名' + str_cd + '完成')
                    # 重命名字幕
                    if subt_file and bool_rename_subt:
                        subt_file = jav_name + subt_type        # 【发生变化】 subt_file
                        path_subt_new = root_now+ sep + subt_file
                        if path_subt != path_subt_new:
                            os.rename(path_subt, path_subt_new)
                            path_subt = path_subt_new           # 【发生变化】 path_subt
                        print('    >修改字幕名完成')

                # 2 归类影片，只针对视频文件和字幕文件。注意：第2操作和（下面第3操作或者下面第7操作）互斥，只能执行一个，归类影片是针对“文件”还是“文件夹”。
                if bool_classify and not bool_classify_folder:
                    # 构造 移动的目标文件夹
                    root_dest = root_classify + sep
                    for j in list_classify_basis:
                        root_dest += dict_nfo[j].rstrip()      # 【临时变量】归类的目标文件夹路径    C:\Users\JuneRain\Desktop\测试文件夹\1\葵司\
                    if not os.path.exists(root_dest):
                        os.makedirs(root_dest)
                    path_jav_new = root_dest + sep + jav_file  # 【临时变量】新的影片路径
                    if not os.path.exists(path_jav_new):       # 【防止错误】目标文件夹没有相同的影片，防止用户已经有一个“avop-127.mp4”，现在又来一个
                        os.rename(path_jav, path_jav_new)
                        root_now = root_dest                   # 【发生变化】root_now   C:\Users\JuneRain\Desktop\测试文件夹\1\葵司\
                        path_jav = path_jav_new                # 【发生变化】path_jav   C:\Users\JuneRain\Desktop\测试文件夹\1\葵司\avop-127.mp4
                        print('    >归类视频文件完成')
                        # 同理操作 字幕文件
                        if subt_file:
                            path_subt_new = root_now + sep + subt_file  # 【临时变量】新的字幕路径
                            if path_subt != path_subt_new:
                                os.rename(path_subt, path_subt_new)
                                # 不再更新 path_subt，下面不会再操作 字幕文件
                            print('    >归类字幕文件完成')
                    else:
                        num_fail += 1
                        record_fail('    >第' + str(num_fail) + '个失败！归类失败，重复的影片，归类的目标文件夹已经存在相同的影片：' + path_jav_new + '\n')
                        continue   # 退出对该jav的整理

                # 3重命名文件夹。如果是针对“文件”归类，这一步会被跳过。 用户只需要归类视频文件，不需要管文件夹。
                if bool_rename_folder:
                    # 构造 新文件夹名jav_folder_new
                    jav_folder_new = ''
                    for j in list_rename_folder:
                        jav_folder_new += (dict_nfo[j])
                    jav_folder_new = jav_folder_new.rstrip(' .')  # 【临时变量】新的所在文件夹。去除末尾空格和“.”，否则windows会自动删除它们，导致程序仍以为带空格和“.”
                    # 是独立文件夹，才会重命名文件夹
                    if bool_separate_folder:
                        if jav_epi == num_all_episodes:
                            # 同一车牌有n部，且这就是第n集，才会被重命名
                            list_root_now = root_now.split(sep)
                            del list_root_now[-1]
                            root_new = sep.join(list_root_now) + sep + jav_folder_new        # 【临时变量】新的影片路径。上级文件夹路径+新文件夹名称=新文件夹路径
                            if not os.path.exists(root_new):        # 【防止错误】目标影片文件夹不存在，或者目标影片文件夹存在，但就是现在的文件夹，即新旧相同
                                # 修改文件夹
                                os.rename(root_now, root_new)
                                root_now = root_new              # 【发生变化】root_now
                                path_jav = root_now + sep + jav_file                # 【发生变化】path_jav
                                jav_folder = jav_folder_new      # 【发生变化】jav_folder
                            elif root_now == root_new:           # 【防止错误】新旧文件夹名 相同
                                pass
                            else:                                # 【防止错误】如果用户已经有一个“avop-127”的文件夹了，现在又要创建一个新的
                                num_fail += 1
                                record_fail('    >第' + str(num_fail) + '个失败！重命名文件夹失败，已存在相同文件夹：' + root_new + '\n')
                                continue   # 退出对该jav的整理
                            print('    >重命名文件夹完成')
                    # 不是独立的文件夹，建立独立的文件夹
                    else:
                        root_separate_folder = root_now + sep + jav_folder_new   # 【临时变量】新的影片所在文件夹。 当前文件夹的上级文件夹路径+新文件夹=新独立的文件夹的路径
                        # 确认没有同名文件夹
                        if not os.path.exists(root_separate_folder):
                            os.makedirs(root_separate_folder)
                        path_jav_new = root_separate_folder + sep + jav_file    # 【临时变量】新的影片路径。
                        if not os.path.exists(path_jav_new):  # 【防止错误】确认在这个文件夹内，没有“avop-127.mp4”。
                            os.rename(path_jav, path_jav_new)
                            root_now = root_separate_folder  # 【发生变化】root_now
                            path_jav = path_jav_new          # 【发生变化】path_jav
                            jav_folder = jav_folder_new      # 【发生变化】jav_folder
                            # 移动字幕
                            if subt_file:
                                os.rename(path_subt, root_separate_folder + sep + subt_file)
                                # 下面不会操作 字幕文件 了，字幕文件的路径不再更新
                                print('    >移动字幕到独立文件夹')
                        # avop-127白捡一个“avop-127”文件夹，可是里面已有“avop-127.mp4”，这不是它的家。
                        else:
                            num_fail += 1
                            record_fail('    >第' + str(num_fail) + '个失败！独立文件夹中已存在：' + path_jav_new + '\n')
                            continue  # 退出对该jav的整理

                # 更新一下path_relative
                path_relative = sep + path_jav.replace(root_choose, '')  # 影片的相对于所选文件夹的路径，用于报错

                # 4写入nfo开始
                if bool_nfo:
                    title_in_nfo = ''
                    for i in list_name_nfo_title:
                        title_in_nfo += dict_nfo[i]                     # nfo中tilte的写法
                    # 开始写入nfo，这nfo格式是参考的kodi的nfo
                    f = open(root_now + sep + jav_name + '.nfo', 'w', encoding="utf-8")
                    f.write("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\" ?>\n"
                            "<movie>\n"
                            "  <plot>" + plot + "</plot>\n"
                            "  <title>" + title_in_nfo + "</title>\n"
                            "  <rating>" + score + "</rating>\n"
                            "  <criticrating>" + criticrating + "</criticrating>\n"
                            "  <year>" + dict_nfo['发行年份'] + "</year>\n"
                            "  <mpaa>NC-17</mpaa>\n"                            
                            "  <customrating>NC-17</customrating>\n"
                            "  <countrycode>JP</countrycode>\n"
                            "  <premiered>" + time_premiered + "</premiered>\n"
                            "  <release>" + time_premiered + "</release>\n"
                            "  <runtime>" + dict_nfo['片长'] + "</runtime>\n"
                            "  <country>日本</country>\n"
                            "  <studio>" + studio + "</studio>\n"
                            "  <id>" + jav_num + "</id>\n"
                            "  <num>" + jav_num + "</num>\n")  # emby不管set系列，kodi可以
                    # 因为emby不直接显示片商，无视系列，所有把它们作为genre
                    for i in genres:
                        f.write("  <genre>" + i + "</genre>\n")
                        f.write("  <tag>" + i + "</tag>\n")
                    if bool_nfo_maker and studio:
                        f.write("  <genre>片商:" + studio + "</genre>\n")
                        f.write("  <tag>片商:" + studio + "</tag>\n")
                    if list_extra_genres:
                        for i in list_extra_genres:
                            f.write("  <genre>" + dict_nfo[i] + "</genre>\n")
                            f.write("  <tag>" + dict_nfo[i] + "</tag>\n")
                    f.write("  <actor>\n    <name>" + dict_nfo['首个演员'] + "</name>\n    <type>Actor</type>\n  </actor>\n")
                    f.write("</movie>\n")
                    f.close()
                    print('    >nfo收集完成')

                # 5需要两张图片
                if bool_jpg:
                    # 下载海报的地址 cover
                    # fanart和poster路径
                    path_fanart = root_now + sep
                    path_poster = root_now + sep
                    for i in list_name_fanart:
                        path_fanart += dict_nfo[i]
                    for i in list_name_poster:
                        path_poster += dict_nfo[i]
                    if jav_epi != 1:
                        copyfile(path_fanart.replace(str_cd, '-cd1'), path_fanart)
                        print('    >fanart.jpg复制成功')
                        copyfile(path_poster.replace(str_cd, '-cd1'), path_poster)
                        print('    >poster.jpg复制成功')
                    else:
                        # 下载 海报
                        list_cover[0] = 0
                        list_cover[1] = url_cover
                        list_cover[2] = path_fanart
                        # 已经去过javbus并找到封面
                        print('    >从jav321下载封面：', url_cover)
                        try:
                            download_pic(list_cover)
                            print('    >fanart.jpg下载成功')
                        except:
                            num_fail += 1
                            record_fail('    >第' + str(num_fail) + '个失败！下载fanart.jpg失败：' + url_cover + '，' + path_relative + '\n')
                            continue  # 退出对该jav的整理
                        if url_cover == url_poster:
                            # 裁剪生成 poster
                            img = Image.open(path_fanart)
                            wf, hf = img.size  # fanart的宽 高
                            wide = int(hf*0.666)
                            x_left = (wf-wide)/2
                            poster = img.crop((x_left, 0, x_left + wide, hf))
                            poster.save(path_poster, quality=95)  # quality=95 是无损crop，如果不设置，默认75
                            print('    >poster.jpg裁剪成功')
                        else:
                            # 下载poster.jpg
                            print('    >从jav321下载poster：', url_poster)
                            list_cover[0] = 0
                            list_cover[1] = url_poster
                            list_cover[2] = path_poster
                            try:
                                download_pic(list_cover)
                                print('    >poster.jpg下载成功')
                            except:
                                num_fail += 1
                                record_fail('    >第' + str(num_fail) + '个失败！poster下载失败：' + url_poster + '，' + path_relative + '\n')
                                continue

                # 7归类影片，针对文件夹
                if bool_classify and bool_classify_folder and jav_epi == num_all_episodes:
                    # 需要移动文件夹，且，是该影片的最后一集
                    if bool_separate_folder and root_classify.startswith(root):      # 用户选择的文件夹是一部影片的独立文件夹，为了避免在这个文件夹里又建立新的独立文件夹
                        print('    >无法归类，请选择该文件夹的上级目录作它的归类根目录')
                        continue   # 退出对该jav的整理
                    # 目标文件夹，暂时是现在的位置
                    root_dest = root_classify + sep
                    # 移动的目标文件夹
                    for j in list_classify_basis:
                        root_dest += dict_nfo[j].rstrip(' .')      # 【临时变量】 文件夹移动的目标上级文件夹  C:\Users\JuneRain\Desktop\测试文件夹\1\葵司\
                    root_now_new = root_dest + jav_folder          # 【临时变量】 文件夹移动的目标路径   C:\Users\JuneRain\Desktop\测试文件夹\1\葵司\【葵司】AVOP-127\
                    # print(root_now_new)
                    if not os.path.exists(root_now_new):
                        os.makedirs(root_now_new)
                        # 把现在文件夹里的东西都搬过去
                        jav_files = os.listdir(root_now)
                        for i in jav_files:
                            os.rename(root_now + sep + i, root_now_new + sep + i)
                        # 删除“旧房子”，这是javsdt唯一的删除操作，而且os.rmdir只能删除空文件夹
                        os.rmdir(root_now)
                        print('    >归类文件夹完成')
                    else:  # 用户已经有了这个车牌的文件夹
                        num_fail += 1
                        record_fail('    >第' + str(num_fail) + '个失败！归类失败，重复的影片，归类的目标目录已存在相同文件夹：' + root_now_new + '\n')
                        continue   # 退出对该jav的整理
            except:
                num_fail += 1
                record_fail('    >第' + str(num_fail) + '个失败！发生错误，如一直在该影片报错请截图并联系作者：' + path_relative + '\n' + format_exc() + '\n')
                continue   # 退出对该jav的整理

    # 完结撒花
    print('\n当前文件夹完成，', end='')
    if num_fail > 0:
        print('失败', num_fail, '个!  ', root_choose, '\n')
        line = -1
        with open('【记得清理它】失败记录.txt', 'r', encoding="utf-8") as f:
            content = list(f)
        while 1:
            if content[line].startswith('已'):
                break
            line -= 1
        for i in range(line+1, 0):
            print(content[i], end='')
        print('\n“【记得清理它】失败记录.txt”已记录错误\n')
    else:
        print('处理完成！“0”失败！', root_choose, '\n')
    # os.system('pause')
    input_start_key = input('回车继续选择文件夹整理：')
