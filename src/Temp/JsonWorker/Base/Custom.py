import os

from Functions.Utils.JsonUtils import read_json_to_dict


# 检查某一路径的json是否没有“剧情”
def check_lost_plot(path):
    if os.path.exists(path):
        dict_json = read_json_to_dict(path)
        # print('当前plot如下')
        # print('plot:', dict_json['plot'])
        return dict_json['plot'] == '未知简介'
    else:
        print('  >没有json：', path)
        return False


# 检查某一路径的json是否没有 系列
def check_lost_series(path):
    if os.path.exists(path):
        dict_json = read_json_to_dict(path)
        return dict_json['series'] == '未知系列'
    else:
        print('  >没有json：', path)
        return False


def modify_cover_dmm(dict_json: dict):
    if 'dmm.co.jp' in dict_json['CoverLibrary']:
        dict_json['CoverDmm'] = dict_json['CoverLibrary']
        dict_json['CoverLibrary'] = ''


def big_ten_cover_dmm(dict_json: dict):
    if dict_json['Score'] < 10:
        dict_json['Score'] = dict_json['Score'] * 10
        print('扩大', dict_json['Score'])
    else:
        print('不需', dict_json['Score'])
