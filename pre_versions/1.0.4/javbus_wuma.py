# -*- coding:utf-8 -*-
import os, time, re
from time import sleep
from re import findall
from re import search
from configparser import RawConfigParser
from shutil import copyfile
from traceback import format_exc
from functions import *
from aip import AipBodyAnalysis


#  main开始
print('1、避开21:00-1:00，访问javbus\n'
      '2、若一直连不上javbus，请在ini中更新网址\n'
      '3、不要用www.javbus.com！用防屏蔽地址\n'
      '4、无码影片没有简介\n'
      '5、找不到AV信息，请在javbus上确认，再修改本地视频文件名，如：\n'
      '   [JAV] [Uncensored] HEYZO 2171 [1080p].mp4 => HEYZO 2171.mp4\n'
      '   112314-742-carib-1080p.mp4 => 112314-742.mp4\n'
      '   Heyzo_HD_0733_full.mp4 => Heyzo_0733.mp4\n'
      '   Heyzo_0733_01.mp4 => Heyzo_0733啊.mp4\n'
      '   Heyzo_0733_02.mp4 => Heyzo_0733吧.mp4\n')
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
    # 是否 去除标题末尾可能存在的演员姓名
    bool_strip_actors = True if config_settings.get("收集nfo", "是否去除标题末尾可能存在的演员姓名？") == '是' else False
    # 是否 是否将 系列 作为特征 因为emby不会直接在影片介绍页面上显示片商，也不会读取系列set，所有把它们作为特征
    bool_nfo_series = True if config_settings.get("收集nfo", "是否将系列作为特征？") == '是' else False
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
    # 是否 收集演员头像
    bool_sculpture = True if config_settings.get("kodi专用", "是否收集演员头像？") == '是' else False
    # 是否 使用代理
    bool_proxy = True if config_settings.get("代理", "是否使用代理？") == '是' else False
    # IP端口 代理
    proxy = config_settings.get("代理", "代理IP及端口")
    # 素人车牌 如果用户的视频名，在这些车牌中，才会去“jav321.com"整理
    custom_suren_pref = config_settings.get("信息来源", "列出车牌(素人为主，可自行添加)")
    # 是否 使用简体中文 简介翻译的结果和jav特征会变成“简体”还是“繁体”
    bool_zh = True if config_settings.get("其他设置", "简繁中文？") == '简' else False
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
    ######################################## 不同之处 ####################################################
    # 原影片性质 马场
    custom_movie_type = config_settings.get("原影片文件的性质", "无码")
    # 网址 javbus
    url_web = config_settings.get("其他设置", "javbus网址")
    # 无视的字母数字 去除影响搜索结果的字母数字 full、tokyohot、
    custom_surplus_words = config_settings.get("原影片文件的性质", "无视无码视频文件名中多余的字母数字")
    # 是否 需要准确定位人脸的poster
    bool_face = True if config_settings.get("百度人体分析", "是否需要准确定位人脸的poster？") == '是' else False
    # 账户 百度人体分析
    ID = config_settings.get("百度人体分析", "appid")
    AK = config_settings.get("百度人体分析", "api key")
    SK = config_settings.get("百度人体分析", "secret key")
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
# 使用人体分析
if bool_face:
    client = AipBodyAnalysis(ID, AK, SK)
# 代理设置
proxies = {"http": "http://" + proxy, "https": "https://" + proxy}
# 确认：代理哪些站点
if bool_proxy and proxy != '':      # 是否需要代理，设置请求时的状态
    list_jav = [0, '', '', proxies]              # 代理jav等网站
    list_cover = [0, '', '', proxies]     # 代理dmm图片原
else:
    list_jav = [0, '', '']
    list_cover = [0, '', '']
# 确认：归类影片本身还是它所在的文件夹，归类“文件（夹）”具有最高决定权
if bool_classify:            # 如果需要归类
    if bool_classify_folder:    # 并且是针对文件夹
        bool_rename_folder = True           # 那么必须重命名文件夹或者创建新的文件夹
    else:
        bool_rename_folder = False           # 否则不会操作新文件夹
# 确认：jav网址，无论用户输不输人后面的斜杠 https://www.buscdn.work/
if not url_web.endswith('/'):
    url_web += '/'
