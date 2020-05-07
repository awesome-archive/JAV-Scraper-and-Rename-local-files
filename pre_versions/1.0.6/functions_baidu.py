# -*- coding:utf-8 -*-
import os, requests
from time import sleep, time
from hashlib import md5
from json import loads
from PIL import Image
# from traceback import format_exc


# 功能：调用百度翻译API接口，翻译日语简介
# 参数：百度翻译api账户api_id, key，需要翻译的内容，目标语言
# 返回：中文简介str
# 辅助：hashlib.md5，time.time，requests.get，json.loads
def tran(api_id, key, word, to_lang):
    for retry in range(10):
        # 把账户、翻译的内容、时间 混合md5加密，传给百度验证
        salt = str(time())[:10]
        final_sign = api_id + word + salt + key
        final_sign = md5(final_sign.encode("utf-8")).hexdigest()
        # 表单paramas
        paramas = {
            'q': word,
            'from': 'jp',
            'to': to_lang,
            'appid': '%s' % api_id,
            'salt': '%s' % salt,
            'sign': '%s' % final_sign
        }
        try:
            response = requests.get('http://api.fanyi.baidu.com/api/trans/vip/translate', params=paramas, timeout=(6, 7))
        except:
            print('    >百度翻译拉闸了...重新翻译...')
            continue
        content = str(response.content, encoding="utf-8")
        # 百度返回为空
        if not content:
            print('    >百度翻译返回为空...重新翻译...')
            sleep(1)
            continue
        # 百度返回了dict json
        json_reads = loads(content)
        if 'error_code' in json_reads:    # 返回错误码
            error_code = json_reads['error_code']
            if error_code == '54003':
                print('    >请求百度翻译太快...技能冷却1秒...')
                sleep(1)
            elif error_code == '54005':
                print('    >发送了太多超长的简介给百度翻译...技能冷却3秒...')
                sleep(3)
            elif error_code == '52001':
                print('    >连接百度翻译超时...重新翻译...')
            elif error_code == '52002':
                print('    >百度翻译拉闸了...重新翻译...')
            elif error_code == '54003':
                print('    >使用过于频繁，百度翻译不想给你用了...')
                os.system('pause')
            elif error_code == '52003':
                print('    >请正确输入百度翻译API账号，请阅读【使用说明】！')
                print('>>javsdt已停止工作...')
                os.system('pause')
            elif error_code == '58003':
                print('    >你的百度翻译API账户被百度封禁了，请联系作者，告诉你解封办法！“')
                print('>>javsdt已停止工作...')
                os.system('pause')
            elif error_code == '90107':
                print('    >你的百度翻译API账户还未通过认证或者失效，请前往API控制台解决问题！“')
                print('>>javsdt已停止工作...')
                os.system('pause')
            else:
                print('    >百度翻译error_code！请截图联系作者！', error_code)
            continue
        else:  # 返回正确信息
            return json_reads['trans_result'][0]['dst']
    print('    >翻译简介失败...请截图联系作者...')
    return '【百度翻译出错】' + word


# 功能：调用百度AL人体分析，分析图片中的人体
# 参数：图片路径，百度人体分析client
# 返回：鼻子的x坐标
# 辅助：cli.bodyAnalysis
def image_cut(path, cli):
    # if bool_face:   # 启动人体分析的这部分代码在主程序中
    #     client = AipBodyAnalysis(al_id, ai_ak, al_sk)
    for retry in range(10):
        with open(path, 'rb') as fp:
            image = fp.read()
        try:
            result = cli.bodyAnalysis(image)
            return int(result["person_info"][0]['body_parts']['nose']['x'])
        except:
            print('    >人体分析出现错误，请对照“人体分析错误表格”：', result)
            print('    >正在尝试重新人体检测...')
            continue
    print('    >人体分析无法使用...请先解决人体分析的问题，或截图联系作者...')
    os.system('pause')


# 功能：不使用人体分析，裁剪fanart封面作为poster，裁剪中间，或者裁剪右边
# 参数：已下载的fanart路径，目标poster路径， 选择模式（有码、无码是裁剪fanart右边，FC2和素人是裁剪fanart中间）
# 返回：无
# 辅助：Image.open
def crop_poster_default(path_fanart, path_poster, int_pattern):
    img = Image.open(path_fanart)
    wf, hf = img.size  # fanart的宽 高
    wide = int(hf * 2 / 3)  # 理想中海报的宽，应该是fanart的高的三分之二
    # 如果fanart特别“瘦”，宽不到高的三分之二，则以fanart现在的宽作为poster的宽，未来的高为宽的二分之三。
    if wf < wide:
        poster = img.crop((0, 0, wf, wf * 1.5))
        poster.save(path_poster, quality=95)  # quality=95 是无损crop，如果不设置，默认75
        print('    >poster.jpg裁剪成功')
    else:
        x_left = (wf - wide) / int_pattern  # / 2，poster裁剪fanart中间；/ 1，poster裁剪fanart右边。
        # crop
        poster = img.crop((x_left, 0, x_left + wide, hf))    # poster在fanart的 左上角(x_left, 0)，右下角(x_left + wide, hf)，
        poster.save(path_poster, quality=95)                 # 坐标轴的Y轴是反的
        print('    >poster.jpg裁剪成功')


# 功能：使用人体分析，裁剪fanart封面作为poster，围绕鼻子坐标进行裁剪
# 参数：已下载的fanart路径，目标poster路径， 百度人体分析client
# 返回：无
# 辅助：Image.open, image_cut()
def crop_poster_baidu(path_fanart, path_poster, client):
    img = Image.open(path_fanart)
    wf, hf = img.size  # fanart的宽 高
    wide = int(hf * 2 / 3)  # 理想中海报的宽，应该是fanart的高的三分之二
    # 如果fanart特别“瘦”，宽不到高的三分之二。以fanart的宽作为poster的宽。
    if wf < wide:
        poster = img.crop((0, 0, wf, wf * 1.5))
        poster.save(path_poster, quality=95)  # quality=95 是无损crop，如果不设置，默认75
        print('    >poster.jpg裁剪成功')
    else:
        wide_half = wide / 2
        # 使用人体分析，得到鼻子位置
        x_nose = image_cut(path_fanart, client)  # 鼻子的x坐标  0.704 0.653
        # 围绕鼻子进行裁剪，先来判断一下鼻子是不是太靠左或者太靠右
        if x_nose + wide_half > wf:  # 鼻子 + 一半poster宽超出fanart右边
            x_left = wf - wide  # 以右边为poster
        elif x_nose - wide_half < 0:  # 鼻子 - 一半poster宽超出fanart左边
            x_left = 0  # 以左边为poster
        else:  # 不会超出poster
            x_left = x_nose - wide_half  # 以鼻子为中心向两边扩展
        # crop
        poster = img.crop((x_left, 0, x_left + wide, hf))    # poster在fanart的 左上角(x_left, 0)，右下角(x_left + wide, hf)，
        poster.save(path_poster, quality=95)                 # 坐标轴的Y轴是反的
        print('    >poster.jpg裁剪成功')
