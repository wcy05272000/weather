import requests  # 发送请求
import time
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# 获取时间戳

def get_earthquake():
    # 请求头
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Mobile Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate, br",
    }

    # 请求地址
    url = 'https://news.ceic.ac.cn/ajax/google'
    # 请求参数
    params = {
        "rand": str(time.time()).split('.')[0] + str(time.time()).split('.')[1][0:3],
    }

    o_time = []
    epi_lon = []
    epi_lat = []
    epi_depth = []
    m = []
    location_c = []
    num = 0

    # 发送请求
    r = requests.get(url, headers=headers, params=params, verify=False).json()

    for i in r:
        o_time.append(i['O_TIME'])
        epi_lon.append(i['EPI_LON'])
        epi_lat.append(i['EPI_LAT'])
        epi_depth.append(i['EPI_DEPTH'])
        m.append(i['M'])
        location_c.append(i['LOCATION_C'])
        num += 1

    return o_time, epi_lon, epi_lat, epi_depth, m, location_c, num
