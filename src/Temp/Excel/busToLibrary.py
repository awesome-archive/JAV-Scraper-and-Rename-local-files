# -*- coding:utf-8 -*-
from Dict import *

list_no = []

for key in dict_bus_wuma:
    if key in dict_library:
        if dict_bus_wuma[key] != dict_library[key]:
            dict_bus_wuma[key] = dict_library[key]
            print(dict_bus_wuma[key])
    elif key in dict_db_youma:
        if dict_bus_wuma[key] != dict_db_youma[key]:
            dict_bus_wuma[key] = dict_db_youma[key]
            print(dict_bus_wuma[key])
    elif key in dict_bus_youma:
        if dict_bus_wuma[key] != dict_bus_youma[key]:
            dict_bus_wuma[key] = dict_bus_youma[key]
            print(dict_bus_wuma[key])
    else:
        list_no.append(key)

print(dict_bus_wuma)

for i, key in enumerate(list_no, start=1):
    print(i, key)
