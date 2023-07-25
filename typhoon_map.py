import re  # 正则表达式提取文本
import requests  # 发送请求

import time

import json


# 获取时间戳

def get_typhoon():
    # 请求头
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Mobile Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate, br",
    }

    # 请求地址
    url = 'http://typhoon.nmc.cn/weatherservice/typhoon/jsons/list_default'
    # 请求参数
    params = {
        "t": str(time.time()).split('.')[0] + str(time.time()).split('.')[1][0:3],
        "callback": 'typhoon_jsons_list_default',
    }

    typhoon_list = []

    # 发送请求
    r = requests.get(url, headers=headers, params=params).text

    findall = re.findall(r'[{](.*?)[}]', r)

    findall = '{' + findall[0] + '}'

    findall = json.loads(findall)

    for i in findall['typhoonList']:
        if i[-1] == 'start':
            typhoon_list.append(i[0])

    if len(typhoon_list) > 0:

        url2 = 'http://typhoon.nmc.cn/weatherservice/typhoon/jsons/view_' + str(typhoon_list[0])

        params2 = {
            "t": str(time.time()).split('.')[0] + str(time.time()).split('.')[1][0:3],
            "callback": 'typhoon_jsons_view_' + str(typhoon_list[0]),
        }

        r2 = requests.get(url2, headers=headers, params=params2).text

        findall2 = re.findall(r'[(](.*?)[)]', r2)

        findall2 = json.loads(findall2[0])

        num = len(findall2['typhoon'][8])

        time_c = []
        epi_lon = []
        epi_lat = []
        wind_speed = []
        pressure = []
        moving_direction = []
        moving_speed = []

        for i in range(num):
            time_c.append(findall2['typhoon'][8][i][1])
            epi_lon.append(findall2['typhoon'][8][i][4])
            epi_lat.append(findall2['typhoon'][8][i][5])
            wind_speed.append(findall2['typhoon'][8][i][7])
            pressure.append(findall2['typhoon'][8][i][6])
            moving_direction.append(findall2['typhoon'][8][i][8])
            moving_speed.append(findall2['typhoon'][8][i][9])

        return num, time_c, epi_lon, epi_lat, wind_speed, pressure, moving_direction, moving_speed

    else:
        num = 0
        time_c = []
        epi_lon = []
        epi_lat = []
        wind_speed = []
        pressure = []
        moving_direction = []
        moving_speed = []

        return num, time_c, epi_lon, epi_lat, wind_speed, pressure, moving_direction, moving_speed

