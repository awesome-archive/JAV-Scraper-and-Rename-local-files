# import xlsxwriter
# from langconv import *
# from Dict import *
#
#
# # 转换简体到繁体
# def chs_to_cht(line):
#     line = Converter('zh-hant').convert(line)
#     line.encode('utf-8')
#     return line
#
#
# def add(workbook, sheet_name, centered, dict):
#     # excel添加一页sheet，命名为 Javbus有码
#     sheet = workbook.add_worksheet(sheet_name)
#     sheet.write(0, 0, '原简体特征', centered)
#     sheet.write(0, 1, '简体', centered)
#     sheet.write(0, 2, '繁体', centered)
#     sheet.write(0, 3, '日语', centered)
#     for row, key in enumerate(dict, start=1):
#         sheet.write(row, 0, key, centered)
#
#         sheet.write(row, 1, dict[key], centered)
#
#         if dict[key] == '删除':
#             sheet.write(row, 2, '删除', centered)
#         else:
#             sheet.write(row, 2, chs_to_cht(dict[key]), centered)
#
#
# path_excel = '【特征对照表】.xlsx'
# workbook = xlsxwriter.Workbook(path_excel)  # 目标是完成一个'example.xlsx'
# centered = workbook.add_format({'align': 'center'})  # 写excel的单元格，使用的对齐方式：居中
# add(workbook, 'Javlibrary', centered, dict_library)
# add(workbook, 'Javbus有码', centered, dict_bus_youma)
# add(workbook, 'Javbus无码', centered, dict_bus_wuma)
# add(workbook, 'JavdbFc2', centered, dict_db_fc2)
# add(workbook, 'Javdb有码', centered, dict_db_youma)
#
# # 保存xlsx文件
# workbook.close()
