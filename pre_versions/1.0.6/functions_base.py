# -*- coding:utf-8 -*-
import os, requests, re
from os.path import exists
from os import sep
from configparser import RawConfigParser
from PIL import Image
from tkinter import filedialog, Tk
from time import sleep
import xml.etree.ElementTree as ET
from shutil import copyfile
# from traceback import format_exc


# 每一部jav的“结构体”
class JavFile(object):
    def __init__(self):
        self.file = 'ABC-123.mp4'  # 原文件名
        self.num = 'ABC-123'  # 车牌
        self.search = 'ABC%20123'  # 用于搜索javbus的车牌，javbus处理不了“-”“_”，算上“空格”，在url中把这三个换成了“%20”
        self.episodes = 1     # 第几集
        self.subt = ''        # 字幕文件名  ABC-123.srt


# 功能：获取用户选取的文件夹路径
# 参数：无
# 返回：路径str
# 辅助：tkinter.Tk，tkinter.filedialog，os.sep
def choose_directory():
    directory_root = Tk()
    directory_root.withdraw()
    path_work = filedialog.askdirectory()
    if path_work == '':
        print('你没有选择目录! 请重新选：')
        sleep(2)
        return choose_directory()
    else:
        # askdirectory 获得是 正斜杠 路径C:/，所以下面要把 / 换成 反斜杠\
        return path_work.replace('/', sep)


# 功能：检查 归类根目录 的合法性
# 参数：用户自定义的归类根目录，用户选择整理的文件夹路径
# 返回：归类根目录路径
# 辅助：os.sep
def check_classify_root(custom_root, root_choose):
    # 用户使用默认的“所选文件夹”
    if custom_root == '所选文件夹':
        return root_choose + sep + '归类完成'
    # 归类根目录 是 用户输入的路径c:\a，继续核实合法性
    else:
        custom_root = custom_root.rstrip(sep)
        # 用户输入的路径 不是 所选文件夹root_choose
        if custom_root != root_choose:
            if custom_root[:2] != root_choose[:2]:
                print('归类的根目录“', custom_root, '”和所选文件夹不在同一磁盘无法归类！请修正！')
                os.system('pause')
            if not exists(custom_root):
                print('归类的根目录“', custom_root, '”不存在！无法归类！请修正！')
                os.system('pause')
            return custom_root
        # 用户输入的路径 就是 所选文件夹root_choose
        else:
            return root_choose + sep + '归类完成'


# 功能：（如果需要为kodi整理头像）检查“演员头像for kodi.ini”、“演员头像”文件夹是否存在
# 参数：无
# 返回：无
# 辅助：os.path.exists，shutil.copyfile
def check_actors():
    if not exists('演员头像'):
        print('\n“演员头像”文件夹丢失！请把它放进exe的文件夹中！\n')
        os.system('pause')
    if not exists('【缺失的演员头像统计For Kodi】.ini'):
        if exists('actors_for_kodi.ini'):
            copyfile('actors_for_kodi.ini', '【缺失的演员头像统计For Kodi】.ini')
            print('\n“【缺失的演员头像统计For Kodi】.ini”成功！')
        else:
            print('\n请打开“【ini】重新创建ini.exe”创建丢失的程序组件!')
            os.system('pause')


# 功能：记录错误到txt
# 参数：错误信息
# 返回：无
# 辅助：无
def record_fail(fail_msg):
    print(fail_msg, end='')
    txt = open('【记得清理它】失败记录.txt', 'a', encoding="utf-8")
    txt.write(fail_msg)
    txt.close()
    

# 功能：记录旧文件名
# 参数：新文件名，旧文件名
# 返回：无
# 辅助：无
def record_video_old(name_new, name_old):
    txt = open('【记得清理它】原视频文件名清单.txt', 'a', encoding="utf-8")
    txt.write(name_new + ' ' + name_old + '\n')
    txt.close()


# 功能：判断是否有除了“.actors”"extrafanrt”外的其他文件夹
# 参数：文件夹list
# 返回：True
# 辅助：无
def check_extra_folders(lst_folders):
    for folder in lst_folders:
        if folder != '.actors' and folder != 'extrafanart':
            return True
    return False


# 功能：判断“原文件名”“旧nfo”是否有“中字”
# 参数：当前jav所处文件夹路径，jav文件名，判断文件名中的字词list，判断旧nfo中的字词list
# 返回：True
# 辅助：os.path.exists，xml.etree.ElementTree as ET，
def check_subt(root, jav_name, list_subt_video, list_subt_nfo):  #
    # 原文件名包含“-c、-C、中字”这些字符
    name_no_cd = jav_name.replace('-cd', '')
    for i in list_subt_video:
        if i in name_no_cd:
            return True
    # 先前的nfo中的“标题”、“标签”有 中字
    path_nfo_temp = root + sep + jav_name + '.nfo'
    if exists(path_nfo_temp):
        try:
            tree = ET.parse(path_nfo_temp)
        except ET.ParseError:  # nfo可能损坏
            return False
        for child in tree.getroot():
            if child.tag == 'title':
                for word in list_subt_nfo:
                    if word in child.text:
                        return True
            if child.text == '中文字幕':
                return True
    return False


# 功能：查看下载好的图片能否打开，是不是完好、没有损坏的图片
# 参数：图片路径
# 返回：True
# 辅助：Image.open
def check_pic(path):
    try:
        Image.open(path)
        return True
    except OSError:
        return False


# 功能：判断现在的”演员头像“文件夹有没有该演员的头像，如果有，是jpg还是png格式的图片；如果没有，记录在”【缺失的演员头像统计For Kodi】.ini“
# 参数：可能存在的头像路径（不含图片类型），演员姓名
# 返回：存在的演员头像图片的格式str，或者“暂无”
# 辅助：os.path.exists，configparser.RawConfigParser
def collect_sculpture(path_no_type, each_actor):
    # 演员jpg图片还没有
    if exists(path_no_type + '.jpg'):
        return '.jpg'
    elif exists(path_no_type + '.png'):
        return '.png'
    else:
        config_actor = RawConfigParser()
        config_actor.read('【缺失的演员头像统计For Kodi】.ini', encoding='utf-8-sig')
        try:
            each_actor_times = config_actor.get('缺失的演员头像', each_actor)
            config_actor.set("缺失的演员头像", each_actor, str(int(each_actor_times) + 1))
        except:
            config_actor.set("缺失的演员头像", each_actor, '1')
        config_actor.write(open('【缺失的演员头像统计For Kodi】.ini', "w", encoding='utf-8-sig'))
        return '暂无'


# 功能：去除xml文档不允许的特殊字符 &<>
# 参数：（文件名、简介、标题）str
# 返回：str
# 辅助：无
def replace_xml(name):
    # 替换xml中的不允许的特殊字符 .replace('\'', '&apos;').replace('\"', '&quot;')
    # .replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')  nfo基于xml，xml中不允许这5个字符，但实际测试nfo只不允许左边3个
    return name.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')\
                .replace('\n', '').replace('\t', '').replace('\r', '').rstrip()


# 功能：去除xml文档和windows路径不允许的特殊字符 &<>  \/:*?"<>|
# 参数：（文件名、简介、标题）str
# 返回：str
# 辅助：无
def replace_xml_win(name):
    # 替换windows路径不允许的特殊字符 \/:*?"<>|
    return name.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')\
                .replace('\n', '').replace('\t', '').replace('\r', '')\
                .replace("\\", "#").replace("/", "#").replace(":", "：").replace("*", "#")\
                .replace("?", "？").replace("\"", "#").replace("|", "#").rstrip()
