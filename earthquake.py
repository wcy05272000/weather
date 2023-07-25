import re  # 正则表达式提取文本
import requests  # 发送请求
import datetime  #


def trans_time(v_str):
    """转换GMT时间为标准格式"""
    GMT_FORMAT = '%a %b %d %H:%M:%S +0800 %Y'
    timeArray = datetime.datetime.strptime(v_str, GMT_FORMAT)
    ret_time = timeArray.strftime("%Y-%m-%d %H:%M:%S")
    return ret_time


def get_earthquake(since_id=None):
    # 请求头
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Mobile Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate, br",
    }

    # 请求地址
    url = 'https://m.weibo.cn/api/container/getIndex'
    # 请求参数
    params = {
        'uid': '2817059020',
        'luicode': '10000011',
        'lfid': '100103type=1&q=中国地震',
        'type': 'uid',
        'value': '2817059020',
        'containerid': '1076032817059020',
        'since_id': since_id
    }
    # 发送请求
    r = requests.get(url, headers=headers, params=params)

    try:
        next_since_id = r.json()["data"]['cardlistInfo']['since_id']

        res = []

        for i in range(9):

            cards = r.json()["data"]["cards"][i]["mblog"]["text"]

            pattern = re.compile(r'<[^>]+>', re.S)

            if len(pattern.sub('', cards).split("#")) > 1:

                if pattern.sub('', cards).split("#")[1] == "地震快讯":
                    result = pattern.sub('', cards).split("#")[2]

                    result = re.sub(u"\\（.*?）|\\{.*?}|\\[.*?]|\\【.*?】", "", result.encode('utf-8').decode())

                    result = result.split('：')[0] + ' ' + result.split('：')[1].split('在')[0] + '\n      ' + \
                             result.split('：')[1].split('在')[1] + '\n\n'

                    res.append(result)

        return res, next_since_id

    except KeyError:
        pass


def more_information():
    global return_data

    res = []
    for i in range(5):
        if i == 0:
            return_data = get_earthquake()
            res.append(return_data[0])
        else:
            return_data = get_earthquake(return_data[1])
            res.append(return_data[0])

    return res

# print(cards)

# # 转发数
# reposts_count_list = jsonpath(cards, '$..mblog.reposts_count')
# # 评论数
# comments_count_list = jsonpath(cards, '$..mblog.comments_count')
# # 点赞数
# attitudes_count_list = jsonpath(cards, '$..mblog.attitudes_count')
#
# print(reposts_count_list)
# print(comments_count_list)
# print(attitudes_count_list)
