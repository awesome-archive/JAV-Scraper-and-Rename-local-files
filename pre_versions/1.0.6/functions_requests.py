# -*- coding:utf-8 -*-
import os, requests, re
from PIL import Image
from time import sleep
from re import search
from cfscrape import get_cookie_string
# from traceback import format_exc

# 功能：请求各大jav网站和arzon的网页
# 参数：网址url，请求头部header/cookies，代理proxy
# 返回：网页html，请求头部


#################################################### arzon ########################################################
# 获取一个arzon_cookie，返回cookie
def steal_arzon_cookies(proxy):
    print('\n正在尝试通过“https://www.arzon.jp”的成人验证...')
    for retry in range(10):
        try:    # 当初费尽心机，想办法如何通过页面上的成人验证，结果在一个C#开发的jav爬虫项目，看到它请求以下网址，再跳转到arzon主页，所得到的的cookie即是合法的cookie
            if proxy:
                session = requests.Session()
                session.get('https://www.arzon.jp/index.php?action=adult_customer_agecheck&agecheck=1&redirect=https%3A%2F%2Fwww.arzon.jp%2F', proxies=proxy, timeout=(6, 7))
                print('通过arzon的成人验证！\n')
                return session.cookies.get_dict()
            else:
                session = requests.Session()
                session.get('https://www.arzon.jp/index.php?action=adult_customer_agecheck&agecheck=1&redirect=https%3A%2F%2Fwww.arzon.jp%2F', timeout=(6, 7))
                print('通过arzon的成人验证！\n')
                return session.cookies.get_dict()
        except:
            # print(format_exc())
            print('通过失败，重新尝试...')
            continue
    print('>>请检查你的网络环境是否可以打开：https://www.arzon.jp/')
    os.system('pause')


# 搜索arzon，或请求arzon上jav所在网页，返回html
def get_arzon_html(url, cookies, proxy):
    # print('代理：', proxy)
    for retry in range(10):
        try:
            if proxy:
                rqs = requests.get(url, cookies=cookies, proxies=proxy, timeout=(6, 7))
            else:
                rqs = requests.get(url, cookies=cookies, timeout=(6, 7))
        except:
            print('    >打开网页失败，重新尝试...')
            continue
        rqs.encoding = 'utf-8'
        rqs_content = rqs.text
        if search(r'arzon', rqs_content):
            return rqs_content
        else:
            print('    >打开网页失败，空返回...重新尝试...')
            continue
    print('>>请检查你的网络环境是否可以打开：', url)
    os.system('pause')


#################################################### javlibrary ########################################################
# 获取一个library_cookie，返回cookie
def steal_library_header(url, proxy):
    print('\n正在尝试通过', url, '的5秒检测...如果超过20秒卡住...重启程序...')
    for retry in range(10):
        try:
            if proxy:
                cookie_value, user_agent = get_cookie_string(url, proxies=proxy, timeout=15)
            else:
                cookie_value, user_agent = get_cookie_string(url, timeout=15)
            print('通过5秒检测！\n')
            return {'User-Agent': user_agent, 'Cookie': cookie_value}
        except:
            print('通过失败，重新尝试...')
            continue
    print('>>通过javlibrary的5秒检测失败：', url)
    os.system('pause')


# 搜索javlibrary，或请求javlibrary上jav所在网页，返回html
def get_library_html(url, header, proxy):
    for retry in range(10):
        try:
            if proxy:
                rqs = requests.get(url, headers=header, proxies=proxy, timeout=(6, 7), allow_redirects=False)
            else:
                rqs = requests.get(url, headers=header, timeout=(6, 7), allow_redirects=False)
        except:
            print('    >打开网页失败，重新尝试...')
            continue
        rqs.encoding = 'utf-8'
        rqs_content = rqs.text
        # print(rqs_content)
        if search(r'JAVLibrary', rqs_content):        # 得到想要的网页，直接返回
            return rqs_content, header
        elif search(r'javli', rqs_content):           # 搜索车牌后，javlibrary跳转前的网页
            url = url[:23] + search(r'(\?v=javli.+?)"', rqs_content).group(1)    # rqs_content是一个非常简短的跳转网页，内容是目标jav所在网址
            if len(url) > 70:                          # 跳转车牌特别长，cf已失效
                header = steal_library_header(url[:23], proxy)  # 更新header后继续请求
                continue
            print('    >获取信息：', url)
            continue                                  # 更新url后继续requests.get
        elif search(r'Compatible', rqs_content):     # cf检测
            header = steal_library_header(url[:23], proxy)    # 更新header后继续请求
            continue
        else:                                         # 代理工具返回的错误信息
            print('    >打开网页失败，空返回...重新尝试...')
            continue
    print('>>请检查你的网络环境是否可以打开：', url)
    os.system('pause')


