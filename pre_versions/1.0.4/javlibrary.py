# -*- coding:utf-8 -*-
import os, time, re
from time import sleep
from re import findall
from re import search
from configparser import RawConfigParser
from shutil import copyfile
from traceback import format_exc
from functions import *


#  main开始
print('1、避开21:00-1:00，访问javlibrary和arzon很慢。\n'
      '2、若一直连不上javlibrary，请在ini中更新网址\n'
      '3、不要用www.javlibrary.com！用防屏蔽地址\n')
# 读取配置文件，这个ini文件用来给用户设置
print('正在读取ini中的设置...', end='')
try:
    config_settings = RawConfigParser()
    config_settings.read('【点我设置整理规则】.ini', encoding='utf-8-sig')
    # 是否 收集nfo
    bool_nfo = True if config_settings.get("收集nfo", "是否收集nfo？") == '是' else False
    # 是否 跳过已存在nfo的文件夹，不整理已有nfo的文件夹
    bool_skip = True if config_settings.get("收集nfo", "是否跳过已存在nfo的文件夹？") == '是' else False
    # 自定义 nfo中title的格式
    custom_nfo_title = config_settings.get("收集nfo", "nfo中title的格式")
    # 是否 去除标题末尾可能存在的演员姓名
    bool_strip_actors = True if config_settings.get("收集nfo", "是否去除标题末尾可能存在的演员姓名？") == '是' else False
    # 是否 是否将 系列 作为特征 因为emby不会直接在影片介绍页面上显示片商，也不会读取系列set，所有把它们作为特征
    bool_nfo_series = True if config_settings.get("收集nfo", "是否将系列作为特征？") == '是' else False
    # 是否 是否将 片商 作为特征
    bool_nfo_maker = True if config_settings.get("收集nfo", "是否将片商作为特征？") == '是' else False
    # 自定义 有些用户想把“发行年份”“影片类型”等其他元素作为特征
    custom_genres = config_settings.get("收集nfo", "额外将以下元素添加到特征中")
    # 是否 重命名 视频
    bool_rename_mp4 = True if config_settings.get("重命名影片", "是否重命名影片？") == '是' else False
    # 自定义 重命名 视频
    custom_video = config_settings.get("重命名影片", "重命名影片的格式")
    # 是否 重命名视频所在文件夹，或者为它创建独立文件夹
    bool_rename_folder = True if config_settings.get("修改文件夹", "是否重命名或创建独立文件夹？") == '是' else False
    # 自定义 新的文件夹名
    custom_folder = config_settings.get("修改文件夹", "新文件夹的格式")
    # 是否 重命名用户已拥有的字幕
    bool_rename_subt = True if config_settings.get("字幕文件", "是否重命名已有的字幕文件？") == '是' else False
    # 自定义 如果旧的nfo包含这些字符，则判定影片是“中字”
    custom_subt_nfo = config_settings.get("字幕文件", "已有字幕即nfo包含")
    # 是否 归类jav
    bool_classify = True if config_settings.get("归类影片", "是否归类影片？") == '是' else False
    # 是否 针对“文件夹”归类jav，“否”即针对“文件”
    bool_classify_folder = True if config_settings.get("归类影片", "针对文件还是文件夹？") == '文件夹' else False
    # 自定义 路径 归类的jav放到哪
    custom_root = config_settings.get("归类影片", "归类的根目录")
    # 自定义 标准 jav按什么类别来归类
    custom_classify_basis = config_settings.get("归类影片", "归类的标准")
    # 是否 下载图片
    bool_jpg = True if config_settings.get("下载封面", "是否下载封面海报？") == '是' else False
    # 自定义 命名 大封面fanart
    custom_fanart = config_settings.get("下载封面", "DVD封面的格式")
    # 自定义 命名 小封面poster
    custom_poster = config_settings.get("下载封面", "海报的格式")
    # 是否 收集演员头像
    bool_sculpture = True if config_settings.get("kodi专用", "是否收集演员头像？") == '是' else False
    # 是否 使用代理
    bool_proxy = True if config_settings.get("代理", "是否使用代理？") == '是' else False
    # IP端口 代理
    proxy = config_settings.get("代理", "代理IP及端口")
    # 是否 使用简体中文 简介翻译的结果和jav特征会变成“简体”还是“繁体”
    bool_zh = True if config_settings.get("其他设置", "简繁中文？") == '简' else False
    # 自定义 素人车牌 如果用户的视频名，在这些车牌中，才会去“jav321.com"整理
    custom_suren_pref = config_settings.get("信息来源", "列出车牌(素人为主，可自行添加)")
    # 自定义 文件类型 只有列举出的视频文件类型，才会被处理
    custom_file_type = config_settings.get("其他设置", "扫描文件类型")
    # 自定义 命名格式中“标题”的长度 windows只允许255字符，所以限制长度，但nfo中的标题是全部
    int_title_len = int(config_settings.get("其他设置", "重命名中的标题长度（50~150）"))
    # 自定义 原影片性质 影片有中文，体现在视频名称中包含这些字符
    custom_subt_video = config_settings.get("原影片文件的性质", "是否中字即文件名包含")
    # 自定义 是否中字 这个元素的表现形式
    custom_subt_expression = config_settings.get("原影片文件的性质", "是否中字的表现形式")
    # 自定义 原影片性质 影片有xx的性质，体现在视频名称中包含这些字符
    custom_xx_words = config_settings.get("原影片文件的性质", "是否xx即文件名包含")
    # 自定义 是否xx 这个元素的表现形式
    custom_xx_expression = config_settings.get("原影片文件的性质", "是否xx的表现形式")
    ######################################## 不同 ####################################################
    # 自定义 原影片性质 有码
    custom_movie_type = config_settings.get("原影片文件的性质", "有码")
    # 网址 javlibrary
    url_web = config_settings.get("其他设置", "javlibrary网址")
    # 网址 javbus
    url_bus = config_settings.get("其他设置", "javbus网址")
    # 是否 收集javlibrary下方用户超过10个人点赞的评论
    bool_review = True if config_settings.get("信息来源", "是否用javlibrary整理影片时收集网友的热评？") == '是' else False
    # 是否 收集“系列”
    bool_series = True if config_settings.get("信息来源", "是否用javlibrary整理影片时同样去javbus获取系列？") == '是' else False
    # 是否 需要简介
    bool_plot = True if config_settings.get("百度翻译API", "是否需要日语简介？") == '是' else False
    # 是否 把日语简介翻译为中文
    bool_tran = True if config_settings.get("百度翻译API", "是否翻译为中文？") == '是' else False
    # 账户 百度翻译api
    ID = config_settings.get("百度翻译API", "APP ID")
    SK = config_settings.get("百度翻译API", "密钥")
