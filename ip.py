import re
import urllib.error
import urllib.request

import requests


def askurl(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/100.0.4896.75 Safari/537.36 Edg/100.0.1185.36 "
    }  # 告诉服务器是我们是什么来历(头文件)
    req = urllib.request.Request(url, headers=headers)
    html = ""
    try:
        response = urllib.request.urlopen(req, timeout=10)
        html = response.read().decode("gbk")
    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)
    return html


def get_location():
    try:
        text = requests.get('http://txt.go.sohu.com/ip/soip').text  # 读公网IP
        ip = re.findall(r'"(\d+\.\d+\.\d+\.\d+)"', text)

        url = "https://www.ip138.com/iplookup.asp?ip=" + ip[0] + "&action=2"  # 公网IP转化为实际地址信息

        match = re.compile(r'var ip_result =.*')
        res = str(match.search(askurl(url))).split(":")[1].split('"')[1].split(" ")

        if len(re.findall("省", res[0])) == 1:
            province = res[0].split("省")[0]
        else:
            province = None

        if len(re.findall("省", res[0])) == 1 and len(re.findall("市", res[0])) == 1:
            city = res[0].split("省")[1].split("市")[0]
        else:
            city = None

        if len(re.findall("省", res[0])) == 1 and len(re.findall("市", res[0])) == 1 and len(
                re.findall("区", res[0])) == 1:
            area = res[0].split("省")[1].split("市")[1].split("区")[0]
        else:
            area = None

        address = res[0]

        return province, city, area, address
    except requests.exceptions.ConnectionError:
        province = None
        city = None
        area = None
        address = "网络错误"

        return province, city, area, address

# print(res[0].split("省")[0])
# print(res[0].split("省")[1].split("市")[0])
# print(res[0].split("省")[1].split("市")[1].split("区")[0])
# print(res[0], res[2], res[3])  # 地址信息  网络运营商  网络范围