#################################################### javbus ########################################################
# 搜索javbus，或请求javbus上jav所在网页，返回html
def get_bus_html(url, proxy):
    for retry in range(10):
        try:
            if proxy:       # existmag=all为了 获得所有影片，而不是默认的有磁力的链接
                rqs = requests.get(url, proxies=proxy, timeout=(6, 7), headers={'Cookie': 'existmag=all'})
            else:
                rqs = requests.get(url, timeout=(6, 7), headers={'Cookie': 'existmag=all'})
        except:
            # print(format_exc())
            print('    >打开网页失败，重新尝试...')
            continue
        rqs.encoding = 'utf-8'
        rqs_content = rqs.text
        if search(r'JavBus', rqs_content):
            return rqs_content
        else:
            print('    >打开网页失败，空返回...重新尝试...')
            continue
    print('>>请检查你的网络环境是否可以打开：', url)
    os.system('pause')


#################################################### jav321 ########################################################
# 用户指定jav321的网址后，请求jav所在网页，返回html
def get_321_html(url, proxy):
    for retry in range(10):
        try:
            if proxy:
                rqs = requests.get(url, proxies=proxy, timeout=(6, 7))
            else:
                rqs = requests.get(url, timeout=(6, 7))
        except:
            print('    >打开网页失败，重新尝试...')
            continue
        rqs.encoding = 'utf-8'
        rqs_content = rqs.text
        if search(r'JAV321', rqs_content):
            return rqs_content
        else:
            print('    >打开网页失败，空返回...重新尝试...')
            continue
    print('>>请检查你的网络环境是否可以打开：', url)
    os.system('pause')


# 向jav321 post车牌，得到jav所在网页，也可能是无结果的网页，返回html
def post_321_html(url, data, proxy):
    for retry in range(10):
        try:
            if proxy:
                rqs = requests.post(url, data=data, proxies=proxy, timeout=(6, 7))
            else:
                rqs = requests.post(url, data=data, timeout=(6, 7))
        except:
            # print(format_exc())
            print('    >打开网页失败，重新尝试...')
            continue
        rqs.encoding = 'utf-8'
        rqs_content = rqs.text
        if search(r'JAV321', rqs_content):
            return rqs_content
        else:
            print('    >打开网页失败，空返回...重新尝试...')
            continue
    print('>>请检查你的网络环境是否可以打开：', url)
    os.system('pause')


#################################################### javdb ########################################################
# 搜索javdb，得到搜索结果网页，返回html。
def get_search_db_html(url, proxy):
    for retry in range(10):
        try:
            if proxy:
                rqs = requests.get(url, proxies=proxy, timeout=(6, 7))
            else:
                rqs = requests.get(url, timeout=(6, 7))
        except:
            # print(format_exc())
            print('    >打开网页失败，重新尝试...')
            continue
        rqs.encoding = 'utf-8'
        rqs_content = rqs.text
        if search(r'JavDB', rqs_content):
            if search(r'搜索結果', rqs_content):
                return rqs_content
            else:
                print('    >睡眠5分钟...')
                sleep(300)
                continue
        else:
            print('    >打开网页失败，空返回...重新尝试...')
            continue
    print('>>请检查你的网络环境是否可以打开：', url)
    os.system('pause')


# 请求jav在javdb上的网页，返回html
def get_db_html(url, proxy):
    for retry in range(10):
        try:
            if proxy:
                rqs = requests.get(url, proxies=proxy, timeout=(6, 7))
            else:
                rqs = requests.get(url, timeout=(6, 7))
        except:
            # print(format_exc())
            print('    >打开网页失败，重新尝试...')
            continue
        rqs.encoding = 'utf-8'
        rqs_content = rqs.text
        if search(r'JavDB', rqs_content):
            if search(r'content="JavDB', rqs_content):
                return rqs_content
            else:
                print('    >睡眠5分钟...')
                sleep(300)
                continue
        else:
            print('    >打开网页失败，空返回...重新尝试...')
            continue
    print('>>请检查你的网络环境是否可以打开：', url)
    os.system('pause')


#################################################### 下载图片 ########################################################
# 下载图片，无返回
def download_pic(url, path, proxy):
    for retry in range(5):
        try:
            if proxy:
                r = requests.get(url, proxies=proxy, stream=True, timeout=(6, 10))
                with open(path, 'wb') as pic:
                    for chunk in r:
                        pic.write(chunk)
            else:
                r = requests.get(url, stream=True, timeout=(6, 10))
                with open(path, 'wb') as pic:
                    for chunk in r:
                        pic.write(chunk)
        except:
            # print(format_exc())
            print('    >下载失败，重新下载...')
            continue
        # 如果下载的图片打不开，则重新下载
        try:
            Image.open(path)
            return
        except OSError:
            print('    >下载失败，重新下载....')
            continue
    raise Exception('    >下载多次，仍然失败！')