# 确认：简/繁中文，影响影片特征和简介
if bool_zh:
    t_lang = 'zh'          # 目标语言，百度翻译规定 zh是简体中文，cht是繁体中文
else:
    t_lang = 'cht'
# 初始化其他
sep = os.sep  # 当前系统的路径分隔符 windows是“\”，linux和mac是“/”
# 存放影片信息，演员，标题等
dict_nfo = {'空格': ' ', '车牌': 'ABC-123', '标题': '无码标题', '完整标题': '完整标题', '导演': '无码导演',
            '发行年月日': '1970-01-01', '发行年份': '1970', '月': '01', '日': '01',
            '片商': '无码片商', '评分': '0', '首个演员': '无码演员', '全部演员': '无码演员',
            '片长': '0', '\\': sep, '/': sep, '是否中字': '', '视频': 'ABC-123', '车牌前缀': 'ABC',
            '是否xx': '', '影片类型': custom_movie_type, '系列': '无码系列',
            '原文件名': 'ABC-123', '原文件夹名': 'ABC-123', }

list_extra_genres = custom_genres.split('、') if custom_genres != '' else []   # 需要的额外特征
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
list_surplus_words = custom_surplus_words.split('、')      # 包含哪些特殊含义的文字，判断是否中字
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
# 特点，繁转简
gen_dict = {'中文字幕': '中文字幕', custom_xx_expression: custom_xx_expression,
            '高清': 'XXXX', '字幕': 'XXXX', '推薦作品': '推荐作品', '通姦': '通奸', '淋浴': '淋浴', '舌頭': '舌头',
            '下流': '下流', '敏感': '敏感', '變態': '变态', '願望': '愿望', '慾求不滿': '慾求不满', '服侍': '服侍',
            '外遇': '外遇', '訪問': '访问', '性伴侶': '性伴侣', '保守': '保守', '購物': '购物', '誘惑': '诱惑',
            '出差': '出差', '煩惱': '烦恼', '主動': '主动', '再會': '再会', '戀物癖': '恋物癖', '問題': '问题',
            '騙奸': '骗奸', '鬼混': '鬼混', '高手': '高手', '順從': '顺从', '密會': '密会', '做家務': '做家务',
            '秘密': '秘密', '送貨上門': '送货上门', '壓力': '压力', '處女作': '处女作', '淫語': '淫语', '問卷': '问卷',
            '住一宿': '住一宿', '眼淚': '眼泪', '跪求': '跪求', '求職': '求职', '婚禮': '婚礼', '第一視角': '第一视角',
            '洗澡': '洗澡', '首次': '首次', '劇情': '剧情', '約會': '约会', '實拍': '实拍', '同性戀': '同性恋',
            '幻想': '幻想', '淫蕩': '淫荡', '旅行': '旅行', '面試': '面试', '喝酒': '喝酒', '尖叫': '尖叫',
            '新年': '新年', '借款': '借款', '不忠': '不忠', '檢查': '检查', '羞恥': '羞耻', '勾引': '勾引',
            '新人': '新人', '推銷': '推销', 'ブルマ': '运动短裤',

            'AV女優': 'AV女优', '情人': '情人', '丈夫': '丈夫', '辣妹': '辣妹', 'S級女優': 'S级女优', '白領': '白领',
            '偶像': '偶像', '兒子': '儿子', '女僕': '女仆', '老師': '老师', '夫婦': '夫妇', '保健室': '保健室',
            '朋友': '朋友', '工作人員': '工作人员', '明星': '明星', '同事': '同事', '面具男': '面具男', '上司': '上司',
            '睡眠系': '睡眠系', '奶奶': '奶奶', '播音員': '播音员', '鄰居': '邻居', '親人': '亲人', '店員': '店员',
            '魔女': '魔女', '視訊小姐': '视讯小姐', '大學生': '大学生', '寡婦': '寡妇', '小姐': '小姐', '秘書': '秘书',
            '人妖': '人妖', '啦啦隊': '啦啦队', '美容師': '美容师', '岳母': '岳母', '警察': '警察', '熟女': '熟女',
            '素人': '素人', '人妻': '人妻', '痴女': '痴女', '角色扮演': '角色扮演', '蘿莉': '萝莉', '姐姐': '姐姐',
            '模特': '模特', '教師': '教师', '學生': '学生', '少女': '少女', '新手': '新手', '男友': '男友',
            '護士': '护士', '媽媽': '妈妈', '主婦': '主妇', '孕婦': '孕妇', '女教師': '女教师', '年輕人妻': '年轻人妻',
            '職員': '职员', '看護': '看护', '外觀相似': '外观相似', '色狼': '色狼', '醫生': '医生', '新婚': '新婚',
            '黑人': '黑人', '空中小姐': '空中小姐', '運動系': '运动系', '女王': '女王', '西裝': '西装', '旗袍': '旗袍',
            '兔女郎': '兔女郎', '白人': '白人',

            '制服': '制服', '內衣': '内衣', '休閒裝': '休閒装', '水手服': '水手服', '全裸': '全裸', '不穿內褲': '不穿内裤',
            '和服': '和服', '不戴胸罩': '不戴胸罩', '連衣裙': '连衣裙', '打底褲': '打底裤', '緊身衣': '紧身衣', '客人': '客人',
            '晚禮服': '晚礼服', '治癒系': '治癒系', '大衣': '大衣', '裸體襪子': '裸体袜子', '絲帶': '丝带', '睡衣': '睡衣',
            '面具': '面具', '牛仔褲': '牛仔裤', '喪服': '丧服', '極小比基尼': '极小比基尼', '混血': '混血', '毛衣': '毛衣',
            '頸鏈': '颈链', '短褲': '短裤', '美人': '美人', '連褲襪': '连裤袜', '裙子': '裙子', '浴衣和服': '浴衣和服',
            '泳衣': '泳衣', '網襪': '网袜', '眼罩': '眼罩', '圍裙': '围裙', '比基尼': '比基尼', '情趣內衣': '情趣内衣',
            '迷你裙': '迷你裙', '套裝': '套装', '眼鏡': '眼镜', '丁字褲': '丁字裤', '陽具腰帶': '阳具腰带', '男装': '男装',
            '襪': '袜',

            '美肌': '美肌', '屁股': '屁股', '美穴': '美穴', '黑髮': '黑发', '嬌小': '娇小', '曬痕': '晒痕',
            'F罩杯': 'F罩杯', 'E罩杯': 'E罩杯', 'D罩杯': 'D罩杯', '素顏': '素颜', '貓眼': '猫眼', '捲髮': '捲发',
            '虎牙': '虎牙', 'C罩杯': 'C罩杯', 'I罩杯': 'I罩杯', '小麥色': '小麦色', '大陰蒂': '大阴蒂', '美乳': '美乳',
            '巨乳': '巨乳', '豐滿': '丰满', '苗條': '苗条', '美臀': '美臀', '美腿': '美腿', '無毛': '无毛',
            '美白': '美白', '微乳': '微乳', '性感': '性感', '高個子': '高个子', '爆乳': '爆乳', 'G罩杯': 'G罩杯',
            '多毛': '多毛', '巨臀': '巨臀', '軟體': '软体', '巨大陽具': '巨大阳具', '長發': '长发', 'H罩杯': 'H罩杯',


            '舔陰': '舔阴', '電動陽具': '电动阳具', '淫亂': '淫乱', '射在外陰': '射在外阴', '猛烈': '猛烈', '後入內射': '后入内射',
            '足交': '足交', '射在胸部': '射在胸部', '側位內射': '侧位内射', '射在腹部': '射在腹部', '騎乘內射': '骑乘内射', '射在頭髮': '射在头发',
            '母乳': '母乳', '站立姿勢': '站立姿势', '肛射': '肛射', '陰道擴張': '阴道扩张', '內射觀察': '内射观察', '射在大腿': '射在大腿',
            '精液流出': '精液流出', '射在屁股': '射在屁股', '內射潮吹': '内射潮吹', '首次肛交': '首次肛交', '射在衣服上': '射在衣服上', '首次內射': '首次内射',
            '早洩': '早洩', '翻白眼': '翻白眼', '舔腳': '舔脚', '喝尿': '喝尿', '口交': '口交', '內射': '内射',
            '自慰': '自慰', '後入': '后入', '騎乘位': '骑乘位', '顏射': '颜射', '口內射精': '口内射精', '手淫': '手淫',
            '潮吹': '潮吹', '輪姦': '轮奸', '亂交': '乱交', '乳交': '乳交', '小便': '小便', '吸精': '吸精',
            '深膚色': '深肤色', '指法': '指法', '騎在臉上': '骑在脸上', '連續內射': '连续内射', '打樁機': '打桩机', '肛交': '肛交',
            '吞精': '吞精', '鴨嘴': '鸭嘴', '打飛機': '打飞机', '剃毛': '剃毛', '站立位': '站立位', '高潮': '高潮',
            '二穴同入': '二穴同入', '舔肛': '舔肛', '多人口交': '多人口交', '痙攣': '痉挛', '玩弄肛門': '玩弄肛门', '立即口交': '立即口交',
            '舔蛋蛋': '舔蛋蛋', '口射': '口射', '陰屁': '阴屁', '失禁': '失禁', '大量潮吹': '大量潮吹', '69': '69',

            '振動': '振动', '搭訕': '搭讪', '奴役': '奴役', '打屁股': '打屁股', '潤滑油': '润滑油',
            '按摩': '按摩', '散步': '散步', '扯破連褲襪': '扯破连裤袜', '手銬': '手铐', '束縛': '束缚', '調教': '调教',
            '假陽具': '假阳具', '變態遊戲': '变态游戏', '注視': '注视', '蠟燭': '蜡烛', '電鑽': '电钻', '亂搞': '乱搞',
            '摩擦': '摩擦', '項圈': '项圈', '繩子': '绳子', '灌腸': '灌肠', '監禁': '监禁', '車震': '车震',
            '鞭打': '鞭打', '懸掛': '悬挂', '喝口水': '喝口水', '精液塗抹': '精液涂抹', '舔耳朵': '舔耳朵', '女體盛': '女体盛',
            '便利店': '便利店', '插兩根': '插两根', '開口器': '开口器', '暴露': '暴露', '陰道放入食物': '阴道放入食物', '大便': '大便',
            '經期': '经期', '惡作劇': '恶作剧', '電動按摩器': '电动按摩器', '凌辱': '凌辱', '玩具': '玩具', '露出': '露出',
            '肛門': '肛门', '拘束': '拘束', '多P': '多P', '潤滑劑': '润滑剂', '攝影': '摄影', '野外': '野外',
            '陰道觀察': '阴道观察', 'SM': 'SM', '灌入精液': '灌入精液', '受虐': '受虐', '綁縛': '绑缚', '偷拍': '偷拍',
            '異物插入': '异物插入', '電話': '电话', '公寓': '公寓', '遠程操作': '远程操作', '偷窺': '偷窥', '踩踏': '踩踏',
            '無套': '无套',

            '企劃物': '企划物', '獨佔動畫': '独佔动画', '10代': '10代', '1080p': 'XXXX', '人氣系列': '人气系列', '60fps': 'XXXX',
            '超VIP': '超VIP', '投稿': '投稿', 'VIP': 'VIP', '椅子': '椅子', '風格出眾': '风格出众', '首次作品': '首次作品',
            '更衣室': '更衣室', '下午': '下午', 'KTV': 'KTV', '白天': '白天', '最佳合集': '最佳合集', 'VR': 'VR',
            '動漫': '动漫',

            '酒店': '酒店', '密室': '密室', '車': '车', '床': '床', '陽台': '阳台', '公園': '公园',
            '家中': '家中', '公交車': '公交车', '公司': '公司', '門口': '门口', '附近': '附近', '學校': '学校',
            '辦公室': '办公室', '樓梯': '楼梯', '住宅': '住宅', '公共廁所': '公共厕所', '旅館': '旅馆', '教室': '教室',
            '廚房': '厨房', '桌子': '桌子', '大街': '大街', '農村': '农村', '和室': '和室', '地下室': '地下室',
            '牢籠': '牢笼', '屋頂': '屋顶', '游泳池': '游泳池', '電梯': '电梯', '拍攝現場': '拍摄现场', '別墅': '别墅',
            '房間': '房间', '愛情旅館': '爱情旅馆', '車內': '车内', '沙發': '沙发', '浴室': '浴室', '廁所': '厕所',
            '溫泉': '温泉', '醫院': '医院', '榻榻米': '榻榻米'}                   # 特点，繁转简

