# -*- coding:utf-8 -*-
import os
import re
import time
from os import sep  # 系统路径分隔符
from configparser import RawConfigParser  # 读取ini
from configparser import NoOptionError  # ini文件不存在或不存在指定node的错误
from shutil import copyfile
from aip import AipBodyAnalysis  # 百度ai人体分析

from Classes.MyJav import JavFile
from Classes.MyLogger import record_video_old
from Classes.MyError import TooManyDirectoryLevelsError, DownloadFanartError
from Functions.Utils.Download import download_pic
from Functions.Progress.Prepare import get_suren_cars
from Functions.Progress.Picture import check_picture, crop_poster_youma, add_watermark_subtitle, add_watermark_divulge
from Functions.Utils.XML import replace_xml_win, replace_xml
from Functions.Metadata.Car import find_car_fc2, find_car_youma


# 设置
class FileHandler(object):
    def __init__(self, pattern):
        self._pattern = pattern
        # ####################################### 本次程序启动通用 ####################################################
        # 素人番号: 得到事先设置的素人番号，让程序能跳过它们
        self.list_suren_cars = get_suren_cars()
        # 是否需要重命名文件夹
        self.bool_rename_folder = self.judge_need_rename_folder()
        # 归类的目标文件夹的拼接公式
        self.list_classify_basis = []
        # 用于给用户自定义命名的字典
        self.dict_for_standard = self.get_dict_for_standard()

        # ####################################### 每次重新选择文件夹通用 ##############################################
        # 选择的文件夹
        self.dir_choose = ''
        # 归类的目标根文件夹
        self.dir_classify_target = ''
        # 当前视频（包括非jav）的编号，用于显示进度、获取最大视频编号即当前文件夹内视频数量
        self.no_current = 0
        # 当前所选文件夹内视频总数
        self.sum_videos_in_choose_dir = 0
        # ####################################### 每一级文件夹通用 ##############################################
        # 当前for循环所处的这一级文件夹路径
        self.dir_current = ''
        # 字幕文件和车牌对应关系 {'c:\a\abc_123.srt': 'abc-123'}
        self.dict_subtitle_file = {}
        # 存放: 每一车牌的集数， 例如{'abp-123': 1, avop-789': 2}是指 abp-123只有一集，avop-789有cd1、cd2
        self.dict_car_episode = {}
        # 当前一级文件夹包含的视频总数
        self.sum_videos_in_current_dir = 0
        # 定义 Windows中的非法字符, 将非法字符替换为空格
        self.winDic = str.maketrans(r':<>"\?/*', '        ')

    # 每次用户选择文件夹后重置
    def rest_choose_dir(self, dir_choose):
        self.dir_choose = dir_choose
        # self.dir_classify_target = ''  通过check_classify_target_directory重置
        self.check_classify_target_directory()
        self.no_current = 0
        self.sum_videos_in_choose_dir = self.count_num_videos()

    # 每层级文件夹重置
    def rest_current_dir(self, dir_current):
        self.dir_current = dir_current
        self.dict_subtitle_file = {}
        self.dict_car_episode = {}
        self.sum_videos_in_current_dir = 0

    # #########################[修改文件夹]##############################
    # 是否需要重命名文件夹或者创建新的文件夹
    def judge_need_rename_folder(self):
        if self._bool_classify:  # 如果需要归类
            if self._bool_classify_folder:  # 并且是针对文件夹
                return True  # 那么必须重命名文件夹或者创建新的文件夹
        else:  # 不需要归类
            if self._bool_rename_folder:  # 但是用户本来就在ini中写了要重命名文件夹
                return True
        return False

    # #########################[归类影片]##############################

    # 功能: 检查 归类根目录 的合法性
    # 参数: 用户选择整理的文件夹路径
    # 返回: 归类根目录路径
    # 辅助: os.sep，os.system
    def check_classify_target_directory(self):
        # 检查 归类根目录 的合法性
        if self._bool_classify:
            custom_classify_target_dir = self._custom_classify_target_dir.rstrip(sep)
            # 用户使用默认的“所选文件夹”
            if custom_classify_target_dir == '所选文件夹':
                self.dir_classify_target = f'{self.dir_choose}{sep}归类完成'
            # 归类根目录 是 用户输入的路径c:\a，继续核实合法性
            else:
                # 用户输入的路径 不是 所选文件夹dir_choose
                if custom_classify_target_dir != self.dir_choose:
                    if custom_classify_target_dir[:2] != self.dir_choose[:2]:
                        input(f'归类的根目录: 【{custom_classify_target_dir}】和所选文件夹不在同一磁盘无法归类！请修正！')
                    if not os.path.exists(custom_classify_target_dir):
                        input(f'归类的根目录: 【{custom_classify_target_dir}】不存在！无法归类！请修正！')
                    self.dir_classify_target = custom_classify_target_dir
                # 用户输入的路径 就是 所选文件夹dir_choose
                else:
                    self.dir_classify_target = f'{self.dir_choose}{sep}归类完成'
        else:
            self.dir_classify_target = ''

    # #########################[百度人体分析]##############################
    # 百度翻译启动
    def start_body_analysis(self):
        if self.bool_face:
            return AipBodyAnalysis(self._al_id, self._ai_ak, self._al_sk)
        else:
            return None

    # 功能: 收集文件们中的字幕文件，存储在self.dict_subtitle_file
    # 参数: list_sub_files（当前文件夹的）子文件们
    # 返回: 无；更新self.dict_subtitle_file
    # 辅助: find_car_youma, find_car_fc2
    def init_dict_subtitle_file(self, list_sub_files:list):
        for file_raw in list_sub_files:
            file_temp = file_raw.upper()
            if file_temp.endswith(('.SRT', '.VTT', '.ASS', '.SSA', '.SUB', '.SMI',)):
                if self._pattern != 'Fc2':
                    # 有码无码不处理FC2
                    if 'FC2' in file_temp:
                        continue
                    # 去除用户设置的、干扰车牌的文字
                    for word in self._list_surplus_words_in_filename:
                        file_temp = file_temp.replace(word, '')
                    # 得到字幕文件名中的车牌
                    subtitle_car = find_car_youma(file_temp, self.list_suren_cars)
                else:
                    # 仅处理fc2
                    if 'FC2' not in file_temp:
                        continue  # 【跳出2】
                    # 得到字幕文件名中的车牌
                    subtitle_car = find_car_fc2(file_temp)
                # 将该字幕文件和其中的车牌对应到dict_subtitle_file中
                if subtitle_car:
                    self.dict_subtitle_file[file_raw] = subtitle_car

    # 功能: 发现文件中的jav视频文件，存储在list_jav_files
    # 参数: list_sub_files（当前文件夹的）子文件们
    # 返回: list_jav_files；更新self.dict_car_episode
    # 辅助: JavFile
    def get_list_jav_files(self, list_sub_files):
        list_jav_files = []  # 存放: 需要整理的jav_file
        for file_raw in list_sub_files:
            file_temp = file_raw.upper()
            if file_temp.endswith(self._tuple_video_types) and not file_temp.startswith('.'):
                self.no_current += 1
                self.sum_videos_in_current_dir += 1
                if 'FC2' in file_temp:
                    continue
                # file_temp = file_temp.replace('HHD800', '')
                for word in self._list_surplus_words_in_filename:
                    file_temp = file_temp.replace(word, '')
                # 得到视频中的车牌
                car = find_car_youma(file_temp, self.list_suren_cars)
                if car:
                    try:
                        self.dict_car_episode[car] += 1  # 已经有这个车牌了，加一集cd
                    except KeyError:
                        self.dict_car_episode[car] = 1  # 这个新车牌有了第一集
                    # 这个车牌在dict_subtitle_files中，有它的字幕。
                    if car in self.dict_subtitle_file.values():
                        subtitle_file = list(self.dict_subtitle_file.keys())[
                            list(self.dict_subtitle_file.values()).index(car)]
                        del self.dict_subtitle_file[subtitle_file]
                    else:
                        subtitle_file = ''
                    carg = re.search(r'\d\dID-(\d\d)(\d+)', car)
                    if carg:
                        car_id = f'{carg.group(1)}ID-{carg.group(2)}'
                    else:
                        car_id = car
                    # 将该jav的各种属性打包好，包括原文件名带扩展名、所在文件夹路径、第几集、所属字幕文件名
                    jav_struct = JavFile(car, car_id, file_raw, self.dir_current, self.dict_car_episode[car],
                                         subtitle_file,
                                         self.no_current)
                    list_jav_files.append(jav_struct)
                else:
                    print(f'>>无法处理: {self.dir_current[len(self.dir_choose):]}{sep}{file_raw}')
        return list_jav_files

    # 功能：所选文件夹总共有多少个视频文件
    # 参数：用户选择整理的文件夹路径root_choose，视频类型后缀集合tuple_video_type
    # 返回：无
    # 辅助：os.walk
    def count_num_videos(self):
        num_videos = 0
        len_choose = len(self.dir_choose)
        for root, dirs, files in os.walk(self.dir_choose):
            if '归类完成' not in root[len_choose:]:
                for file_raw in files:
                    file_temp = file_raw.upper()
                    if file_temp.endswith(self._tuple_video_types) and not file_temp.startswith('.'):
                        num_videos += 1
        return num_videos

    # 功能: 处理多视频文件的问题，（1）所选文件夹总共有多少个视频文件，包括非jav文件，主要用于显示进度（2）同一车牌有多少cd，用于cd2...命名
    # 参数: list_jav_files
    # 返回: 无；更新self.sum_all_videos
    # 辅助: 无
    def count_num_and_no(self, list_jav_files):
        for jav_file in list_jav_files:
            jav_file.Sum_all_episodes = self.dict_car_episode[jav_file.Car]

    # 功能: （1）完善用于给用户命名的dict_for_standard，如果用户自定义的各种命名公式中有dict_for_standard未包含的元素，则添加。
    #      （2）将_custom_classify_basis按“+”“\”切割好，准备用于组装后面的归类路径。
    # 参数: 无
    # 返回: dict_for_standard; 更新self.list_classify_basis
    # 辅助: os.sep
    def get_dict_for_standard(self):
        dict_for_standard = {'车牌': 'ABC-123',
                             '车牌前缀': 'ABC',
                             '标题': f'{self._pattern}标题',
                             '完整标题': f'完整{self._pattern}标题',
                             '导演': f'{self._pattern}导演',
                             '制作商': f'{self._pattern}制作商',
                             '发行商': f'{self._pattern}发行商',
                             '评分': 0.0,
                             '片长': 0,
                             '系列': f'{self._pattern}系列',
                             '发行年月日': '1970-01-01', '发行年份': '1970', '月': '01', '日': '01',
                             '首个演员': f'{self._pattern}演员', '全部演员': f'{self._pattern}演员',
                             '空格': ' ',
                             '\\': sep, '/': sep,  # 文件路径分隔符
                             '是否中字': '',
                             '是否流出': '',
                             '影片类型': self._av_type,  # 自定义有码、无码、素人、FC2的对应称谓
                             '视频': 'ABC-123',  # 当前及未来的视频文件名，不带ext
                             '原文件名': 'ABC-123', '原文件夹名': 'ABC-123', }
        if self._pattern == 'fc2':
            dict_for_standard['车牌'] = 'FC2-123'
            dict_for_standard['车牌前缀'] = 'FC2'
            dict_for_standard['视频'] = 'FC2-123'
            dict_for_standard['原文件名'] = 'FC2-123'
            dict_for_standard['原文件夹名'] = 'FC2-123'
        for i in self._list_extra_genres:
            if i not in dict_for_standard:
                dict_for_standard[i] = i
        for i in self._list_rename_video:
            if i not in dict_for_standard:
                dict_for_standard[i] = i
        for i in self._list_rename_folder:
            if i not in dict_for_standard:
                dict_for_standard[i] = i
        for i in self._list_name_nfo_title:
            if i not in dict_for_standard:
                dict_for_standard[i] = i
        for i in self._list_name_fanart:
            if i not in dict_for_standard:
                dict_for_standard[i] = i
        for i in self._list_name_poster:
            if i not in dict_for_standard:
                dict_for_standard[i] = i
        # 归类路径的组装公式
        for i in self._custom_classify_basis.split('\\'):
            for j in i.split('+'):
                if j not in dict_for_standard:
                    dict_for_standard[j] = j
                self.list_classify_basis.append(j)
            self.list_classify_basis.append(sep)
        return dict_for_standard

    # 功能: 判定影片所在文件夹是否是独立文件夹，独立文件夹是指该文件夹仅用来存放该影片，不包含“.actors”"extrafanrt”外的其他文件夹
    # 参数: len_dict_car_pref 当前所处文件夹包含的车牌数量, len_list_jav_struct当前所处文件夹包含的、需要整理的jav的结构体数量,
    #      list_sub_dirs当前所处文件夹包含的子文件夹们
    # 返回: True
    # 辅助: judge_exist_extra_folders
    def judge_separate_folder(self, len_list_jav_files, list_sub_dirs):
        # 当前文件夹下，车牌不止一个；还有其他非jav视频；有其他文件夹，除了演员头像文件夹“.actors”和额外剧照文件夹“extrafanart”；
        if len(self.dict_car_episode) > 1 or self.sum_videos_in_current_dir > len_list_jav_files:
            JavFile.Bool_in_separate_folder = False
            return
        for folder in list_sub_dirs:
            if folder != '.actors' and folder != 'extrafanart':
                JavFile.Bool_in_separate_folder = False
                return
        JavFile.Bool_in_separate_folder = True  # 这一层文件夹是这部jav的独立文件夹
        return



    # 功能: 1重命名视频(jav_file和dict_for_standard发生改变）
    # 参数: 设置settings，命名信息dict_for_standard，处理的影片jav
    # 返回: path_return，重命名操作可能不成功，返回path_return告知主程序提醒用户处理
    # 辅助: os.exists, os.rename, record_video_old, record_fail
    def rename_mp4(self, jav_file):
        # 如果重命名操作不成功，将path_new赋值给path_return，提醒用户自行重命名
        path_return = ''
        if self._bool_rename_video:
            # 构造新文件名，不带文件类型后缀
            name_without_ext = ''
            for j in self._list_rename_video:
                name_without_ext = f'{name_without_ext}{self.dict_for_standard[j]}'
            if os.name == 'nt':  # 如果是windows系统
                name_without_ext = name_without_ext.translate(self.winDic)  # 将文件名中的非法字符替换为空格
            name_without_ext = f'{name_without_ext.strip()}{jav_file.Cd}'  # 去除末尾空格，否则windows会自动删除空格，导致程序仍以为带空格
            path_new = f'{jav_file.Dir}{sep}{name_without_ext}{jav_file.Ext}'  # 【临时变量】path_new 视频文件的新路径

            # 一般情况，不存在同名视频文件
            if not os.path.exists(path_new):
                os.rename(jav_file.Path, path_new)
                record_video_old(jav_file.Path, path_new)
            # 已存在目标文件，但就是现在的文件
            elif jav_file.Path.upper() == path_new.upper():
                try:
                    os.rename(jav_file.Path, path_new)
                # windows本地磁盘，“abc-123.mp4”重命名为“abc-123.mp4”或“ABC-123.mp4”没问题，但有用户反映，挂载的磁盘会报错“file exists error”
                except FileExistsError:
                    # 提醒用户后续自行更改
                    path_return = path_new
            # 存在目标文件，不是现在的文件。
            else:
                raise FileExistsError(f'重命名影片失败，重复的影片，已经有相同文件名的视频了: {path_new}')  # 【终止对该jav的整理】
            self.dict_for_standard['视频'] = name_without_ext  # 【更新】 dict_for_standard['视频']
            jav_file.Name = f'{name_without_ext}{jav_file.Ext}'  # 【更新】jav.name，重命名操作可能不成功，但之后的操作仍然围绕成功的jav.name来命名
            print(f'    >修改文件名{jav_file.Cd}完成')
            # 重命名字幕
            if jav_file.Subtitle and self._bool_rename_subtitle:
                subtitle_new = f'{name_without_ext}{jav_file.Ext_subtitle}'  # 【临时变量】subtitle_new
                path_subtitle_new = f'{jav_file.Dir}{sep}{subtitle_new}'  # 【临时变量】path_subtitle_new
                if jav_file.Path_subtitle != path_subtitle_new:
                    os.rename(jav_file.Path_subtitle, path_subtitle_new)
                    jav_file.Subtitle = subtitle_new  # 【更新】 jav.subtitle 字幕完整文件名
                print('    >修改字幕名完成')
        return path_return

    # 功能: 2归类影片，只针对视频文件和字幕文件，无视它们当前所在文件夹
    # 参数: 设置settings，命名信息dict_for_standard，处理的影片jav
    # 返回: 处理的影片jav（所在文件夹路径改变）
    # 辅助: os.exists, os.rename, os.makedirs，
    def classify_files(self, jav_file):
        # 如果需要归类，且不是针对文件夹来归类
        if self._bool_classify and not self._bool_classify_folder:
            # 移动的目标文件夹路径
            dir_dest = f'{self.dir_classify_target}{sep}'
            for j in self.list_classify_basis:
                # 【临时变量】归类的目标文件夹路径    C:\Users\JuneRain\Desktop\测试文件夹\葵司\
                dir_dest = f'{dir_dest}{self.dict_for_standard[j].strip()}'
            # 还不存在该文件夹，新建
            if not os.path.exists(dir_dest):
                os.makedirs(dir_dest)
            path_new = f'{dir_dest}{sep}{jav_file.Name}'  # 【临时变量】新的影片路径
            # 目标文件夹没有相同的影片，防止用户已经有一个“avop-127.mp4”，现在又来一个
            if not os.path.exists(path_new):
                os.rename(jav_file.Path, path_new)
                print('    >归类视频文件完成')
                # 移动字幕
                if jav_file.Subtitle:
                    path_subtitle_new = f'{dir_dest}{sep}{jav_file.Subtitle}'  # 【临时变量】新的字幕路径
                    if jav_file.Path_subtitle != path_subtitle_new:
                        os.rename(jav_file.Path_subtitle, path_subtitle_new)
                    print('    >归类字幕文件完成')
                jav_file.Dir = dir_dest  # 【更新】jav.dir
            else:
                raise FileExistsError(f'归类失败，重复的影片，归类的目标文件夹已经存在相同的影片: {path_new}')  # 【终止对该jav的整理】

    # 功能: 3重命名文件夹【相同】如果已进行第2操作，第3操作不会进行，因为用户只需要归类视频文件，不需要管文件夹。
    # 参数: 处理的影片jav
    # 返回: 处理的影片jav（所在文件夹路径改变）
    # 辅助: os.exists, os.rename, os.makedirs，record_fail
    def rename_folder(self, jav_file):
        if self.bool_rename_folder:
            # 构造 新文件夹名folder_new
            folder_new = ''
            for j in self._list_rename_folder:
                folder_new = f'{folder_new}{self.dict_for_standard[j]}'
            folder_new = folder_new.rstrip(' .')  # 【临时变量】新的所在文件夹。去除末尾空格和“.”
            # 是独立文件夹，才会重命名文件夹
            if jav_file.Bool_in_separate_folder:
                # 当前视频是该车牌的最后一集，他的兄弟姐妹已经处理完成，才会重命名它们的“家”。
                if jav_file.Episode == jav_file.Sum_all_episodes:
                    dir_new = f'{os.path.dirname(jav_file.Dir)}{sep}{folder_new}'  # 【临时变量】新的影片所在文件夹路径。
                    # 想要重命名的目标影片文件夹不存在
                    if not os.path.exists(dir_new):
                        os.rename(jav_file.Dir, dir_new)
                        jav_file.Dir = dir_new  # 【更新】jav.dir
                    # 目标影片文件夹存在，但就是现在的文件夹，即新旧相同
                    elif jav_file.Dir == dir_new:
                        pass
                    # 真的有一个同名的文件夹了
                    else:
                        raise FileExistsError(f'重命名文件夹失败，已存在相同文件夹: {dir_new}')  # 【终止对该jav的整理】
                    print('    >重命名文件夹完成')
            # 不是独立的文件夹，建立独立的文件夹
            else:
                path_separate_folder = f'{jav_file.Dir}{sep}{folder_new}'  # 【临时变量】需要创建的的影片所在文件夹。
                # 确认没有同名文件夹
                if not os.path.exists(path_separate_folder):
                    os.makedirs(path_separate_folder)
                path_new = f'{path_separate_folder}{sep}{jav_file.Name}'  # 【临时变量】新的影片路径
                # 如果这个文件夹是现成的，在它内部确认有没有“abc-123.mp4”。
                if not os.path.exists(path_new):
                    os.rename(jav_file.Path, path_new)
                    print('    >移动到独立文件夹完成')
                    # 移动字幕
                    if jav_file.Subtitle:
                        path_subtitle_new = f'{path_separate_folder}{sep}{jav_file.Subtitle}'  # 【临时变量】新的字幕路径
                        os.rename(jav_file.Path_subtitle, path_subtitle_new)
                        # 下面不会操作 字幕文件 了，jav.path_subtitle不再更新
                        print('    >移动字幕到独立文件夹')
                    jav_file.Dir = path_separate_folder  # 【更新】jav.dir
                # 里面已有“avop-127.mp4”，这不是它的家。
                else:
                    raise FileExistsError(f'创建独立文件夹失败，已存在相同的视频文件: {path_new}')  # 【终止对该jav的整理】

    # 功能: 6为当前jav收集演员头像到“.actors”文件夹中
    # 参数: jav_file 处理的jav视频文件对象，jav_model 保存jav元数据的对象
    # 返回: 无
    # 辅助: os.path.exists，os.makedirs, configparser.RawConfigParser, shutil.copyfile
    def collect_sculpture(self, jav_file, jav_model):
        if self._bool_sculpture and jav_file.Episode == 1:
            if not jav_model.Actors:
                print('    >未知演员，无法收集头像')
            else:
                for each_actor in jav_model.Actors:
                    path_exist_actor = f'演员头像{sep}{each_actor[0]}{sep}{each_actor}'  # 事先准备好的演员头像路径
                    if os.path.exists(f'{path_exist_actor}.jpg'):
                        pic_type = '.jpg'
                    elif os.path.exists(f'{path_exist_actor}.png'):
                        pic_type = '.png'
                    else:
                        config_actor = RawConfigParser()
                        config_actor.read('【缺失的演员头像统计For Kodi】.ini', encoding='utf-8-sig')
                        try:
                            each_actor_times = config_actor.get('缺失的演员头像', each_actor)
                            config_actor.set("缺失的演员头像", each_actor, str(int(each_actor_times) + 1))
                        except NoOptionError:
                            config_actor.set("缺失的演员头像", each_actor, '1')
                        config_actor.write(open('【缺失的演员头像统计For Kodi】.ini', "w", encoding='utf-8-sig'))
                        continue
                    # 已经收录了这个演员头像
                    dir_dest_actor = f'{jav_file.Dir}{sep}.actors{sep}'  # 头像的目标文件夹
                    if not os.path.exists(dir_dest_actor):
                        os.makedirs(dir_dest_actor)
                    # 复制一份到“.actors”
                    copyfile(f'{path_exist_actor}{pic_type}', f'{dir_dest_actor}{each_actor}{pic_type}')
                    print('    >演员头像收集完成: ', each_actor)

    # 功能: 7归类影片，针对文件夹（如果已进行第2操作，第7操作不会进行，因为用户只需要归类视频文件，不需要管文件夹）
    # 参数: jav_file 处理的jav视频文件对象
    # 返回: 处理的影片jav（所在文件夹路径改变）
    # 辅助: os.exists, os.rename, os.makedirs，
    def classify_folder(self, jav_file):
        # 需要移动文件夹，且，是该影片的最后一集
        if self._bool_classify and self._bool_classify_folder and jav_file.Episode == jav_file.Sum_all_episodes:
            # 用户选择的文件夹是一部影片的独立文件夹，为了避免在这个文件夹里又生成新的归类文件夹
            if jav_file.Bool_in_separate_folder and self.dir_classify_target.startswith(jav_file.Dir):
                raise TooManyDirectoryLevelsError(f'无法归类，不建议在当前文件夹内再新建文件夹')
            # 归类放置的目标文件夹
            dir_dest = f'{self.dir_classify_target}{sep}'
            # 移动的目标文件夹
            for j in self.list_classify_basis:
                # 【临时变量】 文件夹移动的目标上级文件夹  C:\Users\JuneRain\Desktop\测试文件夹\1\葵司\
                dir_dest = f'{dir_dest}{self.dict_for_standard[j].rstrip(" .")}'
            # 【临时变量】 文件夹移动的目标路径   C:\Users\JuneRain\Desktop\测试文件夹\1\葵司\【葵司】AVOP-127\
            dir_new = f'{dir_dest}{sep}{jav_file.Folder}'
            # print(dir_new)
            # 还不存在归类的目标文件夹
            if not os.path.exists(dir_new):
                os.makedirs(dir_new)
                # 把现在文件夹里的东西都搬过去
                jav_files = os.listdir(jav_file.Dir)
                for i in jav_files:
                    os.rename(f'{jav_file.Dir}{sep}{i}', f'{dir_new}{sep}{i}')
                # 删除“旧房子”，这是javsdt唯一的删除操作，而且os.rmdir只能删除空文件夹
                os.rmdir(jav_file.Dir)
                print('    >归类文件夹完成')
            # 用户已经有了这个文件夹，可能以前处理过同车牌的视频
            else:
                raise FileExistsError(f'归类失败，归类的目标位置已存在相同文件夹: {dir_new}')

    # 功能: 写nfo
    # 参数: jav_file 处理的jav视频文件对象，jav_model 保存jav元数据的对象，genres
    # 返回: 素人车牌list
    # 辅助: 无
    def write_nfo(self, jav_file, jav_model, genres):
        if self._bool_nfo:
            # 如果是为kodi准备的nfo，不需要多cd
            if self._bool_cd_only:
                path_nfo = f'{jav_file.Dir}{sep}{jav_file.Name_no_ext.replace(jav_file.Cd, "")}.nfo'
            else:
                path_nfo = f'{jav_file.Dir}{sep}{jav_file.Name_no_ext}.nfo'
            # nfo中tilte的写法
            title_in_nfo = ''
            for i in self._list_name_nfo_title:
                title_in_nfo = f'{title_in_nfo}{self.dict_for_standard[i]}'  # nfo中tilte的写法
            # 开始写入nfo，这nfo格式是参考的kodi的nfo
            plot = replace_xml(jav_model.PlotZh) if self._bool_need_zh_plot else replace_xml(jav_model.Plot)
            f = open(path_nfo, 'w', encoding="utf-8")
            f.write(f'<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\" ?>\n'
                    f'<movie>\n'
                    f'  <plot>{plot}{replace_xml(jav_model.Review)}</plot>\n'
                    f'  <title>{title_in_nfo}</title>\n'
                    f'  <originaltitle>{jav_model.Car} {replace_xml(jav_model.Title)}</originaltitle>\n'
                    f'  <director>{replace_xml(jav_model.Director)}</director>\n'
                    f'  <rating>{jav_model.Score / 10}</rating>\n'
                    f'  <criticrating>{jav_model.Score}</criticrating>\n'  # 烂番茄评分 用上面的评分*10
                    f'  <year>{jav_model.Release[0:4]}</year>\n'
                    f'  <mpaa>NC-17</mpaa>\n'
                    f'  <customrating>NC-17</customrating>\n'
                    f'  <countrycode>JP</countrycode>\n'
                    f'  <premiered>{jav_model.Release}</premiered>\n'
                    f'  <release>{jav_model.Release}</release>\n'
                    f'  <runtime>{jav_model.Runtime}</runtime>\n'
                    f'  <country>日本</country>\n'
                    f'  <studio>{replace_xml(jav_model.Studio)}</studio>\n'
                    f'  <id>{jav_model.Car}</id>\n'
                    f'  <num>{jav_model.Car}</num>\n'
                    f'  <set>{replace_xml(jav_model.Series)}</set>\n')  # emby不管set系列，kodi可以
            # 需要将特征写入genre
            if self._bool_genre:
                for i in genres:
                    f.write(f'  <genre>{i}</genre>\n')
                if self._bool_write_series and jav_model.Series:
                    f.write(f'  <genre>系列:{jav_model.Series}</genre>\n')
                if self._bool_write_studio and jav_model.Studio:
                    f.write(f'  <genre>片商:{jav_model.Studio}</genre>\n')
                for i in self._list_extra_genres:
                    f.write(f'  <genre>{self.dict_for_standard[i]}</genre>\n')
            # 需要将特征写入tag
            if self._bool_tag:
                for i in genres:
                    f.write(f'  <tag>{i}</tag>\n')
                if self._bool_write_series and jav_model.Series:
                    f.write(f'  <tag>系列:{jav_model.Series}</tag>\n')
                if self._bool_write_studio and jav_model.Studio:
                    f.write(f'  <tag>片商:{jav_model.Studio}</tag>\n')
                for i in self._list_extra_genres:
                    f.write(f'  <tag>{self.dict_for_standard[i]}</tag>\n')
            # 写入演员
            for i in jav_model.Actors:
                f.write(f'  <actor>\n'
                        f'    <name>{i}</name>\n'
                        f'    <type>Actor</type>\n'
                        f'  </actor>\n')
            f.write('</movie>\n')
            f.close()
            print('    >nfo收集完成')

    def download_fanart(self, jav_file, jav_model):
        if self._bool_jpg:
            # fanart和poster路径
            path_fanart = f'{jav_file.Dir}{sep}'
            path_poster = f'{jav_file.Dir}{sep}'
            for i in self._list_name_fanart:
                path_fanart = f'{path_fanart}{self.dict_for_standard[i]}'
            for i in self._list_name_poster:
                path_poster = f'{path_poster}{self.dict_for_standard[i]}'
            # kodi只需要一份图片，不管视频是cd几，图片仅一份不需要cd几。
            if self._bool_cd_only:
                path_fanart = path_fanart.replace(jav_file.Cd, '')
                path_poster = path_poster.replace(jav_file.Cd, '')
            # emby需要多份，现在不是第一集，直接复制第一集的图片
            elif jav_file.Episode != 1:
                # 如果用户不重名视频，并且用户的原视频是第二集，没有带cd2，例如abc-123.mkv和abc-123.mp4，
                # 会导致fanart路径和cd1相同，引发报错raise SameFileError("{!r} and {!r} are the same file".format(src, dst))
                # 所以这里判断下path_fanart有没有
                if not os.path.exists(path_fanart):
                    copyfile(path_fanart.replace(jav_file.Cd, '-cd1'), path_fanart)
                    print('    >fanart.jpg复制成功')
                    copyfile(path_poster.replace(jav_file.Cd, '-cd1'), path_poster)
                    print('    >poster.jpg复制成功')
            # kodi或者emby需要的第一份图片
            if check_picture(path_fanart):
                # 这里有个遗留问题，如果已有的图片文件名是小写，比如abc-123 xx.jpg，现在path_fanart是大写ABC-123，无法改变，poster同理
                # print('    >已有fanart.jpg')
                pass
            else:
                status = False
                if jav_model.Javdb:
                    url_cover = f'https://jdbimgs.com/covers/{jav_model.Javdb[:2].lower()}/{jav_model.Javdb}.jpg'
                    # print('    >从javdb下载封面: ', url_cover)
                    print('    >下载封面: ...')
                    status = download_pic(url_cover, path_fanart, self.proxy_db)
                if not status and jav_model.CoverBus:
                    url_cover = f'{self.url_bus}/pics/cover/{jav_model.CoverBus}'
                    print('    >从javbus下载封面: ', url_cover)
                    status = download_pic(url_cover, path_fanart, self.proxy_bus)
                if not status and jav_model.CoverLibrary:
                    url_cover = jav_model.CoverLibrary
                    print('    >从dmm下载封面: ', url_cover)
                    status = download_pic(url_cover, path_fanart, self.proxy_dmm)
                if status:
                    pass
                else:
                    raise DownloadFanartError
            # 裁剪生成 poster
            if check_picture(path_poster):
                # print('    >已有poster.jpg')
                pass
            else:
                crop_poster_youma(path_fanart, path_poster)
                # 需要加上条纹
                if self._bool_watermark_subtitle and jav_file.Bool_subtitle:
                    add_watermark_subtitle(path_poster)
                if self._bool_watermark_divulge and jav_file.Bool_divulge:
                    add_watermark_divulge(path_poster)

    # 功能: 如果需要为kodi整理头像，则先检查“演员头像for kodi.ini”、“演员头像”文件夹是否存在; 检查 归类根目录 的合法性
    # 参数: 是否需要整理头像，用户自定义的归类根目录，用户选择整理的文件夹路径
    # 返回: 归类根目录路径
    # 辅助: os.sep，os.path.exists，shutil.copyfile
    def check_actors(self):
        # 检查头像: 如果需要为kodi整理头像，先检查演员头像ini、头像文件夹是否存在。
        if self._bool_sculpture:
            if not os.path.exists('演员头像'):
                input('\n“演员头像”文件夹丢失！请把它放进exe的文件夹中！\n')
            if not os.path.exists('【缺失的演员头像统计For Kodi】.ini'):
                if os.path.exists('actors_for_kodi.ini'):
                    copyfile('actors_for_kodi.ini', '【缺失的演员头像统计For Kodi】.ini')
                    print('\n“【缺失的演员头像统计For Kodi】.ini”成功！')
                else:
                    input('\n请打开“【ini】重新创建ini.exe”创建丢失的程序组件!')
