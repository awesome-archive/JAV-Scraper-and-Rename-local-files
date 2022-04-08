# # -*- coding:utf-8 -*-
# import os, requests
# from user import choose_directory
# from time import strftime, localtime, time
# from functions_json import check_lost_plot, check_lost_series, get_lib_dmm
#
#
# # from traceback import format_exc
#
#
# def get_dmm_html(url):
#     rqs = requests.get(url, timeout=10)
#     rqs.encoding = 'utf-8'
#     return(rqs.text)
#
#
# # print(check_lost_plot('abba-128'))
# root_choose = choose_directory()
# print(root_choose)
# # 在txt中记录一下用户的这次操作
# record_txt = open('失败记录.txt', 'a', encoding="utf-8")
# record_txt.write('已选择文件夹：' + root_choose + ' ' + strftime('%Y-%m-%d %H:%M:%S', localtime(time())) + '\n')
# record_txt.close()
# # 初始化：失败次数
# num_fail = 0
# for root, dirs, files in os.walk(root_choose):
#     # 是最底层的文件夹
#     if dirs:
#         continue
#     print('>>正在处理：', root)
#     # 这一层文件夹的车牌前缀
#     jav_pref = root.split('\\')[-1]
#     for file_raw in files:
#         path_json = root + '\\' + file_raw
#         bool_plot = bool_series = False
#         if check_lost_plot(path_json):
#             bool_plot = True
#             print('  >没有简介：', file_raw)
#         if check_lost_series(path_json):
#             bool_series = True
#             print('  >没有系列：', file_raw)
#         if bool_series or bool_plot:
#             lib_dmm = get_lib_dmm(path_json)
#             if not lib_dmm.startswith('未知'):
#                 url_dmm = 'https://www.dmm.co.jp/mono/dvd/-/detail/=/cid=' + lib_dmm
#                 print(url_dmm)
#                 html_dmm = get_dmm_html(url_dmm)
#                 print(html_dmm)
#                 os.system('pause')
#
