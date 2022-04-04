import os

from Classes.Model.JavFile import JavFile
from Classes.Handler.FileAnalyzer import FileAnalyzer
from Classes.Handler.FileExplorer import FileExplorer
from Classes.Handler.FileLathe import FileLathe
from Classes.Handler.MyLogger import MyLogger
from Classes.Model.JavData import JavData
from Classes.Static.Config import Ini
from Classes.Static.Const import Const
from Classes.Static.Enums import ScrapeStatusEnum
from Classes.Web.Arzon import Arzon
from Classes.Web.Baidu import Translator
from Classes.Web.Dmm import Dmm
from Classes.Web.JavBus import JavBus
from Classes.Web.JavDb import JavDb
from Classes.Web.JavLibrary import JavLibrary
from FileUtils import confirm_dir_exist
from Functions.Utils.Datetime import time_now
from Functions.Utils.JsonUtils import read_json_to_dict, write_json
from Functions.Utils.User import choose_directory
from Functions.Metadata.Car import extract_pref


def appoint_name(dict_json: dict):
    db = f'仓库{dict_json["JavDb"]}.' if dict_json['JavDb'] else ''
    library = f'图书馆{dict_json["JavLibrary"]}.' if dict_json['JavLibrary'] else ''
    bus = f'公交车{dict_json["JavBus"]}.' if dict_json['JavBus'] else ''
    arzon = f'阿如{dict_json["Arzon"]}.' if dict_json['Arzon'] else ''
    return f'{dict_json["Car"]}{db}{library}{bus}{arzon}mp4'


def repair_dict(dict_json: dict, jav_data: JavData):
    if jav_data.CarOrigin:
        dict_json['CarOrigin'] = jav_data.CarOrigin  # 2
    if jav_data.Series:
        dict_json['Series'] = jav_data.Series  # 3
    if jav_data.Title:
        dict_json['Title'] = jav_data.Title  # 4
    if jav_data.TitleZh:
        dict_json['TitleZh'] = jav_data.TitleZh  # 5
    if jav_data.Plot \
            and not jav_data.Plot.startswith('【arzon有该影片') \
            and not jav_data.Plot.startswith('【影片下架'):
        dict_json['Plot'] = jav_data.Plot  # 6
        dict_json['PlotZh'] = jav_data.PlotZh  # 7
    if jav_data.Review:
        dict_json['Review'] = jav_data.Review  # 8
    if jav_data.Release:
        dict_json['Release'] = jav_data.Release  # 9
    if jav_data.Runtime:
        dict_json['Runtime'] = jav_data.Runtime  # 10
    if jav_data.Director:
        dict_json['Director'] = jav_data.Director  # 11
    if jav_data.Studio:
        dict_json['Studio'] = jav_data.Studio  # 12
    if jav_data.Publisher:
        dict_json['Publisher'] = jav_data.Publisher  # 13
    if jav_data.Score:
        dict_json['Score'] = jav_data.Score  # 14
    if jav_data.CoverDb:
        dict_json['CoverDb'] = jav_data.CoverDb  # 15
    if jav_data.CoverLibrary:
        dict_json['CoverLibrary'] = jav_data.CoverLibrary  # 16
    if jav_data.CoverBus:
        dict_json['CoverBus'] = jav_data.CoverBus  # 17
    if jav_data.CoverDmm:
        dict_json['CoverDmm'] = jav_data.CoverDmm  # 18
    if jav_data.CutType:
        dict_json['CutType'] = jav_data.CutType  # 19
    if jav_data.JavDb:
        dict_json['JavDb'] = jav_data.JavDb  # 20
    if jav_data.JavLibrary:
        dict_json['JavLibrary'] = jav_data.JavLibrary  # 21
    if jav_data.JavBus:
        dict_json['JavBus'] = jav_data.JavBus  # 22
    if jav_data.Arzon:
        dict_json['Arzon'] = jav_data.Arzon  # 23
    if jav_data.CompletionStatus:
        dict_json['CompletionStatus'] = jav_data.CompletionStatus  # 24
    if jav_data.Genres:
        dict_json['Genres'] = jav_data.Genres  # 26
    if jav_data.Actors:
        dict_json['Actors'] = jav_data.Actors  # 27


