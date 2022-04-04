import os

from Functions.Metadata.Genre import better_dict_genres
from Functions.Utils.JsonUtils import read_json_to_dict
from Temp.JsonWorker.Base.Find import find_wrong_genre
from Functions.Utils.User import choose_directory

list_genres = list(better_dict_genres('JavDb', 'zh').values())
list_genres.extend(list(better_dict_genres('JavLibrary', 'zh').values()))
list_genres.extend(list(better_dict_genres('JavBus', 'zh').values()))
list_genres = list(set(list_genres))

dir_choose = choose_directory()
list_wrong_genre = []
for root, dirs, files in os.walk(dir_choose):
    for file in files:
        if file.endswith(('.json',)):
            path = f'{root}\\{file}'
            dict_json = read_json_to_dict(path)

            if genre := find_wrong_genre(dict_json, list_genres):
                list_wrong_genre.append(genre)
                print(file, genre)

print('OK!!!')
for genre in list(set(list_wrong_genre)):
    print(genre)