except:
    print(format_exc())
    print('\n无法读取ini文件，请修改它为正确格式，或者打开“【ini】重新创建ini.exe”创建全新的ini！')
    os.system('pause')

# 确认：演员头像ini及头像文件夹
if bool_sculpture:   # 需要为kodi整理头像
    if not os.path.exists('演员头像'):
        print('\n“演员头像”文件夹丢失！请把它放进exe的文件夹中！\n')
        os.system('pause')
    if not os.path.exists('【缺失的演员头像统计For Kodi】.ini'):
        config_actor = RawConfigParser()
        config_actor.add_section("缺失的演员头像")
        config_actor.set("缺失的演员头像", "演员姓名", "N(次数)")
        config_actor.add_section("说明")
        config_actor.set("说明", "上面的“演员姓名 = N(次数)”的表达式", "后面的N数字表示你有N部(次)影片都在找她的头像，可惜找不到")
        config_actor.set("说明", "你可以去保存一下她的头像jpg到“演员头像”文件夹", "以后就能保存她的头像到影片的文件夹了")
        config_actor.write(open('【缺失的演员头像统计For Kodi】.ini', "w", encoding='utf-8-sig'))
        print('\n    >“【缺失的演员头像统计For Kodi】.ini”文件丢失...正在重写ini...成功！')
        print('正在重新读取...', end='')
print('\n读取ini文件成功!')
# 代理设置
proxies = {"http": "http://" + proxy, "https": "https://" + proxy}
# 获得：arzon的cookie，通过成人验证
acook = {}
if bool_plot and bool_nfo:
    print('正在尝试通过“https://www.arzon.jp”的成人验证...')
    if bool_proxy and proxy != '':
        acook = get_acook(proxies, 0)
    else:
        acook = get_acook({}, 0)
    print('通过arzon的成人验证！\n')
# 确认：代理哪些站点
if bool_proxy and proxy != '':                   # 是否需要代理，设置请求时的状态
    list_jav = [0, '', '', proxies]              # 代理jav等网站
    list_arzon = [0, '', '', acook, proxies]     # 代理arzon
    list_cover = [0, '', '', proxies]            # 代理dmm图片源
else:
    list_jav = [0, '', '']
    list_arzon = [0, '', '', acook]
    list_cover = [0, '', '']
# 确认：归类影片本身还是它所在的文件夹，归类“文件（夹）”具有最高决定权
if bool_classify:                           # 如果需要归类
    if bool_classify_folder:                # 并且是针对文件夹
        bool_rename_folder = True           # 那么必须重命名文件夹或者创建新的文件夹
    else:
        bool_rename_folder = False          # 否则不会操作新文件夹
# 确认：jav网址，无论用户输不输人后面的斜杠 http://www.x39n.com/   https://www.buscdn.work/
if not url_web.endswith('/'):
    url_web += '/'
if not url_bus.endswith('/'):
    url_bus += '/'
# 确认：简/繁中文，影响影片特征和简介
if bool_zh:
    url_web += 'cn/'   # library显示简体中文
    t_lang = 'zh'          # 目标语言，百度翻译规定 zh是简体中文，cht是繁体中文
else:
    url_web += 'tw/'   # library显示繁体中文
    t_lang = 'cht'
# 初始化 其他
sep = os.sep  # 当前系统的路径分隔符 windows是“\”，linux和mac是“/”
# 存放影片信息，演员，标题等
dict_nfo = {'空格': ' ', '车牌': 'ABC-123', '标题': '有码标题', '完整标题': '完整标题', '导演': '有码导演',
            '发行年月日': '1970-01-01', '发行年份': '1970', '月': '01', '日': '01',
            '片商': '有码片商', '评分': '0', '首个演员': '有码演员', '全部演员': '有码演员',
            '片长': '0', '\\': sep, '/': sep, '是否中字': '', '视频': 'ABC-123', '车牌前缀': 'ABC',
            '是否xx': '', '影片类型': custom_movie_type, '系列': '有码系列',
            '原文件名': 'ABC-123', '原文件夹名': 'ABC-123', }