logger = MyLogger()
ini = Ini(Const.YOUMA)
fileExplorer = FileExplorer(ini)
fileAnalyzer = FileAnalyzer(ini)
fileLathe = FileLathe(ini)
translator = Translator(ini)
javDb = JavDb(ini)
javLibrary = JavLibrary(ini)
dmm = Dmm(ini)
javBus = JavBus(ini)
arzon = Arzon(ini)

dir_choose = choose_directory()
list_wrong_genre = []
for root, dirs, files in os.walk(dir_choose):
    for file in files:
        if file.endswith(('.json',)):
            path = f'{root}\\{file}'
            dict_json = read_json_to_dict(path)
            print(f'>>正在处理: {path}')

            jav_file = JavFile(dict_json['Car'], appoint_name(dict_json), '', 1, '', 1)
            jav_data = JavData()

            # region从javdb获取信息
            javDb.scrape(jav_file, jav_data)
            # Todo找到一个才报警
            if javDb.status is ScrapeStatusEnum.not_found:
                logger.record_warn(f'javdb找不到该车牌的信息: {jav_file.Car}，')
            elif javDb.status is ScrapeStatusEnum.multiple_results:
                logger.record_fail(f'javlibrary搜索到同车牌的不同视频: {jav_file.Car}，')
            # endregion

            # 从javlibrary获取信息
            status = javLibrary.scrape(jav_file, jav_data)
            if status is ScrapeStatusEnum.not_found:
                logger.record_warn(f'javlibrary找不到该车牌的信息: {jav_file.Car}，')
            elif status is ScrapeStatusEnum.multiple_results:
                logger.record_fail(f'javlibrary搜索到同车牌的不同视频: {jav_file.Car}，')
            # endregion

            if not jav_data.JavDb and not jav_data.JavLibrary:
                logger.record_fail(f'Javdb和Javlibrary都找不到该车牌信息: {jav_file.Car}，')
                continue  # 结束对该jav的整理

            # 前往javbus查找【封面】【系列】【特征】.py
            status = javBus.scrape(jav_file, jav_data)
            if status is ScrapeStatusEnum.multiple_results:
                logger.record_warn(f'javbus搜索到同车牌的不同视频: {jav_file.Car}，')
            elif status is ScrapeStatusEnum.not_found:
                logger.record_warn(f'javbus有码找不到该车牌的信息: {jav_file.Car}，')
            # endregion

            # region arzon找简介
            status = arzon.scrape(jav_file, jav_data)
            url_search_arzon = f'https://www.arzon.jp/itemlist.html?t=&m=all&s=&q={jav_file.Car_search}'
            if status is ScrapeStatusEnum.exist_but_no_want:
                jav_data.Plot = '【arzon有该影片，但找不到简介】'
                logger.record_warn(f'找不到简介，尽管arzon上有搜索结果: {url_search_arzon}，')
            elif status is ScrapeStatusEnum.not_found:
                jav_data.Plot = '【影片下架，暂无简介】'
                logger.record_warn(f'找不到简介，影片被arzon下架: {url_search_arzon}，')

            jav_data.prefect_completion_status()
            translator.prefect_zh(jav_data)
            dict_json['Modify'] = time_now()

            dir_new = confirm_dir_exist(f'D:\\MyJava\\MyData\\AlreadyJsons\\修复jsons\\{extract_pref(dict_json["Car"])}')
            write_json(f'{dir_new}\\{file}', dict_json)
            print('    >写json成功')

            dir_transfer = confirm_dir_exist(
                f'D:\\MyJava\\MyData\\AlreadyJsons\\迁移jsons\\{extract_pref(dict_json["Car"])}')
            os.rename(path, f'{dir_transfer}\\{file}')
            print('    >迁移json成功')