# 用户输入“回车”就继续选择文件夹整理
input_start_key = ''
while input_start_key == '':
    # 用户选择文件夹
    print('请选择要整理的文件夹：', end='')
    root_choose = get_directory()  # 用户选择的文件夹
    print(root_choose)
    # 在txt中记录一下用户的这次操作
    record_txt = open('【记得清理它】失败记录.txt', 'a', encoding="utf-8")
    record_txt.write('已选择文件夹：' + root_choose + ' ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + '\n')
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
        if '归类完成' in root.replace(root_choose, ''):  # 跳过“归类完成”文件夹
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
                if 'fc2' in file_raw or 'FC2' in file_raw:
                    continue
                file_temp = file_raw
                for word in list_surplus_words:
                    file_temp = file_temp.replace(word, '')
                subt_num = search(r'([a-zA-Z0-9]+)[-_ ]*([a-zA-Z0-9]+[-_ ]*\d*)', file_temp)  # 字幕中含有的车牌，字幕车牌 和 视频车牌要配对
                if str(subt_num) != 'None':
                    jav_pref = subt_num.group(1).upper()
                    if jav_pref in list_suren_num:
                        continue     # 跳出此次file_raw
                    jav_suf = subt_num.group(2)
                    jav_num = jav_pref + '-' + jav_suf.rstrip()
                    dict_subt_files[file_raw] = jav_num
                continue            # 跳出此次file_raw
        # print(dict_subt_files)
        # 判断文件是不是视频，得到车牌号
        for file_raw in files:
            if file_raw.endswith(tuple_type) and not file_raw.startswith('.'):
                if 'fc2' in file_raw or 'FC2' in file_raw:
                    continue
                num_videos_include += 1
                file_temp = file_raw
                for word in list_surplus_words:
                    file_temp = file_temp.replace(word, '')
                video_numg = search(r'([a-zA-Z0-9]+)[-_ ]*([a-zA-Z0-9]+[-_ ]*\d*)', file_temp)    # 这个正则表达式匹配“车牌号”可能有点奇怪，
                if str(video_numg) != 'None':                               # 如果你下过上千部片，各种参差不齐的命名，你就会理解我了。
                    jav_pref = video_numg.group(1).upper()
                    if jav_pref in list_suren_num:  # 如果这是素人影片，告诉一下用户，它们需要另外处理
                        print('>>跳过素人影片：' + root.replace(root_choose, '') + sep + file_raw)
                        continue     # 跳出此次file_raw       素人影片不参与下面的整理
                    # 不是素人影片，继续
                    jav_suf = video_numg.group(2).rstrip()
                    # jav_num 车牌
                    jav_num = jav_pref + '-' + jav_suf.rstrip()
                    jav_search = jav_num.replace('-', '%20').replace('_', '%20')
                    # 这个车牌有几集？
                    try:
                        dict_car_pref[jav_num] += 1  # 已经有这个车牌了，加一集cd
                    except KeyError:
                        dict_car_pref[jav_num] = 1  # 这个新车牌有了第一集
                    # 把这个jav的各种属性打包好
                    jav_struct = JavFile()
                    jav_struct.num = jav_num           # 车牌
                    jav_struct.search = jav_search     # # 用于搜索的车牌，javbus处理不了“-”“_”，把这两个换成了“%20”
                    jav_struct.file = file_raw         # 原文件名
                    jav_struct.episodes = dict_car_pref[jav_num]  # 这个jav视频，是第几集  {'abp': 1, avop': 2}
                    if jav_num in dict_subt_files.values():
                        jav_struct.subt = list(dict_subt_files.keys())[list(dict_subt_files.values()).index(jav_num)]
                        del dict_subt_files[jav_struct.subt]
                    list_jav_videos.append(jav_struct)
                else:
                    continue     # 跳出此次file_raw
            else:
                continue       # 跳出此次file_raw
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
        # print(list_jav_videos)
        # 这个车牌的信息还未查找
        bool_already = False
        for jav in list_jav_videos:
            jav_search = jav.search  # 搜素用的车牌  abc%20123
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
                # 搜索获取nfo信息的javbus网页
                if '公交车' not in jav_file:
                    url_search_web = url_web + 'uncensored/search/' + jav_search + '&type=&parent=uc'
                    list_jav[0] = 0
                    list_jav[1] = '    >打开javbus无码搜索页面失败，正在重新尝试...'
                    list_jav[2] = url_search_web
                    # 得到javbus搜索网页html
                    html_web = get_bus_html(list_jav)
                    # 搜索结果的网页，大部分情况就是这个影片的网页，也有可能是多个结果的网页
                    # 尝试找movie-box
                    list_search_results = findall(r'movie-box" href="(.+?)">', html_web)  # 匹配处理“标题”
                    if len(list_search_results) == 1:  # 搜索结果页面只有一个box
                        url_on_web = list_search_results[0]
                    elif len(list_search_results) > 1:  # 找到不止一个box
                        # print(list_search_results)
                        print('    >该车牌：' + jav_raw_num + ' 搜索到多个结果，正在尝试精确定位...')
                        jav_pref = jav_search.split('%20')[0]  # 匹配车牌的前缀字母
                        jav_suf = jav_search.split('%20')[-1].lstrip('0')  # 当前车牌的后缀数字 去除多余的0
                        list_fit_results = []
                        for i in list_search_results:
                            url_end = i.split('/')[-1]
                            url_suf = search(r'[^\d](\d\d+)', url_end).group(1).lstrip('0')  # 匹配box上影片url，车牌的后缀数字，去除多余的0
                            if jav_suf == url_suf:  # 数字相同
                                url_pref = search(r'([a-zA-Z0-9]+)[-_\d]', url_end).group(1).upper()  # 匹配处理url所带车牌前面的字母“n”
                                if jav_pref == url_pref:  # 数字相同的基础下，字母也相同，即可能车牌相同
                                    list_fit_results.append(i)
                        # 无码搜索的结果一个都匹配不上
                        if not list_fit_results:
                            num_fail += 1
                            record_fail('    >第' + str(
                                num_fail) + '个失败！多个搜索结果也找不到AV信息：' + url_search_web + '，' + path_relative + '\n')
                            continue
                        url_on_web = list_fit_results[0]
                        # print('最终链接：', url_on_web)
                        # print('最终list：', list_fit_results)
                        if len(list_fit_results) > 1:
                            num_fail += 1
                            record_fail('    >第' + str(
                                num_fail) + '个警告！从多个搜索结果中确定为：' + url_on_web + '，' + path_relative + '\n')
                    # 找不到box
                    else:
                        list_jav[0] = 0
                        list_jav[1] = '    >打开javbus有码搜索页面失败，正在重新尝试...'
                        list_jav[2] = url_web + 'search/' + jav_search + '&type=1&parent=ce'
                        # print(list_jav[2])
                        # 得到javbus搜索网页html
                        html_web = get_bus_html(list_jav)
                        # 尝试找movie-box
                        list_search_results = findall(r'movie-box" href="(.+?)">', html_web)  # 匹配处理“标题”
                        if list_search_results:  # 搜索结果页面只有一个box
                            print('    >跳过有码影片：', path_relative)
                            continue
                        else:
                            num_fail += 1
                            record_fail('    >第' + str(
                                num_fail) + '个失败！javbus有码无码都找不到AV信息：' + url_search_web + '，' + path_relative + '\n')
                            continue
                # 用户指定javbus上的网页
                else:
                    url_appointg = search(r'公交车(.+?)\.', jav_file)
                    if str(url_appointg) != 'None':
                        url_on_web = url_web + url_appointg.group(1)
                    else:
                        num_fail += 1
                        record_fail('    >第' + str(num_fail) + '个失败！你指定的javbus网址有错误：' + path_relative + '\n')
                        continue  # 跳出这次整理
                # 经过上面的三种情况，可能找到了jav在bus上的网页链接url_on_web
                list_jav[0] = 0
                list_jav[1] = '    >打开jav所在页面失败，正在重新尝试...'
                list_jav[2] = url_on_web
                # 得到最终的jav所在网页
                html_web = get_bus_html(list_jav)

                # 开始匹配信息
                # 有大部分信息的html_web
                html_web = search(r'(h3>[\s\S]*?)磁力連結投稿', html_web, re.DOTALL).group(1)
                # print(html_web)
                # 标题
                title = search(r'h3>(.+?)</h3', html_web, re.DOTALL).group(1)  # javbus上的标题可能占两行
                # 替换xml中的不允许的特殊字符 .replace('\'', '&apos;').replace('\"', '&quot;')
                # .replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')  nfo基于xml中不允许这5个字符，但实际测试只不允许左边3个
                title = title.replace('&', '和').replace("<", "[").replace(">", "]")\
                    .replace("\\", "#").replace("/", "#").replace(":", "：").replace("*", "#")\
                    .replace("?", "？").replace("\"", "#").replace("|", "#").replace('\n', '')\
                    .replace('\t', '').replace('\r', '').rstrip()  # 替换windows路径不允许的特殊字符 \/:*?"<>|
                print('    >开始处理：', title)
                # 正则匹配 影片信息 开始！
                # title的开头是车牌号，想要后面的纯标题
                car_titleg = search(r'(.+?) (.+)', title)
                # 车牌号
                dict_nfo['车牌'] = jav_num = car_titleg.group(1)
                dict_nfo['车牌前缀'] = jav_num.split('-', )[0]                # 无码的车牌不一定有‘-’，这个问题没有解决
                # 给用户重命名用的标题是 短的title，nfo中是“完整标题”，但用户在ini中只用写“标题”
                title_only = car_titleg.group(2)
                # DVD封面cover
                coverg = search(r'bigImage" href="(.+?)">', html_web)  # 封面图片的正则对象
                if str(coverg) != 'None':
                    url_cover = coverg.group(1)
                else:
                    url_cover = ''
                # 发行日期
                premieredg = search(r'發行日期:</span> (.+?)</p>', html_web)
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
                runtimeg = search(r'長度:</span> (.+?)分鐘</p>', html_web)
                if str(runtimeg) != 'None':
                    dict_nfo['片长'] = runtimeg.group(1)
                else:
                    dict_nfo['片长'] = '0'
                # 导演
                directorg = search(r'導演:</span> <a href=".+?">(.+?)<', html_web)
                if str(directorg) != 'None':
                    dict_nfo['导演'] = directorg.group(1)
                else:
                    dict_nfo['导演'] = '无码导演'
                # 片商 制作商
                studio = ''
                studiog = search(r'製作商:</span> <a href=".+?">(.+?)</a>', html_web)
                if str(studiog) != 'None':
                    dict_nfo['片商'] = studio = studiog.group(1).replace("\\", "#").replace("/", "#").replace(":", "：")\
                        .replace("*", "#").replace("?", "？").replace("\"", "#")
                else:
                    dict_nfo['片商'] = '无码片商'
                # 系列:</span> <a href="https://www.cdnbus.work/series/kpl">悪質シロウトナンパ</a>
                series = ''
                seriesg = search(r'系列:</span> <a href=".+?">(.+?)</a>', html_web)  # 封面图片的正则对象
                if str(seriesg) != 'None':
                    dict_nfo['系列'] = series = seriesg.group(1)
                else:
                    dict_nfo['系列'] = '无码系列'
                # print('系列', series)
                # 演员们 和 # 第一个演员
                actors = findall(r'star/.+?"><img src=.+?" title="(.+?)">', html_web)
                if actors:
                    if len(actors) > 7:
                        dict_nfo['全部演员'] = ' '.join(actors[:7])
                    else:
                        dict_nfo['全部演员'] = ' '.join(actors)
                    dict_nfo['首个演员'] = actors[0]
                    if bool_strip_actors and title_only.endswith(dict_nfo['全部演员']):
                        title_only = title_only[:-len(dict_nfo['全部演员'])].rstrip()
                else:
                    actors = ['无码演员']
                    dict_nfo['首个演员'] = dict_nfo['全部演员'] = '无码演员'
                # 处理影片的标题过长
                dict_nfo['完整标题'] = title_only
                if len(title_only) > int_title_len:
                    dict_nfo['标题'] = title_only[:int_title_len]
                else:
                    dict_nfo['标题'] = title_only
                # 特点
                genres = findall(r'genre"><a href=".+?">(.+?)</a></span>', html_web)
                genres = [i for i in genres if i != '字幕' and i != '高清' and i != '高畫質' and i != '60fps' and i != '1080p']
                if bool_subt:  # 有“中字“，加上特征”中文字幕”
                    genres.append('中文字幕')
                if dict_nfo['是否xx']:   # 有xx，加上特征custom_xx_expression
                    genres.append(custom_xx_expression)
                # print(genres)
                #######################################################################
                # jav_name 是自始至终的 文件名（不带文件类型）  jav_file是自始至终的 文件名（完整带文件类型） root是原所在文件夹的路径  root_now 是现在（新）所在文件夹的路径
                # path_jav 是现在视频路径   path_subt是现在字幕路径   subt_file是 自始至终的 字幕文件名（带文件类型）  jav_folder是自始至终的 所在文件夹名（不是路径）
                dict_nfo['视频'] = dict_nfo['原文件名'] = jav_name                    # 【发生变化】 dict_nfo['视频']
                jav_folder = dict_nfo['原文件夹名'] = root.split(sep)[-1]  # 当前影片的目录名称，在下面的重命名操作中即将发生变化
                path_subt = root + sep + subt_file  # 字幕的起始路径
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
                            path_jav = path_jav_new              # 【发生变化】 path_jav
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
                            record_fail('    >第' + str(num_fail) + '个失败！独立文件夹中已存在相同的视频文件：' + path_jav_new + '\n')
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
                            "  <title>" + title_in_nfo + "</title>\n"
                            "  <director>" + dict_nfo['导演'] + "</director>\n"
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
                    if bool_zh:
                        for i in genres:
                            f.write("  <genre>" + gen_dict[i] + "</genre>\n")
                            f.write("  <tag>" + gen_dict[i] + "</tag>\n")
                    else:
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
                        print('    >从javbus下载封面：', url_cover)
                        try:
                            download_pic(list_cover)
                            print('    >fanart.jpg下载成功')
                        except:
                            num_fail += 1
                            record_fail('    >第' + str(
                                num_fail) + '个失败！下载fanart.jpg失败：' + url_cover + '，' + path_relative + '\n')
                            continue     # 退出对该jav的整理
                        # 裁剪生成 poster
                        img = Image.open(path_fanart)
                        wf, hf = img.size                        # fanart的宽 高
                        wide = int(hf*2/3)                     # 理想中海报的宽，应该是fanart的高的三分之二
                        # 如果fanart特别“瘦”，宽不到高的三分之二。以fanart的宽作为poster的宽。
                        if wf < wide:
                            poster = img.crop((0, 0, wf, wf*1.5))
                            poster.save(path_poster, quality=95)  # quality=95 是无损crop，如果不设置，默认75
                            print('    >poster.jpg裁剪成功')
                        else:
                            wide_half = wide / 2
                            # 需要使用人体分析
                            if bool_face:
                                x_nose = image_cut(path_fanart, client)  # 鼻子的x坐标  0.704 0.653
                                if x_nose + wide_half > wf:              # 鼻子 + 一半poster宽超出fanart右边
                                    x_left = wf - wide                   # 以右边为poster
                                elif x_nose - wide_half < 0:            # 鼻子 - 一半poster宽超出fanart左边
                                    x_left = 0                          # 以左边为poster
                                else:                                   # 不会超出poster
                                    x_left = x_nose - wide_half          # 以鼻子为中心向两边扩展
                            else:
                                x_left = wf-wide                        # 以右边为poster
                            # crop
                            poster = img.crop((x_left, 0, x_left + wide, hf))
                            poster.save(path_poster, quality=95)
                            print('    >poster.jpg裁剪成功')

                # 6收集演员头像
                if bool_sculpture and jav_epi == 1:
                    if actors[0] == '无码演员':
                        print('    >无码演员，无法收集头像！')
                    else:
                        for each_actor in actors:
                            path_exist_actor = '演员头像' + sep + each_actor[0] + sep + each_actor + '.jpg'  # 事先准备好的演员头像路径
                            # print(path_exist_actor)
                            pic_type = '.jpg'
                            if not os.path.exists(path_exist_actor):                # 演员jpg图片还没有
                                path_exist_actor = '演员头像' + sep + each_actor[0] + sep + each_actor + '.png'
                                if not os.path.exists(path_exist_actor):            # 演员png图片还没有
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
                                    continue  # 跳出此次 each_actor
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