list_extra_genres = custom_genres.split('、') if custom_genres != '' else []  # 需要的额外特征
list_suren_num = custom_suren_pref.split('、')          # 素人番号的列表
list_rename_video = custom_video.split('+')             # 重命名视频的格式
list_rename_folder = custom_folder.split('+')           # 重命名文件夹的格式
tuple_type = tuple(custom_file_type.split('、'))        # 需要扫描的文件的类型
list_name_nfo_title = custom_nfo_title.replace('标题', '完整标题', 1).split('+')  # nfo中title的写法。给用户命名用的标题可能是删减的，nfo中的标题是完整标题
list_name_fanart = custom_fanart.split('+')            # fanart的格式
list_name_poster = custom_poster.split('+')            # poster的格式
list_subt_video = custom_subt_video.split('、')      # 包含哪些特殊含义的文字，判断是否中字
list_include_xx = custom_xx_words.split('、')          # 包含哪些特殊含义的文字，判断是否xx
list_subt_nfo = custom_subt_nfo.split('、')      # 包含哪些特殊含义的文字，判断是否中字
# 7+1个for，如果有什么高效简介的办法，请告诉我
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
    root_choose = get_directory()              # 用户选择的文件夹
    print(root_choose)
    # 在txt中记录一下用户的这次操作
    record_txt = open('【记得清理它】失败记录.txt', 'a', encoding="utf-8")
    record_txt.write('已选择文件夹：' + root_choose + ' ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + '\n')
    record_txt.close()
    print('...文件扫描开始...如果时间过长...请避开中午夜晚高峰期...\n')
    # 确认：归类根目录
    if bool_classify:
        custom_root = custom_root.rstrip(sep)
        # 归类根目录是用户输入的路径，继续核实合法性
        if custom_root != '所选文件夹':
            # ini中记录的“归类根目录”的路径不是“所选文件夹”
            if custom_root != root_choose:
                if custom_root[:2] != root_choose[:2]:
                    print('归类的根目录“', custom_root, '”和所选文件夹不在同一磁盘无法归类！请修正！')
                    os.system('pause')
                if not os.path.exists(custom_root):
                    print('归类的根目录“', custom_root, '”不存在！无法归类！请修正！')
                    os.system('pause')
                root_classify = custom_root.rstrip(sep)
            # 归类根目录就是用户所选的路径
            else:
                root_classify = root_choose + sep + '归类完成'
        # 用户使用默认的“归类完成”
        else:
            root_classify = root_choose + sep + '归类完成'
    # 初始化“失败信息”
    num_fail = 0                             # 计数 失败、警告的次数
    # root【当前根目录】 dirs【子目录】 files【文件】，root是字符串，后两个是list
    for root, dirs, files in os.walk(root_choose):
        if not files:
            continue                       # 【跳出此次root, dirs, files】
        if '归类完成' in root.replace(root_choose, ''):  # “当前目录”在“目标归类目录”中
            # print('>>该文件夹在归类的根目录中，跳过处理...', root)
            continue                       # 【跳出此次root, dirs, files】
        if bool_skip and len(files) > 1 and (files[-1].endswith('nfo') or files[-2].endswith('nfo')):
            # print(root+'sep+files[-1])    跳过已存在nfo的文件夹，判断这一层文件夹最后两个文件是不是nfo
            continue                       # 【跳出此次root, dirs, files】
        # 对这一层文件夹进行评估,有多少视频，有多少同车牌视频，是不是独立文件夹
        list_jav_videos = []               # 存放：需要整理的jav的结构体
        dict_car_pref = {}                 # 存放：这一层目录下的几个车牌 abp avop snis。。。{'abp': 1, avop': 2} abp只有一集，avop有cd1、cd2
        num_videos_include = 0             # 当前文件夹中视频的数量，可能有视频不是jav
        dict_subt_files = {}               # 存放：jav的字幕文件 {'c:\a\abc_123.srt': 'abc-123'}
        # 判断文件是不是字幕文件
        for file_raw in files:
            if file_raw.endswith(('.srt', '.vtt', '.ass', '.ssa', '.sub', '.smi',)):
                subt_num = search(r'([a-zA-Z]{2,7})[-_ ]*(\d{2,6})', file_raw)      # 字幕中含有的车牌，字幕车牌 和 视频车牌要配对
                if str(subt_num) != 'None':
                    jav_pref = subt_num.group(1).upper()
                    if jav_pref in list_suren_num:
                        continue     # 【跳出此次file_raw】
                    jav_suf = subt_num.group(2)
                    jav_num = jav_pref + '-' + jav_suf
                    dict_subt_files[file_raw] = jav_num
                continue             # 【跳出此次file_raw】
        # print(dict_subt_files)
        # 判断文件是不是视频，得到车牌号
        for file_raw in files:
            if file_raw.endswith(tuple_type) and not file_raw.startswith('.'):
                num_videos_include += 1
                video_numg = search(r'([a-zA-Z]{2,7})[-_ ]*(\d{2,6})', file_raw)     # 不是我吓唬你，真的有车牌带7个数字！
                if str(video_numg) != 'None':
                    jav_pref = video_numg.group(1).upper()
                    if jav_pref in list_suren_num:                                    # 如果这是素人影片，告诉一下用户，它们需要另外处理
                        print('>>跳过素人影片：' + root.replace(root_choose, '') + sep + file_raw)
                        continue     # 【跳出此次file_raw】
                    # 不是素人影片，继续
                    jav_suf = video_numg.group(2)
                    # 去掉太多的0，avop00127
                    if len(jav_suf) > 3:
                        jav_suf = jav_suf[:-3].lstrip('0') + jav_suf[-3:]
                    # jav_num 车牌
                    jav_num = jav_pref + '-' + jav_suf
                    # 这个车牌有几集？
                    try:
                        dict_car_pref[jav_num] += 1    # 已经有这个车牌了，加一集cd
                    except KeyError:
                        dict_car_pref[jav_num] = 1     # 这个新车牌有了第一集
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
                    continue     # 【跳出此次file_raw】
            else:
                continue         # 【跳出此次file_raw】
        # 判定影片所在文件夹是否是独立文件夹
        if dict_car_pref:  # 这一层文件夹下有jav
            if len(dict_car_pref) > 1 or num_videos_include > len(list_jav_videos) or exist_other_folders(dirs):
                # 当前文件夹下，车牌不止一个；还有其他非jav视频；有其他文件夹，除了演员头像文件夹“.actors”和额外剧照文件夹“extrafanart”；
                bool_separate_folder = False   # 不是独立的文件夹
            else:
                bool_separate_folder = True    # 这一层文件夹是这部jav的独立文件夹
        else:
            continue             # 【跳出此次root, dirs, files】
        # 正式开始
        # print(list_jav_videos)
        bool_already = False        # 这个车牌的信息还未查找，如果这是cd2，那么 cd1已经找过。
        for jav in list_jav_videos:
            jav_raw_num = jav.num   # 车牌  abc-123
            jav_file = jav.file     # 完整的原文件名  abc-123.mp4
            jav_epi = jav.episodes  # 这是第几集？一般都只有一集
            num_all_episodes = dict_car_pref[jav_raw_num]  # 该车牌总共多少集
            path_jav = root + sep + jav_file               # jav的起始路径
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

            # 获取nfo信息的javlibrary网页
            try:
                if '图书馆' in jav_file:
                    url_appointg = search(r'(javli.+?)\.', jav_file)
                    if str(url_appointg) != 'None':
                        url_search_web = url_web + '?v=' + url_appointg.group(1)
                    else:
                        num_fail += 1
                        record_fail('    >第' + str(num_fail) + '个失败！你指定的library网址有错误：' + path_relative + '\n')
                        continue        # 【退出对该jav的整理】
                else:
                    url_search_web = url_web + 'vl_searchbyid.php?keyword=' + jav_raw_num
                list_jav[0] = 0
                list_jav[1] = '    >打开javlibrary搜索页面失败，正在重新尝试...'
                list_jav[2] = url_search_web
                # 得到javlibrary搜索网页html
                html_web = get_library_html(list_jav)
                # 搜索结果的网页，大部分情况就是这个影片的网页，也有可能是多个结果的网页
                # 尝试找标题，第一种情况：找得到，就是这个影片的网页
                titleg = search(r'<title>([A-Z].+?) - JAVLibrary</title>', html_web)  # 匹配处理“标题”
                # 搜索结果就是AV的页面
                if str(titleg) != 'None':
                    title = titleg.group(1)
                # 第二种情况：搜索结果可能是两个以上，所以这种匹配找不到标题，None！
                else:   # 继续找标题，但匹配形式不同，这是找“可能是多个结果的网页”上的第一个标题
                    list_search_results = findall(r'v=javli(.+?)" title="(.+?-\d+?[a-z]? .+?)"', html_web)     # 这个正则表达式可以忽略avop-00127bod，它是近几年重置的，信息冗余
                    # os.system('pause')
                    # 搜索有几个结果，用第一个AV的网页，打开它
                    if list_search_results:
                        url_first_result = url_web + '?v=javli' + list_search_results[0][0]
                        # 在javlibrary上搜索 SSNI-589 SNIS-459 这两个车牌，你就能看懂下面的if
                        if len(list_search_results) > 1 and not list_search_results[1][1].endswith('ク）'):  # ク）是蓝光重置版
                            if list_search_results[0][1].endswith('ク）'):   # 排在第一个的是蓝光重置版，比如SSNI-589（ブルーレイディスク），它的封面不正常，跳过它
                                url_first_result = url_web + '?v=javli' + list_search_results[1][0]
                            elif list_search_results[1][1] == jav_raw_num:  # 不同的片，但车牌完全相同，比如id-020。警告用户，但默认用第一个结果。
                                num_fail += 1
                                record_fail('    >第' + str(num_fail) + '个警告！搜索页面：' + url_search_web + ' 上的有多个结果：' + path_relative + '\n')
                            # else: 还有一种情况，不同片，车牌也不同，但搜索到一堆，比如搜“AVOP-039”，还会得到“AVOP-390”，正确的肯定是第一个。
                        # 打开这个jav在library上的网页
                        list_jav[0] = 0
                        list_jav[1] = '    >打开影片在javlibrary上的网页失败，正在重新尝试...'
                        list_jav[2] = url_first_result
                        html_web = get_library_html(list_jav)
                        # 找到标题，留着马上整理信息用
                        title = search(r'<title>([A-Z].+?) - JAVLibrary</title>', html_web).group(1)
                    # 第三种情况：搜索不到这部影片，搜索结果页面什么都没有
                    else:
                        num_fail += 1
                        record_fail('    >第' + str(num_fail) + '个失败！javlibrary找不到影片信息：' + url_search_web + '，' + path_relative + '\n')
                        continue           # 【退出对该jav的整理】

                print('    >开始处理：', title)
                # 替换xml中的不允许的特殊字符 .replace('\'', '&apos;').replace('\"', '&quot;')
                # .replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')  nfo基于xml，xml中不允许这5个字符，但实际测试nfo只不允许左边3个
                title = title.replace('&', '和').replace("<", "[").replace(">", "]")\
                    .replace("\\", "#").replace("/", "#").replace(":", "：").replace("*", "#")\
                    .replace("?", "？").replace("\"", "#").replace("|", "#").replace('\n', '')\
                    .replace('\t', '').replace('\r', '').rstrip()  # 替换windows路径不允许的特殊字符 \/:*?"<>|
                # 正则匹配 影片信息 开始！
                # title的开头是车牌号，想要后面的纯标题
                car_titleg = search(r'(.+?) (.+)', title)
                # 车牌号
                jav_temp = car_titleg.group(1)
                # 在javlibrary中，T-28 和 ID 的车牌很奇特
                if 'T-28' in jav_temp:
                    jav_temp = jav_temp.replace('T-28', 'T28-', 1)
                elif 'ID-' in jav_temp:
                    jav_tempg = search(r'ID-(\d\d)(\d\d\d)', jav_temp)
                    if jav_tempg:
                        jav_temp = jav_tempg.group(1) + 'ID-' + jav_tempg.group(2)
                dict_nfo['车牌'] = jav_num = jav_temp                              # jav_num可能发生了变化
                dict_nfo['车牌前缀'] = jav_num.split('-')[0]
                # 给用户重命名用的标题是 短的title，nfo中是“完整标题”，但用户在ini中只用写“标题”
                title_only = car_titleg.group(2)     # 不包含车牌的标题
                # javlibrary的精彩影评   (.+?\s*.*?\s*.*?\s*.*?) 下面的匹配可能很奇怪，没办法，就这么奇怪
                review = ''
                if bool_review:
                    list_all_reviews = findall(
                        r'(textarea style="display: none;" class="hidden">[\s\S]*?scoreup">\d{2,})', html_web, re.DOTALL)
                    if list_all_reviews:
                        review = '【精彩影评】：'
                        for rev in list_all_reviews:
                            list_reviews = findall(r'hidden">([\s\S]*?)</textarea>', rev, re.DOTALL)
                            if list_reviews:
                                review = review + list_reviews[-1] + '////'
                        review = review.replace('&', '和').replace('<', '[').replace('>', ']') \
                            .replace('\n', '').replace('\t', '').replace('\r', '')
                # print(review)
                # 有大部分信息的html_web
                html_web = search(r'video_title"([\s\S]*?)favorite_edit', html_web, re.DOTALL).group(1)
                # DVD封面cover
                coverg = search(r'src="(.+?)" width="600', html_web)  # 封面图片的正则对象
                if str(coverg) != 'None':
                    url_cover = coverg.group(1)
                else:
                    url_cover = ''
                # 发行日期
                premieredg = search(r'(\d\d\d\d-\d\d-\d\d)', html_web)
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
                runtimeg = search(r'span class="text">(\d+?)</span>', html_web)
                if str(runtimeg) != 'None':
                    dict_nfo['片长'] = runtimeg.group(1)
                else:
                    dict_nfo['片长'] = '0'
                # 导演
                directorg = search(r'director\.php.+?>(.+?)<', html_web)
                if str(directorg) != 'None':
                    dict_nfo['导演'] = directorg.group(1)
                else:
                    dict_nfo['导演'] = '有码导演'
                # 片商 制作商
                studio = ''
                studiog = search(r'maker\.php.+?>(.+?)<', html_web)
                if str(studiog) != 'None':
                    dict_nfo['片商'] = studio = studiog.group(1).replace("\\", "#").replace("/", "#").replace(":", "：")\
                        .replace("*", "#").replace("?", "？").replace("\"", "#")
                else:
                    dict_nfo['片商'] = '有码片商'
                # 演员们 和 # 第一个演员
                actors = findall(r'star\.php.+?>(.+?)<', html_web)
                if actors:
                    if len(actors) > 7:
                        dict_nfo['全部演员'] = ' '.join(actors[:7])
                    else:
                        dict_nfo['全部演员'] = ' '.join(actors)
                    dict_nfo['首个演员'] = actors[0]
                    if bool_strip_actors and title_only.endswith(dict_nfo['全部演员']):
                        title_only = title_only[:-len(dict_nfo['全部演员'])].rstrip()
                else:
                    actors = ['有码演员']
                    dict_nfo['首个演员'] = dict_nfo['全部演员'] = '有码演员'
                # 处理影片的标题过长  给用户重命名用的标题是 短的title，nfo中是“完整标题”，但用户在ini中只用写“标题”
                dict_nfo['完整标题'] = title_only
                if len(title_only) > int_title_len:
                    dict_nfo['标题'] = title_only[:int_title_len]
                else:
                    dict_nfo['标题'] = title_only
                # 特点
                genres = findall(r'category tag">(.+?)<', html_web)
                if bool_subt:  # 有“中字“，加上特征”中文字幕”
                    genres.append('中文字幕')
                if dict_nfo['是否xx']:   # 有xx，加上特征custom_xx_expression
                    genres.append(custom_xx_expression)
                # print(genres)
                # 评分
                scoreg = search(r'score">\((.+?)\)<', html_web)
                if str(scoreg) != 'None':
                    float_score = float(scoreg.group(1))
                    float_score = (float_score - 4) * 5 / 3     # javlibrary上稍微有人关注的影片评分都是6分以上（10分制），强行把它差距拉大
                    if float_score >= 0:
                        score = '%.1f' % float_score
                    else:
                        score = '0'
                else:
                    score = '0'
                dict_nfo['评分'] = score
                # 烂番茄评分 用上面的评分*10
                criticrating = str(float(score)*10)
                # 最后再优化下标题  标题去除末尾的演员
                # arzon的简介 #########################################################
                plot = ''   # arzon上有极少量的“系列”，很少，几乎没有
                if bool_nfo and bool_plot:
                    url_search_arzon = 'https://www.arzon.jp/itemlist.html?t=&m=all&s=&q=' + jav_num
                    print('    >查找简介：', url_search_arzon)
                    list_arzon[0] = 0
                    list_arzon[1] = '    >打开arozn搜索页面失败，正在重新尝试...'
                    list_arzon[2] = url_search_arzon
                    # 得到arzon的搜索结果页面
                    html_search_arzon = get_arzon_html(list_arzon)
                    # <dt><a href="https://www.arzon.jp/item_1376110.html" title="限界集落 ～村民"><img src=
                    list_arzon_results = findall(r'<h2><a href="(/item.+?)" title=', html_search_arzon)  # 所有搜索结果链接
                    # 搜索结果为N个AV的界面
                    if list_arzon_results:  # arzon有搜索结果
                        num_results = len(list_arzon_results)
                        for i in range(num_results):
                            url_arzon_jav = 'https://www.arzon.jp' + list_arzon_results[i]  # 第i+1个链接
                            list_arzon[0] = 0
                            list_arzon[1] = '    >打开影片在arzon上的网页失败，正在重新尝试...'
                            list_arzon[2] = url_arzon_jav
                            # 打开arzon上每一个搜索结果的页面
                            html_arzon = get_arzon_html(list_arzon)
                            # 在该url_arzon_jav网页上查找简介
                            plotg = search(r'h2>作品紹介</h2>([\s\S]*?)</div>', html_arzon)
                            # 成功找到plot
                            if str(plotg) != 'None':
                                plot_br = plotg.group(1)
                                plot = ''
                                for line in plot_br.split('<br />'):
                                    line = line.strip()
                                    plot += line
                                plot = plot.replace('&', '和').replace('<', '[').replace('>', ']')\
                                    .replace('\n', '').replace('\t', '').replace('\r', '')
                                break
                        # 几个搜索结果查找完了，也没有找到简介
                        if plot == '':
                            plot = '【arzon有该影片，但找不到简介】'
                            num_fail += 1
                            record_fail('    >第' + str(num_fail) + '个失败！找不到简介，尽管arzon：' +
                                        url_search_arzon + '，有' + str(num_results) + '个搜索结果：' + path_relative + '\n')
                    # 没有搜索结果
                    else:
                        # arzon返回的页面实际是18岁验证
                        adultg = search(r'１８歳未満', html_search_arzon)
                        if str(adultg) != 'None':
                            num_fail += 1
                            record_fail('    >第' + str(num_fail) + '个失败！arzon成人验证失效，请重启程序：' + path_relative + '\n')
                            break
                        # 不是成人验证，也没有简介
                        else:
                            plot = '【影片下架，暂无简介】'
                            num_fail += 1
                            record_fail('    >第' + str(num_fail) + '个失败！arzon找不到该影片简介，可能被下架：' + url_search_arzon + '，' + path_relative + '\n')
                    if bool_tran:
                        plot = tran(ID, SK, plot, t_lang, 0)
                        if plot.startswith('【百度'):
                            num_fail += 1
                            record_fail('    >第' + str(num_fail) + '个失败！翻译简介失败：' + path_relative + '\n')
                #######################################################################
                series = url_cover_bus = ''
                dict_nfo['系列'] = '有码系列'
                if bool_nfo and bool_series:
                    print('    >查找javbus上的系列')
                    # 在javbus上找图片url
                    url_on_bus = url_bus + jav_num
                    list_jav[0] = 0
                    list_jav[1] = '    >打开影片在javbus上的网页失败，正在重新尝试...'
                    list_jav[2] = url_on_bus
                    # 获得影片在javbus上的网页
                    html_bus = get_bus_html(list_jav)
                    # DVD封面cover
                    coverg = search(r'bigImage" href="(.+?)">', html_bus)
                    if str(coverg) != 'None':
                        url_cover_bus = coverg.group(1)
                        # 系列:</span> <a href="https://www.cdnbus.work/series/kpl">悪質シロウトナンパ</a>
                        seriesg = search(r'系列:</span> <a href=".+?">(.+?)</a>', html_bus)
                        if str(seriesg) != 'None':
                            series = dict_nfo['系列'] = seriesg.group(1)
                    else:
                        # 获取nfo信息的javbus搜索网页  https://www.cdnbus.work/search/avop&type=&parent=ce
                        url_on_bus = url_bus + 'search/' + jav_num + '&type=1&parent=ce'
                        # print(url_on_bus)
                        list_jav[0] = 0
                        list_jav[1] = '    >打开影片在javbus上的网页失败，正在重新尝试...'
                        list_jav[2] = url_on_bus
                        html_bus = get_bus_html(list_jav)
                        # 搜索结果的网页，大部分情况一个结果，也有可能是多个结果的网页
                        # 尝试找movie-box
                        list_bus_results = findall(r'movie-box" href="(.+?)">', html_bus)  # 匹配处理“标题”
                        if len(list_bus_results):  # 搜索结果页面只有一个box
                            num_fail += 1
                            record_fail('    >第' + str(num_fail) + '个警告！系列可能错误，javbus上有多个搜索结果：' + url_on_bus + '，' + path_relative + '\n')
                            list_jav[0] = 0
                            list_jav[1] = '    >打开影片在javbus上的网页失败，正在重新尝试...'
                            list_jav[2] = list_bus_results[0]     # 默认用第一个
                            html_bus = get_bus_html(list_jav)
                            # DVD封面cover
                            coverg = search(r'bigImage" href="(.+?)">', html_bus)
                            if str(coverg) != 'None':
                                url_cover_bus = coverg.group(1)
                                # 系列:</span> <a href="https://www.cdnbus.work/series/kpl">悪質シロウトナンパ</a>
                                seriesg = search(r'系列:</span> <a href=".+?">(.+?)</a>', html_bus)
                                if str(seriesg) != 'None':
                                    series = dict_nfo['系列'] = seriesg.group(1)
                            else:
                                num_fail += 1
                                record_fail('    >第' + str(num_fail) + '个失败！查找系列失败，javbus上的链接：' + url_on_bus + ' ，请手动添加它的系列。\n')
                        else:
                            num_fail += 1
                            record_fail(
                                '    >第' + str(num_fail) + '个失败！查找系列失败，在javbus上找不到影片信息：' + url_on_bus + '，' + path_relative + '\n')
                #######################################################################
                # jav_name 是自始至终的 文件名（不带文件类型）  jav_file是自始至终的 文件名（完整带文件类型） root是原所在文件夹的路径  root_now 是现在（新）所在文件夹的路径
                # path_jav 是现在视频路径   path_subt是现在字幕路径   subt_file是 自始至终的 字幕文件名（带文件类型）  jav_folder是自始至终的 所在文件夹名（不是路径）
                dict_nfo['视频'] = dict_nfo['原文件名'] = jav_name                    # 【发生变化】 dict_nfo['视频']
                jav_folder = dict_nfo['原文件夹名'] = root.split(sep)[-1]  # 当前影片的目录名称，在下面的重命名操作中即将发生变化
                path_subt = root + sep + subt_file  # 字幕的起始路径
                root_now = root                     # 当前影片的目录路径
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
                    jav_name = jav_name.rstrip() + str_cd         # 【发生变化】jav_name  去除末尾空格，否则windows会自动删除空格，导致程序仍以为带空格
                    # 新的完整文件名，新的路径
                    dict_nfo['视频'] = jav_name                   # 【发生变化】 dict_nfo['视频']
                    jav_file = jav_name + video_type      # 【发生变化】jav_file
                    path_jav_new = root_now + sep + jav_file
                    # 理想状态下，还不存在目标文件
                    if not os.path.exists(path_jav_new):
                        # 重命名视频
                        os.rename(path_jav, path_jav_new)
                        path_jav = path_jav_new                  # 【发生变化】 path_jav
                    # 已存在目标文件，但就是现在的文件
                    elif path_jav.upper() == path_jav_new.upper():
                        try:
                            os.rename(path_jav, path_jav_new)
                            path_jav = path_jav_new  # 【发生变化】 path_jav
                        except:  # windows本地磁盘，“abc-123.mp4”重命名为“abc-123.mp4”或“ABC-123.mp4”没问题，但有用户反映，挂载的磁盘会报错“file exists error”
                            num_fail += 1
                            record_fail('    >第' + str(num_fail) + '个失败！请自行重命名：' + path_relative + '\n')
                    # 存在目标文件，不是现在的文件。
                    else:
                        num_fail += 1
                        record_fail(
                            '    >第' + str(num_fail) + '个失败！重命名影片失败，重复的影片，已经有相同文件名的视频了：' + path_jav_new + '\n')
                        continue  # 【退出对该jav的整理】
                    print('    >修改文件名' + str_cd + '完成')
                    # 重命名字幕
                    if subt_file and bool_rename_subt:
                        subt_file = jav_name + subt_type        # 【发生变化】 subt_file
                        path_subt_new = root_now + sep + subt_file
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
                        continue   # 【退出对该jav的整理】

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
                            # 同一车牌有n集，且这就是第n集，才会被重命名
                            list_root_now = root_now.split(sep)
                            del list_root_now[-1]
                            root_new = sep.join(list_root_now) + sep + jav_folder_new        # 【临时变量】新的影片路径。上级文件夹路径+新文件夹名称=新文件夹路径
                            if not os.path.exists(root_new):        # 【防止错误】目标影片文件夹不存在，或者目标影片文件夹存在，但就是现在的文件夹，即新旧相同
                                # 修改文件夹
                                os.rename(root_now, root_new)
                                root_now = root_new              # 【发生变化】root_now
                                path_jav = root_now + sep + jav_file                # 【发生变化】path_jav
                                jav_folder = jav_folder_new      # 【发生变化】jav_folder
                                print('    >重命名文件夹完成')
                            elif root_now == root_new:           # 【防止错误】新旧文件夹名 相同
                                pass
                            else:                                # 【防止错误】如果用户已经有一个“avop-127”的文件夹了，现在又要创建一个新的
                                num_fail += 1
                                record_fail('    >第' + str(num_fail) + '个失败！重命名文件夹失败，已存在相同文件夹：' + root_new + '\n')
                                continue                        # 【退出对该jav的整理】
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
                            record_fail('    >第' + str(num_fail) + '个失败！独立文件夹中已存在相同的视频文件：' + path_jav_new + '\n')
                            continue  # 【退出对该jav的整理】

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
                            "  <plot>" + plot + review + "</plot>\n"
                            "  <title>" + title_in_nfo + "</title>\n"
                            "  <director>" + dict_nfo['导演'] + "</director>\n"
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
                            "  <num>" + jav_num + "</num>\n"
                            "  <set>" + series + "</set>\n")  # emby不管set系列，kodi可以
                    for i in genres:
                        f.write("  <genre>" + i + "</genre>\n")
                        f.write("  <tag>" + i + "</tag>\n")
                    # 因为emby不直接显示片商，无视系列，所有把它们作为genre
                    if bool_nfo_series and series:
                        f.write("  <genre>系列:" + series + "</genre>\n")
                        f.write("  <tag>系列:" + series + "</tag>\n")
                    if bool_nfo_maker and studio:
                        f.write("  <genre>片商:" + studio + "</genre>\n")
                        f.write("  <tag>片商:" + studio + "</tag>\n")
                    if list_extra_genres:
                        for i in list_extra_genres:
                            f.write("  <genre>" + dict_nfo[i] + "</genre>\n")
                            f.write("  <tag>" + dict_nfo[i] + "</tag>\n")
                    for i in actors:
                        f.write("  <actor>\n    <name>" + i + "</name>\n    <type>Actor</type>\n  </actor>\n")
                    f.write("</movie>\n")
                    f.close()
                    print('    >nfo收集完成')

                # 5需要两张图片
                if bool_jpg:
                    # 下载海报的地址 cover    有一些图片dmm没了，是javlibrary自己的图片，缺少http
                    if not url_cover.startswith('http'):
                        url_cover = 'http:' + url_cover
                    # url_cover = url_cover.replace('pics.dmm.co.jp', 'jp.netcdn.space')    # 有人建议用avmoo的反代图片地址代替dmm
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
                        list_cover[2] = path_fanart
                        # 已经去过javbus并找到封面
                        if url_cover_bus and '图书馆' not in jav.file:
                            print('    >从javbus下载封面：', url_cover_bus)
                            list_cover[1] = url_cover_bus
                            try:
                                download_pic(list_cover)
                                print('    >fanart.jpg下载成功')
                            except:
                                print('    >从javbus下载fanart.jpg失败，正在前往javlibrary...')
                                # 还是用javlibrary的dmm图片
                                list_cover[0] = 0
                                list_cover[1] = url_cover
                                print('    >从javlibrary下载封面：', url_cover)
                                try:
                                    download_pic(list_cover)
                                    print('    >fanart.jpg下载成功')
                                except:
                                    num_fail += 1
                                    record_fail('    >第' + str(
                                        num_fail) + '个失败！下载fanart.jpg失败：' + url_cover + '，' + path_relative + '\n')
                                    continue     # 【退出对该jav的整理】
                        # 用户没有去javbus获取系列，或者指定“图书馆”网址，还是从javlibrary的dmm图片地址下载
                        else:
                            print('    >从javlibrary下载封面：', url_cover)
                            list_cover[1] = url_cover
                            try:
                                download_pic(list_cover)
                                print('    >fanart.jpg下载成功')
                            except:
                                print('    >从javlibrary下载fanart.jpg失败，正在前往javbus...')
                                # 在javbus上找图片url
                                url_on_bus = url_bus + jav_num
                                list_jav[0] = 0
                                list_jav[1] = '    >打开影片在javbus上的网页失败，正在重新尝试...'
                                list_jav[2] = url_on_bus
                                # 获得影片在javbus上的网页
                                html_bus = get_bus_html(list_jav)
                                # DVD封面cover
                                coverg = search(r'bigImage" href="(.+?)">', html_bus)
                                if str(coverg) != 'None':
                                    url_cover = coverg.group(1)
                                    list_cover[0] = 0
                                    list_cover[1] = url_cover
                                    print('    >从javbus下载封面：', url_cover)
                                    try:
                                        download_pic(list_cover)
                                        print('    >fanart.jpg下载成功')
                                    except:
                                        num_fail += 1
                                        record_fail('    >第' + str(
                                            num_fail) + '个失败！下载fanart.jpg失败：' + url_cover + '，' + path_relative + '\n')
                                        continue   # 【退出对该jav的整理】
                                else:
                                    num_fail += 1
                                    record_fail('    >第' + str(
                                        num_fail) + '个失败！下载javlibrary上的封面失败：' + url_cover + '，从javbus上查找封面失败：' + url_on_bus + '，' + path_relative + '\n')
                                    continue   # 【退出对该jav的整理】
                        # 裁剪生成 poster
                        img = Image.open(path_fanart)
                        wf, hf = img.size                        # fanart的宽 高
                        if wf > hf:  # 一般的800*536的图
                            x_left = int(wf*0.52625)                # 0.52625是海报宽（800-379）/800原长
                        else:  # 已经是竖直的海报了
                            x_left = 0
                        poster = img.crop((x_left, 0, wf, hf))       # 以fanart为坐标平面，坐标轴的y轴是反着的，（x_left, 0）是poster左上角，（wf, hf)是右下角
                        poster.save(path_poster, quality=95)   # quality=95 是无损crop，如果不设置，默认75
                        print('    >poster.jpg裁剪成功')

                # 6收集演员头像
                if bool_sculpture and jav_epi == 1:
                    if actors[0] == '有码演员':
                        print('    >有码演员，无法收集头像！')
                    else:
                        for each_actor in actors:
                            path_exist_actor = '演员头像' + sep + each_actor[0] + sep + each_actor + '.jpg'  # 事先准备好的演员头像路径
                            # print(path_exist_actor)
                            pic_type = '.jpg'
                            # 演员jpg图片还没有
                            if not os.path.exists(path_exist_actor):
                                path_exist_actor = '演员头像' + sep + each_actor[0] + sep + each_actor + '.png'
                                # 演员png图片还没有
                                if not os.path.exists(path_exist_actor):
                                    num_fail += 1
                                    record_fail('    >第' + str(num_fail) + '个失败！没有演员头像：' + each_actor + '，' + path_relative + '\n')
                                    config_actor = RawConfigParser()
                                    config_actor.read('【缺失的演员头像统计For Kodi】.ini', encoding='utf-8-sig')
                                    try:
                                        each_actor_times = config_actor.get('缺失的演员头像', each_actor)
                                        config_actor.set("缺失的演员头像", each_actor, str(int(each_actor_times) + 1))
                                    except:
                                        config_actor.set("缺失的演员头像", each_actor, '1')
                                    config_actor.write(open('【缺失的演员头像统计For Kodi】.ini', "w", encoding='utf-8-sig'))
                                    continue  # 【跳出此次 each_actor】
                                else:
                                    pic_type = '.png'
                            # 已经收录了这个演员头像
                            root_dest_actor = root_now + sep + '.actors' + sep   # 头像的目标目录
                            if not os.path.exists(root_dest_actor):
                                os.makedirs(root_dest_actor)
                            copyfile(path_exist_actor, root_dest_actor + each_actor + pic_type)       # 复制一份到“.actors”
                            print('    >演员头像收集完成：', each_actor)

                # 7归类影片，针对文件夹
                if bool_classify and bool_classify_folder and jav_epi == num_all_episodes:
                    # 需要移动文件夹，且，是该影片的最后一集
                    if bool_separate_folder and root_classify.startswith(root):      # 用户选择的文件夹是一部影片的独立文件夹，为了避免在这个文件夹里又建立新的独立文件夹
                        print('    >无法归类，请选择该文件夹的上级目录作它的归类根目录')
                        continue   # 【退出对该jav的整理】
                    # 目标文件夹，暂时是现在的位置
                    root_dest = root_classify + sep
                    # 移动的目标文件夹
                    for j in list_classify_basis:
                        root_dest += dict_nfo[j].rstrip(' .')      # 【临时变量】 文件夹移动的目标上级文件夹  C:\Users\JuneRain\Desktop\测试文件夹\1\葵司\
                    root_now_new = root_dest + jav_folder          # 【临时变量】 文件夹移动的目标路径   C:\Users\JuneRain\Desktop\测试文件夹\1\葵司\【葵司】AVOP-127\
                    # print(root_now_new)
                    # 确认 归类的目标路径 还没有这个车牌的文件夹
                    if not os.path.exists(root_now_new):
                        os.makedirs(root_now_new)
                        # 把现在文件夹里的东西都搬过去
                        jav_files = os.listdir(root_now)
                        for i in jav_files:
                            os.rename(root_now + sep + i, root_now_new + sep + i)
                        # 删除“旧房子”，这是javsdt唯一的删除操作，而且os.rmdir只能删除空文件夹
                        os.rmdir(root_now)
                        print('    >归类文件夹完成')
                    # 用户已经有了这个车牌的文件夹
                    else:
                        num_fail += 1
                        record_fail('    >第' + str(num_fail) + '个失败！归类失败，重复的影片，归类的目标目录已存在相同文件夹：' + root_now_new + '\n')
                        continue   # 【退出对该jav的整理】
            except:
                num_fail += 1
                record_fail('    >第' + str(num_fail) + '个失败！发生错误，如一直在该影片报错请截图并联系作者：' + path_relative + '\n' + format_exc() + '\n')
                continue     # 【退出对该jav的整理】

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
