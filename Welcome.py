import datetime
import math
import os
import platform
import re
import subprocess
import sys
from threading import Thread

import folium
import pandas as pd
import pymysql
import requests
from PySide2.QtCore import QEvent, Qt, QDateTime, QTimer, QRect, QStringListModel, QUrl, QTranslator
from PySide2.QtGui import QPixmap, QPainter, QPen, QDesktopServices, QFont, QMovie
from PySide2.QtWidgets import QWidget, QApplication, QCompleter, QGraphicsDropShadowEffect, QMenu

import earthquake
import typhoon_map
import earthquake_map
import ip
import systemtheme
from WelcomeUI import Ui_Form


class MyWelcomeWindow(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.map_lon = None
        self.map_lat = None
        self.aqi_now = -1
        self.all_check_lock = True  # 用于修正全选天气指数时的一些错误
        self.favorites_province_text = None  # 用于记录收藏夹 省份文本
        self.favorites_city_text = None  # 用于记录收藏夹 城市文本
        self.favorites_city_list = []  # 收藏城市列表
        self.favorites_city_success = False  # 是否收藏城市
        self.search_datetime = datetime.datetime.now()  # 当前时间
        self.theme_color_dark_lock = True
        self.theme_color_light_lock = True
        self.allow_follow_success_theme = False
        self.cityname = []
        self.theme_color = None
        self.allow_location_start = False
        self.allow_location_ip_start = False

        self.location_x = 0  # location Label x轴
        self.location_ip_x = 0  # location_ip Label x轴
        self.lock_search = False  # 搜索框锁

        self.api_key = None  # 认证码
        self.api_key_Check_success = False  # 判断认证码是否正确

        self.location_text = None  # location Label 文本
        self.location_ip_text = None  # location_ip Label 文本
        self.city = None  # 城市名称
        self.province = None  # 省份名称
        self.cityid = None  # 城市id
        self.completer_city = None  # 匹配城市容器
        self.get_weather_success = False  # 是否成功获取天气
        self.internet_connect_success = False  # 网络连接是否正常
        self.page_tip_count = None  # 警告数量
        self.page_life_weather_count = None  # 天气指数数量
        self.get_city_id_way = 1  # 获取城市id方式（1.网络查询2.本地excel查询）
        self.life_weather_checkBox_list_isCheck = []  # 生活天气指数选中列表
        self.life_weather_checkBox_list_isCheck_old = []  # 用于内部存储生活天气指数
        self.life_weather_checkBox_list_isCheck_old_str = []
        self.life_weather_checkBox_list_isCheck_save = []  # 用于外部存储生活天气指数

        self.window_point = None  # 窗口坐标
        self.start_point = None  # 鼠标坐标
        self.ismoving = False  # 是否允许移动

        self.window_point_2 = None  # 窗口坐标
        self.start_point_2 = None  # 鼠标坐标
        self.ismoving_2 = None  # 是否允许移动

        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.Timer = QTimer()  # 该定时器负责持续对程序变量进行状态扫描
        self.Timer.timeout.connect(self.thread_control)
        self.Timer.timeout.connect(self.start_thread)
        self.Timer.timeout.connect(self.update_ui)
        self.Timer.start(100)

        self.Timer_internet = QTimer()  # 更新LCD时间定时器
        self.Timer_internet.timeout.connect(self.start_thread_8)

        self.Timer_now_weather = QTimer()  # 更新实时天气定时器
        self.Timer_now_weather.timeout.connect(self.start_thread_1)
        self.Timer_now_weather.timeout.connect(self.start_thread_3)

        self.Timer_earthquake = QTimer()
        self.Timer_earthquake.timeout.connect(self.start_thread_9)
        self.Timer_earthquake.start(600000)

        self.Timer_paint_location_ip = QTimer()
        self.Timer_paint_location_ip.timeout.connect(self.paint_location_ip_time_lock)

        self.Timer_paint_location = QTimer()
        self.Timer_paint_location.timeout.connect(self.paint_location_time_lock)

        self.ui.title.clicked.connect(self.show_setting)

        self.ui.favorites.clicked.connect(self.show_favorites_listView)

        self.ui.favorites_listView.clicked.connect(self.select_favorites_city)

        self.ui.search_favorites.clicked.connect(self.favorites_city_clicked)

        # 信号 点击后从网络获取界面信息
        self.ui.searchButton.clicked.connect(self.start_thread_7)

        # 信号 设置界面的取消和保存按钮
        self.ui.closeButton_dialog.clicked.connect(self.read_old_setting)
        self.ui.saveButton_dialog.clicked.connect(self.change_setting)

        # 信号 转至天气详情的关联函数信号
        self.ui.now_weather_detailed.clicked.connect(self.change_to_now_weather_detailed)
        self.ui.stackedWidget_weather.currentChanged.connect(self.change_now_weather_detailed_icon)

        #  天气预警切换界面
        self.ui.change_page_tip_left.clicked.connect(self.change_page_tip_left)
        self.ui.change_page_tip_right.clicked.connect(self.change_page_tip_right)

        #  天气指数切换界面
        self.ui.change_page_life_weather_right.clicked.connect(self.change_page_life_weather_right)
        self.ui.change_page_life_weather_left.clicked.connect(self.change_page_life_weather_left)

        #  天气指数全选
        self.ui.life_weather_all_checkBox.clicked.connect(self.life_weather_all_check)
        for i in range(16):
            self.ui.life_weather_checkBox_[i].stateChanged.connect(self.life_weather_all_check_2)

        #  信号 点击后通过IP获取地址
        self.ui.location_ip_Button.clicked.connect(self.start_thread_6)

        #  信号 搜索框编辑结束与字符改变信号
        self.ui.search.editingFinished.connect(self.lock_search_even)
        self.ui.search.textChanged.connect(self.search_completer)

        #  信号 主题颜色
        self.ui.select_color_dark.clicked.connect(self.ui_style_dark)
        self.ui.select_color_light.clicked.connect(self.ui_style_light)
        self.ui.select_color_system_button.clicked.connect(self.allow_follow_system_theme_click)

        #  信号 打开网页
        self.ui.typhoon_web_button.clicked.connect(self.open_typhoon_web)
        self.ui.get_api_key_button.clicked.connect(self.get_api_key_web)
        self.ui.earthquake_web_button.clicked.connect(self.get_earthquake_web)

        #  信号 打开地图
        self.ui.map_Button.clicked.connect(self.show_map)

        #  背景阴影
        self.add_shadow(self.ui.background)  # 将设置套用到窗口中
        self.add_shadow(self.ui.dialog)

        self.loading_earthquake = QMovie('icon/loading.gif')
        self.loading_day_weather = QMovie('icon/loading.gif')
        self.ui.movie_earthquake.setMovie(self.loading_earthquake)
        self.ui.movie_day_weather.setMovie(self.loading_day_weather)

        self.ui.favorites_listView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.favorites_listView.customContextMenuRequested.connect(self.listWidgetContext)

        self.init_ui()  # 初始化UI
        self.init_base()  # 初始化
        self.thread_init()  # 初始化

    # 添加阴影
    def add_shadow(self, obj):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setOffset(0, 0)  # 偏移
        shadow.setBlurRadius(30)  # 阴影半径
        shadow.setColor(Qt.black)  # 阴影颜色
        obj.setGraphicsEffect(shadow)  # 将设置套用到窗口中

    ##################################################################################################
    ##################################################################################################
    ##################################################################################################

    # 事件筛选器
    def eventFilter(self, obj, event):
        if obj == self.ui.search:
            if event.type() == QEvent.FocusIn or event.type() == QEvent.MouseButtonRelease:
                self.ui.search.setPlaceholderText("")

                if self.lock_search:
                    if len(self.ui.search.text()) > 0:
                        self.ui.search.completer().complete(self.ui.search.rect())

                elif event.type() == QEvent.FocusOut:
                    if self.theme_color == 'light':
                        self.ui.search.setStyleSheet(
                            u"QLineEdit{font-size:16px;border-top:0px  solid;border-bottom:1px  solid;"
                            "border-left:0px  solid;border-right: 0px  solid;border-bottom-color:black;"
                            "background-color:transparent;color:black;}")

                    elif self.theme_color == 'dark':
                        self.ui.search.setStyleSheet(
                            u"QLineEdit{font-size:16px;border-top:0px  solid;border-bottom:1px  solid;"
                            "border-left:0px  solid;border-right: 0px  solid;border-bottom-color:white;"
                            "background-color:transparent;color:white;}")

                    # self.ui.search.setPlaceholderText("市/县/区")

            elif event.type() == QEvent.MouseButtonPress:
                self.ui.favorites_listView.hide()

            else:
                pass

        elif obj == self.ui.dialog:
            if event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
                self.ismoving_2 = True
                self.start_point_2 = event.globalPos()  # globalPosition().toPoint() Pyside6
                self.window_point_2 = self.ui.dialog.frameGeometry().topLeft()
            elif event.type() == QEvent.MouseMove:
                if self.ismoving_2:
                    relpos = event.globalPos() - self.start_point_2  # globalPosition().toPoint() Pyside6
                    self.ui.dialog.move(self.window_point_2 + relpos)
            elif event.type() == QEvent.MouseButtonRelease:
                self.ismoving_2 = False
            else:
                pass

        elif obj == self.ui.title:
            if event.type() == QEvent.Enter:
                self.ui.title.setText("")
                if self.theme_color == 'light':
                    self.ui.title.setStyleSheet(
                        u"QPushButton{background-color:transparent;image: url(icon/setblack.png);}")
                elif self.theme_color == 'dark':
                    self.ui.title.setStyleSheet(u"QPushButton{background-color:transparent;image: url(icon/set.png);}")
            elif event.type() == QEvent.Leave:
                if self.theme_color == 'light':
                    self.ui.title.setStyleSheet(u"QPushButton{background-color:transparent;color:black;image: none;}")
                elif self.theme_color == 'dark':
                    self.ui.title.setStyleSheet(u"QPushButton{background-color:transparent;color:white;image: none;}")
                self.ui.title.setText("天气")
            else:
                pass

        elif obj == self.ui.location or self.ui.location_ip:
            if self.ui.location.fontMetrics().size(Qt.TextSingleLine, self.location_text).width() > \
                    self.ui.location.width():
                if event.type() == QEvent.Paint:
                    self.paint_location()

            if self.ui.location_ip.fontMetrics().size(Qt.TextSingleLine, self.location_ip_text).width() > \
                    self.ui.location_ip.width():
                if event.type() == QEvent.Paint:
                    self.paint_location_ip()

            if event.type() == QEvent.MouseButtonPress:
                self.ui.search.setPlaceholderText("市/县/区")
                self.ui.search.clearFocus()
                if event.button() == Qt.LeftButton:
                    if self.ui.minButton.y() < event.globalPos().y() - self.frameGeometry().y() < \
                            (self.ui.minButton.y() + self.ui.minButton.height()):
                        self.ismoving = True
                        self.start_point = event.globalPos()  # globalPosition().toPoint() Pyside6
                        self.window_point = self.frameGeometry().topLeft()
            elif event.type() == QEvent.MouseMove:
                if self.ismoving:
                    relpos = event.globalPos() - self.start_point  # globalPosition().toPoint() Pyside6
                    self.move(self.window_point + relpos)
            elif event.type() == QEvent.MouseButtonRelease:
                self.ismoving = False

            else:
                pass

        return False  # eventFilter必须返回一个布尔值

        ##################################################################################################
        ##################################################################################################
        ##################################################################################################

        # 文字过长时，绘制跑马字幕

    def paint_location(self):
        painter = QPainter(self.ui.location)
        painter.setPen(QPen(Qt.white, 1, Qt.SolidLine))
        painter.drawText(self.location_x -
                         (1 * self.ui.location.fontMetrics().size(Qt.TextSingleLine, self.location_text).width()),
                         0, self.ui.location.fontMetrics().size(Qt.TextSingleLine, self.location_text).width(),
                         30, Qt.AlignHCenter, self.location_text)

        if self.location_x < self.ui.location.width() + \
                (1 * self.ui.location.fontMetrics().size(Qt.TextSingleLine, self.location_text).width()):
            self.location_x += 0.2
        else:
            self.location_x = -(0.8 * self.ui.location.fontMetrics().size(Qt.TextSingleLine,
                                                                          self.location_text).width())

    def paint_location_ip(self):
        painter = QPainter(self.ui.location_ip)
        painter.setPen(QPen(Qt.white, 1, Qt.SolidLine))
        painter.drawText(self.location_ip_x -
                         (1 * self.ui.location_ip.fontMetrics().size(Qt.TextSingleLine, self.location_ip_text).width()),
                         5, self.ui.location_ip.fontMetrics().size(Qt.TextSingleLine, self.location_ip_text).width(),
                         30, Qt.AlignHCenter, self.location_ip_text)

        if self.location_ip_x < self.ui.location_ip.width() + \
                (1 * self.ui.location_ip.fontMetrics().size(Qt.TextSingleLine, self.location_ip_text).width()):
            self.location_ip_x += 0.2
        else:
            self.location_ip_x = -(0.8 * self.ui.location_ip.fontMetrics().size(Qt.TextSingleLine, self.location_text).
                                   width())

    def paint_location_time_lock(self):

        self.ui.location.update()

    def paint_location_ip_time_lock(self):

        self.ui.location_ip.update()

    ##################################################################################################
    ##################################################################################################
    ##################################################################################################

    # 检查网络
    def check_internet(self):
        cmd = 'ping baidu.com -n 1'
        ret = subprocess.call(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # ret = os.system("ping baidu.com -n 1")
        if ret == 0:
            self.ui.location.setText("")
            self.ui.location_ip.setText("")
            self.check_key()
            self.start_thread_9()
        else:
            pass

    ##################################################################################################
    ##################################################################################################
    ##################################################################################################

    # 搜索框编辑完毕后 锁定操作 （使得自动填充可以弹出）
    def lock_search_even(self):

        self.lock_search = True

    ##################################################################################################
    ##################################################################################################
    ##################################################################################################

    # 检查key
    def check_key(self):
        # 读key，并验证
        try:
            self.internet_connect_success = True

            if len(self.ui.search.text()) == 0:
                text = requests.get('https://geoapi.qweather.com/v2/city/lookup?location=101010100&key=' +
                                    str(self.api_key))

                text.encoding = 'utf-8'

                if text.json()['code'] == str(200):
                    self.api_key_Check_success = True
                    self.ui.location.setText("")
                    self.ui.api_key_QLineEdit.setText(self.api_key)
                    self.ui.api_key_QLineEdit.setReadOnly(True)
                    self.ui.api_key_QLineEdit.setFocusPolicy(Qt.NoFocus)
                    if self.theme_color == 'light':
                        self.ui.check_api_key_icon.setPixmap(QPixmap('icon/round_checkblack.png'))
                    elif self.theme_color == 'dark':
                        self.ui.check_api_key_icon.setPixmap(QPixmap('icon/round_check.png'))
                    self.ui.check_api_key_icon.setToolTip("认证成功")

                elif text.json()['code'] == str(401):
                    self.api_key_Check_success = False
                    self.ui.location.setText("认证失败")
                    if self.theme_color == 'light':
                        self.ui.check_api_key_icon.setPixmap(QPixmap('icon/errorblack.png'))
                    elif self.theme_color == 'dark':
                        self.ui.check_api_key_icon.setPixmap(QPixmap('icon/error.png'))
                    self.ui.check_api_key_icon.setToolTip("认证失败")

                else:
                    pass

            else:
                text = requests.get('https://geoapi.qweather.com/v2/city/lookup?location=' +
                                    self.ui.search.text() + '&key=' + self.api_key)

                text.encoding = 'utf-8'

                if text.json()['code'] == str(200):
                    self.api_key_Check_success = True
                    self.ui.location.setText("")
                    self.ui.api_key_QLineEdit.setText(self.api_key)
                    self.ui.api_key_QLineEdit.setReadOnly(True)
                    self.ui.api_key_QLineEdit.setFocusPolicy(Qt.NoFocus)
                    if self.theme_color == 'light':
                        self.ui.check_api_key_icon.setPixmap(QPixmap('icon/round_checkblack.png'))
                    elif self.theme_color == 'dark':
                        self.ui.check_api_key_icon.setPixmap(QPixmap('icon/round_check.png'))
                    self.ui.check_api_key_icon.setToolTip("认证成功")

                    self.cityid = text.json()['location'][0]['id']
                    self.province = text.json()['location'][0]['adm1']
                    self.city = text.json()['location'][0]['adm2']

                elif text.json()['code'] == str(401):
                    self.api_key_Check_success = False
                    self.ui.location.setText("认证失败")
                    if self.theme_color == 'light':
                        self.ui.check_api_key_icon.setPixmap(QPixmap('icon/errorblack.png'))
                    elif self.theme_color == 'dark':
                        self.ui.check_api_key_icon.setPixmap(QPixmap('icon/error.png'))
                    self.ui.check_api_key_icon.setToolTip("认证失败")

                else:
                    pass

            if self.api_key_Check_success:
                f_key = open("config/key.xml", 'w')
                f_key.write(self.ui.api_key_QLineEdit.text() + "/True")
                self.api_key = self.ui.api_key_QLineEdit.text()
                f_key.close()

            else:
                f_key = open("config/key.xml", 'w')
                f_key.write(self.ui.api_key_QLineEdit.text() + "/False")
                self.api_key = self.ui.api_key_QLineEdit.text()
                f_key.close()

        except requests.exceptions.ConnectionError:
            self.internet_connect_success = False
            self.ui.api_key_QLineEdit.setText(self.api_key)
            self.ui.location.setText("网络错误")
            if self.theme_color == 'light':
                self.ui.check_api_key_icon.setPixmap(QPixmap('icon/questionblack.png'))
            elif self.theme_color == 'dark':
                self.ui.check_api_key_icon.setPixmap(QPixmap('icon/question.png'))
            self.ui.check_api_key_icon.setToolTip("网络错误，无法进行认证")

    #  初始化配置
    def init_base(self):

        ##################################################################
        # 读key，并验证

        try:
            read_key = open("config/key.xml", 'r')

            read_key_text = read_key.read()

            if len(read_key_text) != 0:

                self.api_key = read_key_text.split("/")[0]

                if read_key_text.split("/")[1] == str(True):
                    self.check_key()  # 检查key

            read_key.close()

        except FileNotFoundError:
            read_key = open("config/key.xml", 'w')
            read_key.close()

        ##################################################################
        # 读天气指数

        try:
            read_life_weather_fire_1 = open("config/life-weather.xml", 'r')

            lenth = len(read_life_weather_fire_1.read().split("/")) - 1

            read_life_weather_fire_1.close()

            read_life_weather_fire_2 = open("config/life-weather.xml", 'r')

            life_weather = []

            for i in read_life_weather_fire_2:
                for x in range(0, lenth):
                    life_weather.append(i.split("/")[x].split(":")[1])

            read_life_weather_fire_2.close()

            try:
                for i in range(16):

                    if life_weather[i] == str(True):
                        self.ui.life_weather_checkBox_[i].setCheckState(Qt.Checked)
                    else:
                        self.ui.life_weather_checkBox_[i].setCheckState(Qt.Unchecked)

                    if self.ui.life_weather_checkBox_[i].isChecked():
                        self.life_weather_checkBox_list_isCheck.append(str(i + 1) + ",")

            except IndexError:
                pass

        except FileNotFoundError:
            read_life_weather_fire = open("config/life-weather.xml", 'w')
            read_life_weather_fire.close()

        ##################################################################
        # 读收藏夹

        try:
            read_favorites_city = open("config/favorites_city.xml", 'r')

            self.favorites_city_list = read_favorites_city.read().split("/")

            self.favorites_city_list.remove('')

            StringListModel_city_list = QStringListModel()
            StringListModel_city_list.setStringList(self.favorites_city_list)
            self.ui.favorites_listView.setModel(StringListModel_city_list)

            read_favorites_city.close()

        except FileNotFoundError:
            read_favorites_city = open("config/favorites_city.xml", 'w')
            read_favorites_city.close()

        ##################################################################
        # 读是否有数据库

        try:
            conn = pymysql.connect(host='localhost', user="root", passwd="123456")
            conn.close()
            self.ui.select_way_ComboBox.addItems(['数据库查询'])
        except pymysql.err.OperationalError:
            self.ui.location.setText("数据库连接错误")

        ##################################################################################################
        ##################################################################################################
        ##################################################################################################

    # 初始化
    def init(self):

        # 获取地震信息
        self.start_thread_9()
        ##################################################################################################
        ##################################################################################################
        ##################################################################################################

    # 初始化UI
    def init_ui(self):
        system_name = platform.platform().split('-')[0] + platform.platform().split('-')[1]

        self.ui.check_system_QLabel.setText("当前操作系统:" + system_name)

        ##################################################################
        # 读系统主题
        system_list = ['Windows10', 'Windows11']

        try:
            read_theme = open("config/system theme.xml", 'r')

            read_theme_text = read_theme.read()

            read_theme.close()

            if len(read_theme_text) != 0:

                if read_theme_text.split("/")[1] == str(True):
                    self.allow_follow_success_theme = True
                    self.theme_color = systemtheme.is_dark_mode()
                    self.ui.select_color_dark.setEnabled(0)
                    self.ui.select_color_light.setEnabled(0)
                else:
                    self.allow_follow_success_theme = False
                    self.theme_color = read_theme_text.split("/")[0]
                    self.ui.select_color_dark.setEnabled(1)
                    self.ui.select_color_light.setEnabled(1)

                self.select_ui_style()

            else:
                self.ui.select_color_system_button.setStyleSheet(
                    u"QPushButton{border:none;image: url(icon/buttonunselect.png);}")
                self.ui_style_light()

        except FileNotFoundError:
            read_theme = open("config/system theme.xml", 'w')
            read_theme.close()
            self.ui.select_color_system_button.setStyleSheet(
                u"QPushButton{border:none;image: url(icon/buttonunselect.png);}")
            self.ui_style_light()

        if system_list.count(system_name) != 0:
            self.ui.select_color_system_button.setEnabled(1)

        else:
            self.ui.select_color_system_button.setEnabled(0)
            self.ui.select_color_system_button.setToolTip("当前操作系统，此功能不可用")

    ##################################################################################################
    ##################################################################################################
    ##################################################################################################

    # 监听函数，持续扫描
    def thread_control(self):

        # 刷新天气
        if not self.Timer_now_weather.isActive():
            if self.get_weather_success:
                self.Timer_now_weather.start(1800000)

        elif not self.get_weather_success:
            if self.Timer_now_weather.isActive():
                self.Timer_now_weather.stop()

        # 断线自动重连
        if not self.internet_connect_success:
            if not self.Timer_internet.isActive():
                self.Timer_internet.start(2000)

        elif self.internet_connect_success:
            if self.Timer_internet.isActive():
                self.Timer_internet.stop()

        # 跑马动画效果
        if self.allow_location_start:
            if not self.Timer_paint_location.isActive():
                self.Timer_paint_location.start(10)

        elif not self.allow_location_start:
            if self.Timer_paint_location.isActive():
                self.Timer_paint_location.stop()
                self.location_x = 0

        if self.allow_location_ip_start:
            if not self.Timer_paint_location_ip.isActive():
                self.Timer_paint_location_ip.start(10)

        elif not self.allow_location_ip_start:
            if self.Timer_paint_location_ip.isActive():
                self.Timer_paint_location_ip.stop()
                self.location_ip_x = 0
        # 系统主题判断
        if self.allow_follow_success_theme:
            self.theme_color = systemtheme.is_dark_mode()

            if self.theme_color == 'light' and self.theme_color_light_lock:
                self.ui_style_light()

            elif self.theme_color == 'dark' and self.theme_color_dark_lock:
                self.ui_style_dark()

    ##################################################################################################
    ##################################################################################################
    ##################################################################################################

    def TimeUpdate(self):  # 刷新时间

        self.ui.lcdNumber.display(QDateTime.currentDateTime().toString('yyyy-MM-dd hh:mm:ss'))

    def thread_init(self):  # 初始化

        self.ui.movie_earthquake.show()
        self.loading_earthquake.start()

        thread_time = Thread(target=self.init,  # 多线程加载,网络请求有时比较慢，其他控件会卡住
                             args=())
        thread_time.start()

    def start_thread(self):

        thread_time = Thread(target=self.TimeUpdate,  # 多线程加载,网络请求有时比较慢，其他控件会卡住
                             args=())
        thread_time.start()

    def start_thread_1(self):  # 请求实时天气

        if self.internet_connect_success:
            thread = Thread(target=self.get_now_weather,  # 多线程加载,网络请求有时比较慢，其他控件会卡住
                            args=())
            thread.start()

    def start_thread_2(self):  # 请求未来3天天气

        self.ui.movie_day_weather.show()
        self.loading_day_weather.start()

        if self.internet_connect_success:
            thread2 = Thread(target=self.get_3_day_weather,  # 多线程加载,网络请求有时比较慢，其他控件会卡住
                             args=())
            thread2.start()

    def start_thread_3(self):  # 请求实时预警信息

        if self.internet_connect_success:
            thread3 = Thread(target=self.get_now_weather_warning,  # 多线程加载,网络请求有时比较慢，其他控件会卡住
                             args=())
            thread3.start()

    def start_thread_4(self):

        if self.internet_connect_success:
            thread4 = Thread(target=self.get_now_weather_more,  # 多线程加载,网络请求有时比较慢，其他控件会卡住
                             args=())
            thread4.start()

    def start_thread_5(self):

        if self.internet_connect_success:
            thread5 = Thread(target=self.get_life_weather,  # 多线程加载,网络请求有时比较慢，其他控件会卡住
                             args=())
            thread5.start()

    def start_thread_6(self):

        self.ui.movie_day_weather.show()
        self.loading_day_weather.start()

        if self.api_key_Check_success:

            thread6 = Thread(target=self.get_location_ip,  # 多线程加载,网络请求有时比较慢，其他控件会卡住
                             args=())
            thread6.start()

        else:
            self.ui.location.setText("认证失败")

    def start_thread_7(self):

        self.loading_day_weather.start()

        if self.api_key_Check_success:

            thread7 = Thread(target=self.get_location,  # 多线程加载,网络请求有时比较慢，其他控件会卡住
                             args=())
            thread7.start()

            self.start_thread_1()
            self.start_thread_2()
            self.start_thread_3()
            self.start_thread_4()
            self.start_thread_5()

        else:
            self.ui.location.setText("认证失败")

    def start_thread_8(self):

        thread8 = Thread(target=self.check_internet,  # 多线程加载,网络请求有时比较慢，其他控件会卡住
                         args=())
        thread8.start()

    def start_thread_9(self):

        self.ui.movie_earthquake.show()
        self.loading_earthquake.start()

        thread9 = Thread(target=self.get_earthquake,  # 多线程加载,网络请求有时比较慢，其他控件会卡住
                         args=())
        thread9.start()

        ##################################################################################################
        ##################################################################################################
        ##################################################################################################

    #  显示并读取设置
    def show_setting(self):

        self.life_weather_checkBox_list_isCheck_old.clear()

        if self.ui.dialog.isHidden():
            self.ui.dialog.show()

            self.ui.favorites_listView.hide()
            self.ui.search.setPlaceholderText("市/县/区")

        for i in range(16):
            self.life_weather_checkBox_list_isCheck_old.append(self.ui.life_weather_checkBox_[i].isChecked())

    def update_ui(self):

        for i in range(16):
            self.ui.life_weather_checkBox_[i].update()

        self.ui.life_weather_all_checkBox.update()

    #  设置（程序运行中）
    ###############################################################
    #  在打开设置界面时读取设置情况，并在界面关闭（未保存）时，重新将所有设置情况赋予设置界面上的控件
    ###############################################################
    def read_old_setting(self):

        for i in range(16):

            if self.life_weather_checkBox_list_isCheck_old[i]:
                self.ui.life_weather_checkBox_[i].setCheckState(Qt.Checked)
            else:
                self.ui.life_weather_checkBox_[i].setCheckState(Qt.Unchecked)

        if self.theme_color == 'light':
            self.ui.search.setStyleSheet(
                u"QLineEdit{font-size:16px;border-top:0px  solid;border-bottom:1px  solid;"
                "border-left:0px  solid;border-right: 0px  solid;border-bottom-color:black;"
                "background-color:transparent;color:black;}")

        elif self.theme_color == 'dark':
            self.ui.search.setStyleSheet(
                u"QLineEdit{font-size:16px;border-top:0px  solid;border-bottom:1px  solid;"
                "border-left:0px  solid;border-right: 0px  solid;border-bottom-color:white;"
                "background-color:transparent;color:white;}")

    #  更改查询方式(并保存)
    def change_setting(self):

        self.life_weather_checkBox_list_isCheck.clear()

        if self.ui.select_way_ComboBox.currentText() == '在线查询':
            self.get_city_id_way = 1
        elif self.ui.select_way_ComboBox.currentText() == '本地查询':
            self.get_city_id_way = 2
        elif self.ui.select_way_ComboBox.currentText() == '数据库查询':
            self.get_city_id_way = 3

        self.life_weather_checkBox_list_isCheck_save.clear()

        for i in range(16):

            self.life_weather_checkBox_list_isCheck_save.append(str(self.ui.life_weather_checkBox_[i].isChecked()))

            #  添加网址查询条件  网址:type=1,2,3,4,5.....
            if self.ui.life_weather_checkBox_[i].isChecked():
                self.life_weather_checkBox_list_isCheck.append(str(i + 1) + ",")

        #  天气指数选项保存至外部存储
        f = open("config/life-weather.xml", 'w')

        for i in range(len(self.life_weather_checkBox_list_isCheck_save)):
            f.write(str(i + 1) + ":" + self.life_weather_checkBox_list_isCheck_save[i] + "/")

        f.close()

        #  当Key值错误时
        if self.api_key_Check_success is False:
            self.api_key = self.ui.api_key_QLineEdit.text()

            self.check_key()

        f_theme = open("config/system theme.xml", 'w')

        f_theme.write(self.theme_color + '/' + str(self.allow_follow_success_theme))

        f_theme.close()

        if not self.ui.dialog.isHidden():
            self.ui.dialog.hide()

        if self.theme_color == 'light':
            self.ui.search.setStyleSheet(
                u"QLineEdit{font-size:16px;border-top:0px  solid;border-bottom:1px  solid;"
                "border-left:0px  solid;border-right: 0px  solid;border-bottom-color:black;"
                "background-color:transparent;color:black;}")

        elif self.theme_color == 'dark':
            self.ui.search.setStyleSheet(
                u"QLineEdit{font-size:16px;border-top:0px  solid;border-bottom:1px  solid;"
                "border-left:0px  solid;border-right: 0px  solid;border-bottom-color:white;"
                "background-color:transparent;color:white;}")

    #  天气指数全选
    def life_weather_all_check(self):

        self.all_check_lock = False

        for i in range(16):
            if self.ui.life_weather_all_checkBox.isChecked():
                self.ui.life_weather_checkBox_[i].setCheckState(Qt.Checked)
            else:
                self.ui.life_weather_checkBox_[i].setCheckState(Qt.Unchecked)

        self.all_check_lock = True

    def life_weather_all_check_2(self):

        if self.all_check_lock:

            self.life_weather_checkBox_list_isCheck_old_str.clear()

            for i in range(16):
                self.life_weather_checkBox_list_isCheck_old_str. \
                    append(str(self.ui.life_weather_checkBox_[i].isChecked()))

            if self.life_weather_checkBox_list_isCheck_old_str.count('True') == 16:
                self.ui.life_weather_all_checkBox.setCheckState(Qt.Checked)
            else:
                self.ui.life_weather_all_checkBox.setCheckState(Qt.Unchecked)

            self.ui.life_weather_all_checkBox.update()
        else:
            pass

    ##################################################################################################
    ##################################################################################################
    ##################################################################################################

    # 请求位置信息
    def get_location(self):

        if len(self.ui.search.text()) > 0:

            if len(self.ui.search.text().split("-")) == 1:  # 防止区域重名，添加区域省份

                self.cityname.clear()

                if self.get_city_id_way == 1:

                    try:

                        text = requests.get('https://geoapi.qweather.com/v2/city/lookup?location=' +
                                            self.ui.search.text() + '&key=' + self.api_key)
                        text.encoding = 'utf-8'

                        self.internet_connect_success = True  # 请求不报错，连接即正常

                        if text.json()['code'] == str(200):

                            for i in range(len(text.json()['location'])):
                                if len(text.json()['location'][i]['name']) > 1:
                                    self.cityname.append(
                                        text.json()['location'][i]['name'] + "-" + text.json()['location'][i]['adm1'])

                            self.cityid = text.json()['location'][0]['id']

                            self.province = text.json()['location'][0]['adm1']

                            self.city = text.json()['location'][0]['adm2']

                            # 收藏夹用
                            self.favorites_city_text = text.json()['location'][0]['adm2']
                            self.favorites_province_text = text.json()['location'][0]['adm1']

                            if self.favorites_city_list.count(self.favorites_city_text + '-' +
                                                              self.favorites_province_text) == 0:
                                self.favorites_city_success = False  # 未收藏

                            else:
                                self.favorites_city_success = True  # 已收藏

                        elif text.json()['code'] == str(404) or text.json()['code'] == str(400):

                            self.cityid = None
                            self.province = None
                            self.city = None

                        elif text.json()['code'] == str(500):

                            self.ui.location.setText("无响应或超时")

                        elif text.json()['code'] == str(429):

                            self.ui.location.setText("请求过快")

                    except requests.exceptions.ConnectionError:
                        self.internet_connect_success = False  # 请求报错，连接即不正常
                        self.ui.location.setText("网络错误")

                elif self.get_city_id_way == 2:

                    self.internet_connect_success = True  # 本地数据，无需请求

                    cityidlist = []
                    provincelist = []
                    citylist = []

                    file = 'LocationList-master/city.xlsx'
                    f = open(file, 'rb')
                    df = pd.read_excel(f, sheet_name='Sheet1', names=None, usecols=['Location_ID',
                                                                                    'Adm1_Name_ZH', 'Location_Name_ZH'])

                    df_li = df.values.tolist()

                    for s_li in df_li:
                        self.cityname.append(s_li[1] + "-" + s_li[2])

                        cityidlist.append(s_li[0])
                        provincelist.append(s_li[2])
                        citylist.append(s_li[1])

                    f.close()

                    for i in range(len(citylist)):
                        if self.ui.search.text().find(citylist[i]) != -1 or self.ui.search.text(). \
                                find(str(cityidlist[i])) != -1:
                            self.cityid = str(cityidlist[i])

                            self.province = str(provincelist[i])

                            self.city = str(citylist[i])

                elif self.get_city_id_way == 3:

                    self.internet_connect_success = True  # 本地数据，无需请求

                    cityidlist = []
                    provincelist = []
                    citylist = []

                    conn = pymysql.connect(host='localhost', user="root", passwd="123456")
                    cur = conn.cursor()

                    try:
                        conn.select_db('weather')

                        # sql = "select * from city;" % (today, tomorrow)
                        sql = "select Location_ID,Adm1_Name_ZH,Location_Name_ZH from city where Location_Name_ZH like" \
                              "'%s' or  Adm1_Name_ZH like '%s';" % ('%' + self.ui.search.text() + '%', '%' +
                                                                    self.ui.search.text() + '%')
                        cur.execute(sql)

                        for i in cur.fetchall():
                            self.cityname.append(i[2] + '-' + i[1])

                            cityidlist.append(i[0])
                            provincelist.append(i[1])
                            citylist.append(i[2])

                        cur.close()
                        conn.close()

                    except pymysql.err.OperationalError:
                        self.ui.location.setText("数据表连接错误")

                    for i in range(len(citylist)):
                        if self.ui.search.text().find(citylist[i]) != -1 or self.ui.search.text(). \
                                find(str(cityidlist[i])) != -1:
                            self.cityid = str(cityidlist[i])

                            self.province = str(provincelist[i])

                            self.city = str(citylist[i])

                #######################################################################################################
                #######################################################################################################

            elif len(self.ui.search.text().split("-")) > 1 and \
                    ((self.ui.search.text().split("-")[1].find('省') != -1) or (
                            self.ui.search.text().split("-")[1].find('市') != -1) or (
                             self.ui.search.text().split("-")[1].find('区') != -1)):
                try:

                    text_2 = requests.get('https://geoapi.qweather.com/v2/city/lookup?location=' +
                                          self.ui.search.text().split("-")[0] + '&adm=' + self.ui.search.text().
                                          split("-")[1] + '&key=' + self.api_key)

                    self.internet_connect_success = True  # 请求不报错，连接即正常

                    if text_2.json()['code'] == str(200):

                        self.cityid = text_2.json()['location'][0]['id']

                        self.province = text_2.json()['location'][0]['adm1']

                        self.city = text_2.json()['location'][0]['adm2']

                        # 收藏夹用
                        self.favorites_city_text = text_2.json()['location'][0]['adm2']
                        self.favorites_province_text = text_2.json()['location'][0]['adm1']

                    elif text_2.json()['code'] == str(500):

                        self.ui.location.setText("无响应或超时")

                    elif text_2.json()['code'] == str(429):

                        self.ui.location.setText("请求过快")

                    else:
                        pass

                except requests.exceptions.ConnectionError:

                    self.internet_connect_success = False  # 请求报错，连接即不正常
                    self.ui.location.setText("网络错误")

        else:
            try:
                requests.get("https://baidu.com")
                self.internet_connect_success = True  # 请求不报错，连接即正常

            except requests.exceptions.ConnectionError:

                self.internet_connect_success = False  # 请求报错，连接即不正常
                self.ui.location.setText("网络错误")

            self.cityid = None
            self.province = None
            self.city = None

    #  搜索框自动填充下拉栏
    def search_completer(self):

        search_datetime_new = datetime.datetime.now()

        if (search_datetime_new - self.search_datetime) > datetime.timedelta(seconds=1) and \
                len(self.ui.search.text()) > 0:

            self.get_location()

            self.lock_search = False

            self.completer_city = QCompleter(self.cityname)

            self.completer_city.setCompletionMode(QCompleter.PopupCompletion)  # 弹出窗口，但选项会进行过滤
            # self.completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion) # 弹出窗口，显示全部

            self.completer_city.setFilterMode(Qt.MatchContains)  # 内容匹配，内容包含即可
            # self.completer.setFilterMode(Qt.MatchExactly) # 默认，完全匹配

            if self.theme_color == 'light':
                self.completer_city.popup().setStyleSheet(
                    "QAbstractItemView{font-size:15px;color:black;"
                    "background-color:rgba(140, 215, 215,60%);}"
                    "QScrollBar:vertical{background-color:rgba(140, 215, 215,60%);}"
                    "QScrollBar::add-line:vertical{background-color:rgba(0,0,0,0%);}"
                    "QScrollBar::sub-line:vertical{background-color:rgba(0,0,0,0%);}"
                    "QScrollBar::handle:vertical{width:8px;background:rgba(0,0,0,25%); border-radius:4px;}")

            elif self.theme_color == 'dark':
                self.completer_city.popup().setStyleSheet(
                    "QAbstractItemView{font-size:15px;color:white;"
                    "background-color:rgba(60, 63, 65,60%);}"
                    "QScrollBar:vertical{background-color:rgba(60, 63, 65,60%);}"
                    "QScrollBar::add-line:vertical{background-color:rgba(0,0,0,0%);}"
                    "QScrollBar::sub-line:vertical{background-color:rgba(0,0,0,0%);}"
                    "QScrollBar::handle:vertical{width:8px;background:rgba(0,0,0,25%); border-radius:4px;}")

            self.completer_city.setMaxVisibleItems(5)

            self.ui.search.setCompleter(self.completer_city)

        self.search_datetime = datetime.datetime.now()

    #  通过IP获取地址
    def get_location_ip(self):

        province, city, area, address = ip.get_location()

        if province is not None:
            self.province = province
        else:
            self.province = None

        if area is not None:
            self.city = area
        elif city is not None:
            self.city = city
        else:
            self.city = None

        self.location_ip_text = address + "(当前网络位置)"

        #  文字过长，显示跑马字幕
        if self.ui.location_ip.fontMetrics().size(Qt.TextSingleLine, self.location_ip_text).width() > \
                self.ui.location_ip.width():

            self.allow_location_ip_start = True

            self.ui.location_ip.setText("")
            self.ui.location_ip.update()

            # location_ip = self.ui.location_ip.fontMetrics().elidedText(address + "(当前网络位置)", Qt.ElideRight,
            #                                                            self.ui.location_ip.width())
        else:
            self.allow_location_ip_start = False

            self.ui.location_ip.setText(self.location_ip_text)

        if (self.province is not None) and (self.city is not None):
            try:
                text_2 = requests.get('https://geoapi.qweather.com/v2/city/lookup?location=' +
                                      self.city + '&adm=' + self.province + '&key=' + self.api_key)

                if text_2.json()['code'] == str(200):
                    self.cityid = text_2.json()['location'][0]['id']
                    self.map_lat = text_2.json()['location'][0]['lat']
                    self.map_lon = text_2.json()['location'][0]['lon']

                    # 收藏夹用
                    self.favorites_city_text = text_2.json()['location'][0]['adm2']
                    self.favorites_province_text = text_2.json()['location'][0]['adm1']

                    self.internet_connect_success = True

                    self.start_thread_1()
                    self.start_thread_2()
                    self.start_thread_3()
                    self.start_thread_4()
                    self.start_thread_5()

                    if self.favorites_city_list.count(self.favorites_city_text + '-' +
                                                      self.favorites_province_text) == 0:

                        self.favorites_city_success = False  # 未收藏

                    else:
                        self.favorites_city_success = True  # 已收藏

                elif text_2.json()['code'] == str(500):

                    self.ui.location.setText("无响应或超时")

                elif text_2.json()['code'] == str(429):

                    self.ui.location.setText("请求过快")

                else:
                    pass

            except requests.exceptions.ConnectionError:

                self.internet_connect_success = False
                self.ui.location_ip.setText("网络错误")

        else:

            if address != "网络错误":
                address = "网络位置不准确,无法获取本地天气"
            else:
                self.internet_connect_success = False

            self.ui.location_ip.setText(address)

    ##################################################################################################
    ##################################################################################################
    ##################################################################################################

    # 收藏夹

    def favorites_city(self):

        if self.favorites_city_success and self.get_weather_success:

            if self.theme_color == 'light':

                self.ui.search_favorites.setStyleSheet(u"QPushButton{border:none;image:url"
                                                       u"(icon/favoritesselectblack.png);}")

            elif self.theme_color == 'dark':

                self.ui.search_favorites.setStyleSheet(u"QPushButton{border:none;image:url"
                                                       u"(icon/favoritesselectwhite.png);}")
            self.ui.search_favorites.setToolTip("已收藏")

        elif not self.favorites_city_success and self.get_weather_success:

            if self.theme_color == 'light':

                self.ui.search_favorites.setStyleSheet(u"QPushButton{border:none;image:url"
                                                       u"(icon/favoritesunselectblack.png);}")
            elif self.theme_color == 'dark':
                self.ui.search_favorites.setStyleSheet(u"QPushButton{border:none;image:url"
                                                       u"(icon/favoritesunselectwhite.png);}")

            self.ui.search_favorites.setToolTip("未收藏")

    def favorites_city_clicked(self):

        if self.favorites_city_success and self.get_weather_success:

            if self.favorites_city_list.count(self.favorites_city_text + '-' + self.favorites_province_text) != 0:
                self.favorites_city_list.remove(self.favorites_city_text + '-' + self.favorites_province_text)

                if self.theme_color == 'light':

                    self.ui.search_favorites.setStyleSheet(u"QPushButton{border:none;image:url"
                                                           u"(icon/favoritesunselectblack.png);}")
                elif self.theme_color == 'dark':
                    self.ui.search_favorites.setStyleSheet(u"QPushButton{border:none;image:url"
                                                           u"(icon/favoritesunselectwhite.png);}")
                self.ui.search_favorites.setToolTip("未收藏")

                self.favorites_city_success = False

        elif not self.favorites_city_success and self.get_weather_success:

            if self.favorites_city_list.count(self.favorites_city_text + '-' + self.favorites_province_text) == 0:
                self.favorites_city_list.append(self.favorites_city_text + '-' + self.favorites_province_text)

                if self.theme_color == 'light':

                    self.ui.search_favorites.setStyleSheet(u"QPushButton{border:none;image:url"
                                                           u"(icon/favoritesselectblack.png);}")

                elif self.theme_color == 'dark':

                    self.ui.search_favorites.setStyleSheet(u"QPushButton{border:none;image:url"
                                                           u"(icon/favoritesselectwhite.png);}")

                self.ui.search_favorites.setToolTip("已收藏")

                self.favorites_city_success = True

        f_favorites_city = open("config/favorites_city.xml", 'w')

        for i in range(len(self.favorites_city_list)):
            f_favorites_city.write(self.favorites_city_list[i] + "/")

        f_favorites_city.close()

        StringListModel_city_list = QStringListModel()
        StringListModel_city_list.setStringList(self.favorites_city_list)
        self.ui.favorites_listView.setModel(StringListModel_city_list)

    def show_favorites_listView(self):

        if self.ui.favorites_listView.isHidden():

            self.ui.favorites_listView.show()

        else:
            self.ui.favorites_listView.hide()

    def select_favorites_city(self, qModelIndex):

        self.ui.favorites_listView.raise_()

        self.ui.favorites_listView.show()

        city = str(self.favorites_city_list[qModelIndex.row()]).split("-")[0]
        province = str(self.favorites_city_list[qModelIndex.row()]).split("-")[1]

        try:

            text = requests.get('https://geoapi.qweather.com/v2/city/lookup?location=' +
                                city + '&adm=' + province + '&key=' + self.api_key)

            self.internet_connect_success = True  # 请求不报错，连接即正常

            if text.json()['code'] == str(200):

                self.cityid = text.json()['location'][0]['id']

                self.province = text.json()['location'][0]['adm1']

                self.city = text.json()['location'][0]['adm2']

                self.start_thread_1()
                self.start_thread_2()
                self.start_thread_3()
                self.start_thread_4()
                self.start_thread_5()

                self.favorites_city_success = True  # 从收藏夹点击进入，即已经为收藏状态

                # 收藏夹用
                self.favorites_city_text = text.json()['location'][0]['adm2']
                self.favorites_province_text = text.json()['location'][0]['adm1']

                self.favorites_city()

            elif text.json()['code'] == str(500):

                self.ui.location.setText("无响应或超时")

            elif text.json()['code'] == str(429):

                self.ui.location.setText("请求过快")

            else:
                pass

            self.ui.favorites_listView.hide()

        except requests.exceptions.ConnectionError:

            self.internet_connect_success = False  # 请求报错，连接即不正常
            self.ui.location.setText("网络错误")

    def listWidgetContext(self, pos):
        menu = QMenu()
        if self.theme_color == 'dark':
            menu.setStyleSheet('background-color:rgb(60, 63, 65);color:white;')
        elif self.theme_color == 'light':
            menu.setStyleSheet('background-color:rgb(170, 255, 255);color:black;')
        # opt1 = menu.addAction("新增")
        option = menu.addAction("删除")
        # opt3 = menu.addAction("排序")
        # opt4 = menu.addAction("清空")
        action = menu.exec_(self.ui.favorites_listView.mapToGlobal(pos))
        if action == option:
            hitIndex = self.ui.favorites_listView.currentIndex().row()
            self.favorites_city_list.remove(self.favorites_city_list[hitIndex])

            f_favorites_city = open("config/favorites_city.xml", 'w')

            for i in range(len(self.favorites_city_list)):
                f_favorites_city.write(self.favorites_city_list[i] + "/")

            f_favorites_city.close()

            StringListModel_city_list = QStringListModel()
            StringListModel_city_list.setStringList(self.favorites_city_list)
            self.ui.favorites_listView.setModel(StringListModel_city_list)

            if self.theme_color == 'light':

                self.ui.search_favorites.setStyleSheet(u"QPushButton{border:none;image:url"
                                                       u"(icon/favoritesunselectblack.png);}")
            elif self.theme_color == 'dark':
                self.ui.search_favorites.setStyleSheet(u"QPushButton{border:none;image:url"
                                                       u"(icon/favoritesunselectwhite.png);}")
            self.ui.search_favorites.setToolTip("未收藏")

            self.favorites_city_success = False

    ##################################################################################################
    ##################################################################################################
    ##################################################################################################

    def get_now_weather(self):  # 获取当前天气

        cityid = self.cityid
        province = self.province
        city = self.city

        if (cityid is not None) and (province is not None) and self.internet_connect_success:
            text = requests.get('https://devapi.qweather.com/v7/weather/now?location=' + cityid +
                                '&key=' + self.api_key)  #
            text.encoding = 'utf-8'

            temp = text.json()['now']['temp']  # 当前气温
            icon = text.json()['now']['icon']  # 当前天气图标编号
            tip = text.json()['now']['text']  # 当前天气状态（文字）
            updatetime = str(text.json()['updateTime'])

            #  文字过长，显示省略号
            if len(re.findall("省", province)) == 0 and len(re.findall("市", province)) == 0 and \
                    len(re.findall("区", province)) == 0:
                self.location_text = province + "省 " + city

            else:
                self.location_text = province + " " + city

            if self.ui.location.fontMetrics().size(Qt.TextSingleLine, self.location_text).width() > \
                    self.ui.location.width():
                self.allow_location_start = True
                self.ui.location.setText("")
                self.ui.location.update()

            else:
                self.allow_location_start = False
                self.ui.location.setText(self.location_text)

                # self.location_text = self.ui.location.fontMetrics().elidedText(province + "省 " + city, Qt.ElideRight,
                #                                                                self.ui.location.width())
                # self.ui.location.setText(self.location_text)

            self.ui.now_weather_icon.setPixmap(QPixmap('icon/256/' + icon + '.png'))
            self.ui.now_weather_icon.setScaledContents(True)

            self.ui.now_weather_tip.setText(tip)

            self.ui.now_weather_temperature.setText(temp + "°C")

            self.ui.updatetime.setText("更新时间:" + updatetime.split("T")[0] + " " +
                                       updatetime.split("T")[1].split("+")[0])

            self.ui.stackedWidget_weather.setCurrentIndex(0)

            self.ui.now_weather_detailed.show()  # 展示实时天气详情

            self.get_weather_success = True

            self.favorites_city()

        else:
            if not self.internet_connect_success:
                self.ui.location.setText("网络错误")
            elif self.api_key_Check_success:
                if len(self.ui.search.text()) != 0:
                    self.ui.location.setText("未能查询到该地点")

            self.ui.now_weather_icon.clear()
            self.ui.now_weather_tip.clear()
            self.ui.now_weather_temperature.clear()
            self.ui.now_weather_detailed.hide()  # 隐藏实时天气详情

            # 天气预警第一页
            self.ui.warn_sender_[0].setText("发布单位：无")
            self.ui.warn_pubTime_[0].setText("发布时间：无")
            self.ui.warn_title_[0].setText("警告内容：无")
            self.ui.warn_text_[0].setText("警告详情：无")

            self.ui.weather_warn_icon_[0].setText("无天气预警")
            self.ui.typhoon_web_button.hide()

            self.ui.scrollAreaWidgetContents_[0].setGeometry(QRect(0, 0, 415, 150))  # 消除滚动条

            # 底部
            self.ui.updatetime.setText("更新时间:" + " 无")

            self.ui.stackedWidget_weather.setCurrentIndex(1)

            self.get_weather_success = False

    def get_3_day_weather(self):  # 获取未来3天天气

        for i in range(3):
            # 日期
            self.ui.get_3_day_weather_label_day_[i].clear()

            # 天气（白天图标）
            self.ui.get_3_day_weather_label_day_icon_[i].clear()

            # 天气（夜间图标）
            self.ui.get_3_day_weather_label_night_icon_[i].clear()

            # 天气文字描述(白天)
            self.ui.get_3_day_weather_label_day_tip_[i].clear()

            # 天气文字描述(夜间)
            self.ui.get_3_day_weather_label_night_tip_[i].clear()

            # 温度
            self.ui.get_3_day_weather_label_day_temp_[i].clear()

            # 降水量
            self.ui.get_3_day_weather_label_day_precip_[i].clear()
            # 紫外线强度
            self.ui.get_3_day_weather_label_day_uvIndex_[i].clear()
            # 湿度
            self.ui.get_3_day_weather_label_day_humidity_[i].clear()

        cityid = self.cityid
        province = self.province

        if (cityid is not None) and (province is not None) and self.internet_connect_success:
            text = requests.get('https://devapi.qweather.com/v7/weather/3d?location=' + cityid +
                                '&key=' + self.api_key)  #
            text.encoding = 'utf-8'

            for i in range(len(text.json()['daily'])):
                # 日期
                self.ui.get_3_day_weather_label_day_[i].setText(text.json()['daily'][i]['fxDate'])

                # 天气（白天图标）
                self.ui.get_3_day_weather_label_day_icon_[i].setPixmap(QPixmap('icon/256/' +
                                                                               text.json()['daily'][i][
                                                                                   'iconDay'] + '.png'))

                # 天气（夜间图标）
                self.ui.get_3_day_weather_label_night_icon_[i].setPixmap(QPixmap('icon/256/' +
                                                                                 text.json()['daily'][i]['iconNight']
                                                                                 + '.png'))

                # 天气文字描述(白天)
                self.ui.get_3_day_weather_label_day_tip_[i].setText(text.json()['daily'][i]['textDay'])

                # 天气文字描述(夜间)
                self.ui.get_3_day_weather_label_night_tip_[i].setText(text.json()['daily'][i]['textNight'])

                # 温度
                self.ui.get_3_day_weather_label_day_temp_[i].setText(text.json()['daily'][i]['tempMin'] + "°C-" +
                                                                     text.json()['daily'][i]['tempMax'] + "°C")

                # 降水量
                self.ui.get_3_day_weather_label_day_precip_[i].setText("预计当日降水量：" +
                                                                       text.json()['daily'][i]['precip'] + "mm")
                # 紫外线强度
                self.ui.get_3_day_weather_label_day_uvIndex_[i].setText("预计当日紫外线强度：" +
                                                                        text.json()['daily'][i]['uvIndex'])
                # 湿度
                self.ui.get_3_day_weather_label_day_humidity_[i].setText("预计当日相对湿度：" +
                                                                         text.json()['daily'][i]['humidity'] + "%")

            self.loading_day_weather.stop()
            self.ui.movie_day_weather.hide()

    def get_now_weather_warning(self):  # 获取当前天气预警

        cityid = self.cityid
        province = self.province

        if (cityid is not None) and (province is not None) and self.internet_connect_success:

            text = requests.get('https://devapi.qweather.com/v7/warning/now?location=' + cityid +
                                '&key=' + self.api_key)  #
            text.encoding = 'utf-8'

            if len(text.json()['warning']) >= 1:

                self.page_tip_count = len(text.json()['warning'])
                self.ui.stackedWidget_tip.setCurrentIndex(0)

                if len(text.json()['warning']) > 1:

                    self.ui.change_page_tip_right.show()
                    self.ui.change_page_tip_left.hide()

                else:

                    self.ui.change_page_tip_right.hide()
                    self.ui.change_page_tip_left.hide()

                icon = []
                icon_2 = []
                icon_3 = []
                icon_4 = []
                icon_5 = []
                icon_list = [icon, icon_2, icon_3, icon_4, icon_5]

                have_icon = False
                have_icon_2 = False
                have_icon_3 = False
                have_icon_4 = False
                have_icon_5 = False
                have_icon_list = [have_icon, have_icon_2, have_icon_3, have_icon_4, have_icon_5]

                for i in range(len(text.json()['warning'])):

                    try:
                        if len(text.json()['warning'][i]['sender']) > 0:
                            self.ui.warn_sender_[i].setText("发布单位：" + text.json()['warning'][i]['sender'])

                        else:
                            self.ui.warn_sender_[i].setText("发布单位：暂无数据")

                    except KeyError:
                        self.ui.warn_sender_[i].setText("发布单位：暂无数据")

                    ###########################################################
                    try:
                        if len(text.json()['warning'][i]['pubTime']) > 0:
                            self.ui.warn_pubTime_[i].setText("发布时间：" +
                                                             str(text.json()['warning'][i]['pubTime']).split("T")[
                                                                 0] + " " +
                                                             str(text.json()['warning'][i]['pubTime']).split("T")[1].
                                                             split("+")[0])
                        else:
                            self.ui.warn_pubTime_[i].setText("发布时间：暂无数据")
                    except KeyError:
                        self.ui.warn_pubTime_[i].setText("发布时间：暂无数据")

                    ###########################################################
                    try:
                        if len(text.json()['warning'][i]['title']) > 0:
                            self.ui.warn_title_[i].setText("警告内容：" + text.json()['warning'][i]['title'])

                            # 设置标题高度
                            self.ui.warn_title_[i].setGeometry(QRect(5, 50, 390,
                                                                     int(25 *
                                                                         math.ceil(
                                                                             (len(text.json()['warning'][i][
                                                                                      'title']) / 20)))))
                        else:
                            self.ui.warn_title_[i].setText("警告内容：暂无数据")

                            self.ui.warn_title_[i].setGeometry(QRect(5, 50, 390, 25))

                    except KeyError:
                        self.ui.warn_title_[i].setText("警告内容：暂无数据")

                        self.ui.warn_title_[i].setGeometry(QRect(5, 50, 390, 25))

                    ###########################################################
                    try:
                        if len(text.json()['warning'][i]['text']):
                            self.ui.warn_text_[i].setText("警告详情：" + text.json()['warning'][i]['text'])

                            # 设置内容高度
                            self.ui.warn_text_[i].setGeometry(QRect(5, 50 +
                                                                    int(25 *
                                                                        math.ceil(
                                                                            (len(text.json()['warning'][i][
                                                                                     'title']) / 20))),
                                                                    400,
                                                                    int(25 *
                                                                        math.ceil(
                                                                            (len(text.json()['warning'][i][
                                                                                     'text']) / 20)))))

                        else:
                            self.ui.warn_text_[i].setText("警告详情：暂无数据")

                            self.ui.warn_text_[i].setGeometry(QRect(5, 75, 400, 25))

                    except KeyError:
                        self.ui.warn_text_[i].setText("警告详情：暂无数据")

                        self.ui.warn_text_[i].setGeometry(QRect(5, 75, 400, 25))

                    self.ui.weather_warn_icon_[i].clear()

                    have_typhoon = []

                    for x in os.listdir("icon/warning"):
                        icon_list[i].append(os.path.splitext(x)[0])

                    try:
                        if (len(text.json()['warning'][i]['typeName']) > 0) and \
                                (len(text.json()['warning'][i]['level']) > 0):

                            for y in icon_list[i]:
                                if y.find(text.json()['warning'][i]['typeName']
                                          + text.json()['warning'][i]['level']) != -1:

                                    self.ui.weather_warn_icon_[i].setPixmap(
                                        QPixmap('icon/warning/' + text.json()['warning'][i]['typeName']
                                                + text.json()['warning'][i]['level'] + '.png'))
                                    self.ui.weather_warn_icon_[i].setScaledContents(True)

                                    have_typhoon.append(text.json()['warning'][i]['typeName'])

                                    have_icon_list[i] = True

                                else:
                                    if not have_icon_list[i]:
                                        self.ui.weather_warn_icon_[i].setText("暂无图标")
                        else:
                            self.ui.weather_warn_icon_[i].setText("暂无数据")

                    except KeyError:
                        self.ui.weather_warn_icon_[i].setText("暂无数据")

                    if have_typhoon.count('台风') > 0:
                        self.ui.typhoon_web_button.show()
                    else:
                        self.ui.typhoon_web_button.hide()
                    # #############################################################################
                    # print(25 * math.ceil((len(text.json()['warning'][i]['title']) / 30)))
                    # math.ceil 向上取整

                    try:
                        if len(text.json()['warning'][i]['title']) > 0 and len(text.json()['warning'][i]['text']) > 0:
                            self.ui.scrollAreaWidgetContents_[i].setGeometry(QRect(0, 0, 415,
                                                                                   int(25 *
                                                                                       math.ceil(
                                                                                           (len(text.json()['warning']
                                                                                                [i]['title']) / 20))) +
                                                                                   int(25 *
                                                                                       math.ceil(
                                                                                           (len(text.json()
                                                                                                ['warning'][i]
                                                                                                ['text']) / 20))) + 50))
                        else:
                            self.ui.scrollAreaWidgetContents_[0].setGeometry(QRect(0, 0, 415, 150))

                    except KeyError:

                        self.ui.scrollAreaWidgetContents_[0].setGeometry(QRect(0, 0, 415, 150))

            elif len(text.json()['warning']) == 0:

                self.ui.change_page_tip_left.hide()
                self.ui.change_page_tip_right.hide()
                self.ui.stackedWidget_tip.setCurrentIndex(0)

                # 第一页
                self.ui.warn_sender_[0].setText("发布单位：无")
                self.ui.warn_pubTime_[0].setText("发布时间：无")
                self.ui.warn_title_[0].setText("警告内容：无")
                self.ui.warn_text_[0].setText("警告详情：无")

                self.ui.weather_warn_icon_[0].clear()
                self.ui.weather_warn_icon_[0].setText("无天气预警")
                self.ui.typhoon_web_button.hide()

                self.ui.scrollAreaWidgetContents_[0].setGeometry(QRect(0, 0, 415, 150))

    #  获取当前天气详情
    def get_now_weather_more(self):
        cityid = self.cityid

        if (cityid is not None) and self.internet_connect_success:
            text = requests.get('https://devapi.qweather.com/v7/air/now?location=' + cityid +
                                '&key=' + self.api_key)  #
            text.encoding = 'utf-8'

            ui_more_weather_air_tip = [self.ui.more_weather_air_tip_pm10, self.ui.more_weather_air_tip_pm25,
                                       self.ui.more_weather_air_tip_so2, self.ui.more_weather_air_tip_no2,
                                       self.ui.more_weather_air_tip_o3, self.ui.more_weather_air_tip_co]

            ui_more_weather_air_value = [self.ui.more_weather_air_value_pm10, self.ui.more_weather_air_value_pm25,
                                         self.ui.more_weather_air_value_so2, self.ui.more_weather_air_value_no2,
                                         self.ui.more_weather_air_value_o3, self.ui.more_weather_air_value_co]

            ui_more_weather_air_icon = [self.ui.more_weather_air_icon_pm10, self.ui.more_weather_air_icon_pm25,
                                        self.ui.more_weather_air_icon_so2, self.ui.more_weather_air_icon_no2,
                                        self.ui.more_weather_air_icon_o3, self.ui.more_weather_air_icon_co]

            if text.json()['code'] == str(200):

                more_weather_air_value = [round(float(text.json()['now']['pm10'])),
                                          round(float(text.json()['now']['pm2p5'])),
                                          round(float(text.json()['now']['so2'])),
                                          round(float(text.json()['now']['no2'])),
                                          round(float(text.json()['now']['o3'])),
                                          round(float(text.json()['now']['co']))]

                for i in range(6):
                    ui_more_weather_air_value[i].setText(str(more_weather_air_value[i]))

                    if 50 >= more_weather_air_value[i] >= 0:
                        ui_more_weather_air_icon[i].setStyleSheet(
                            u"QLabel{min-width: 12px; min-height: 12px;max-width:12px; "
                            u"max-height: 12px;border-radius: 6px;background:green;}")

                    elif 150 >= more_weather_air_value[i] > 50:
                        ui_more_weather_air_icon[i].setStyleSheet(
                            u"QLabel{min-width: 12px; min-height: 12px;max-width:12px; "
                            u"max-height: 12px;border-radius: 6px;background:yellow;}")

                    elif 300 >= more_weather_air_value[i] > 150:
                        ui_more_weather_air_icon[i].setStyleSheet(
                            u"QLabel{min-width: 12px; min-height: 12px;max-width:12px; "
                            u"max-height: 12px;border-radius: 6px;background:orange;}")

                    elif more_weather_air_value[i] > 300:
                        ui_more_weather_air_icon[i].setStyleSheet(
                            u"QLabel{min-width: 12px; min-height: 12px;max-width:12px; "
                            u"max-height: 12px;border-radius: 6px;background:red;}")

                    ui_more_weather_air_tip[i].show()
                    ui_more_weather_air_value[i].show()
                    ui_more_weather_air_icon[i].show()

                self.aqi_now = round(float(text.json()['now']['aqi']))

                if self.theme_color == 'light':

                    if 50 >= self.aqi_now >= 0:
                        self.ui.more_weather_air_tip_all.setStyleSheet(
                            u"QLabel{min-width: 80px; min-height: 80px;max-width:80px;"
                            u"max-height: 80px;border-radius: 40px;color:black;"
                            u"border:5px solid green;}")

                    elif 150 >= self.aqi_now > 50:
                        self.ui.more_weather_air_tip_all.setStyleSheet(
                            u"QLabel{min-width: 80px; min-height: 80px;max-width:80px;"
                            u"max-height: 80px;border-radius: 40px;color:black;"
                            u"border:5px solid yellow;}")

                    elif 300 >= self.aqi_now > 150:
                        self.ui.more_weather_air_tip_all.setStyleSheet(
                            u"QLabel{min-width: 80px; min-height: 80px;max-width:80px;"
                            u"max-height: 80px;border-radius: 40px;color:black;"
                            u"border:5px solid orange;}")

                    elif self.aqi_now > 300:
                        self.ui.more_weather_air_tip_all.setStyleSheet(
                            u"QLabel{min-width: 80px; min-height: 80px;max-width:80px;"
                            u"max-height: 80px;border-radius: 40px;color:black;"
                            u"border:5px solid red;}")

                elif self.theme_color == 'dark':

                    if 50 >= self.aqi_now >= 0:
                        self.ui.more_weather_air_tip_all.setStyleSheet(
                            u"QLabel{min-width: 80px; min-height: 80px;max-width:80px;"
                            u"max-height: 80px;border-radius: 40px;color:white;"
                            u"border:5px solid green;}")

                    elif 150 >= self.aqi_now > 50:
                        self.ui.more_weather_air_tip_all.setStyleSheet(
                            u"QLabel{min-width: 80px; min-height: 80px;max-width:80px;"
                            u"max-height: 80px;border-radius: 40px;color:white;"
                            u"border:5px solid yellow;}")

                    elif 300 >= self.aqi_now > 150:
                        self.ui.more_weather_air_tip_all.setStyleSheet(
                            u"QLabel{min-width: 80px; min-height: 80px;max-width:80px;"
                            u"max-height: 80px;border-radius: 40px;color:white;"
                            u"border:5px solid orange;}")

                    elif self.aqi_now > 300:
                        self.ui.more_weather_air_tip_all.setStyleSheet(
                            u"QLabel{min-width: 80px; min-height: 80px;max-width:80px;"
                            u"max-height: 80px;border-radius: 40px;color:white;"
                            u"border:5px solid red;}")

                self.ui.more_weather_air_tip_all.setText(
                    text.json()['now']['category'] + "\n" + text.json()['now']['aqi'])

            else:
                self.ui.more_weather_air_tip_all.setText("暂无数据")
                if self.theme_color == 'light':
                    self.ui.more_weather_air_tip_all.setStyleSheet(u"QLabel{color:black;}")
                elif self.theme_color == 'dark':
                    self.ui.more_weather_air_tip_all.setStyleSheet(u"QLabel{color:white;}")

                for i in range(6):
                    ui_more_weather_air_tip[i].hide()
                    ui_more_weather_air_value[i].hide()
                    ui_more_weather_air_icon[i].hide()

    #  获取生活指数
    def get_life_weather(self):

        cityid = self.cityid

        for i in range(16):
            self.ui.life_weather_label_title_[i].clear()
            self.ui.life_weather_label_level_[i].clear()
            self.ui.life_weather_label_text_[i].clear()

        if (cityid is not None) and self.internet_connect_success and len(self.life_weather_checkBox_list_isCheck) != 0:

            text = requests.get('https://devapi.qweather.com/v7/indices/1d?type=' +
                                str(''.join(self.life_weather_checkBox_list_isCheck)) + '&location=' + cityid +
                                '&key=' + self.api_key)  #
            text.encoding = 'utf-8'

            if text.json()['code'] == str(200):

                self.page_life_weather_count = len(text.json()['daily'])
                self.ui.stackedWidget_life_weather.setCurrentIndex(0)

                if self.page_life_weather_count > 2:
                    self.ui.change_page_life_weather_left.hide()
                    self.ui.change_page_life_weather_right.show()
                else:
                    self.ui.change_page_life_weather_left.hide()
                    self.ui.change_page_life_weather_right.hide()

                for i in range(len(text.json()['daily'])):
                    self.ui.life_weather_label_title_[i].setText(str(text.json()['daily'][i]['name']))
                    self.ui.life_weather_label_level_[i].setText(str(text.json()['daily'][i]['category']))
                    try:
                        self.ui.life_weather_label_text_[i].setText(str(text.json()['daily'][i]['text']))

                        self.ui.life_weather_label_text_[i]. \
                            setGeometry(QRect(0, 0, 400, int(20 *
                                                             math.ceil(
                                                                 (len(text.json()['daily'][i]
                                                                      ['text']) / 30)))))

                        self.ui.scrollAreaWidgetContents_life_weather_[i]. \
                            setGeometry(QRect(0, 0, 400, int(20 *
                                                             math.ceil(
                                                                 (len(text.json()[
                                                                          'daily'][i]['text']) / 30)))))
                    except KeyError:

                        self.ui.life_weather_label_text_[i].setText("无数据")

            else:

                self.ui.stackedWidget_life_weather.setCurrentIndex(0)
                self.ui.change_page_life_weather_right.hide()
                self.ui.change_page_life_weather_left.hide()

                for i in range(2):
                    self.ui.life_weather_label_title_[i].clear()
                    self.ui.life_weather_label_level_[i].clear()
                    self.ui.life_weather_label_text_[i].clear()

        else:

            self.ui.stackedWidget_life_weather.setCurrentIndex(0)
            self.ui.change_page_life_weather_right.hide()
            self.ui.change_page_life_weather_left.hide()

            for i in range(2):
                self.ui.life_weather_label_title_[i].clear()
                self.ui.life_weather_label_level_[i].clear()
                self.ui.life_weather_label_text_[i].clear()

    ######################################################################################

    ######################################################################################
    # 天气指数右翻页
    def change_page_life_weather_right(self):

        if self.ui.change_page_life_weather_left.isHidden():
            self.ui.change_page_life_weather_left.show()

        if self.ui.stackedWidget_life_weather.currentIndex() + 1 < (self.page_life_weather_count / 2):
            self.ui.stackedWidget_life_weather.setCurrentIndex(self.ui.stackedWidget_life_weather.currentIndex() + 1)

            if self.ui.change_page_life_weather_right.isHidden():
                self.ui.change_page_life_weather_right.show()

        if self.ui.stackedWidget_life_weather.currentIndex() + 1 == (round(float(self.page_life_weather_count / 2)
                                                                           + 0.01)):
            self.ui.change_page_life_weather_right.hide()

    # 天气指数左翻页
    def change_page_life_weather_left(self):

        self.ui.stackedWidget_life_weather.setCurrentIndex(self.ui.stackedWidget_life_weather.currentIndex() - 1)

        if self.ui.change_page_life_weather_right.isHidden():
            self.ui.change_page_life_weather_right.show()

        if self.ui.stackedWidget_life_weather.currentIndex() == 0:
            self.ui.change_page_life_weather_left.hide()

    # 天气预警右翻页
    def change_page_tip_right(self):

        if self.ui.change_page_tip_left.isHidden():
            self.ui.change_page_tip_left.show()

        if self.ui.stackedWidget_tip.currentIndex() + 1 < self.page_tip_count:

            self.ui.stackedWidget_tip.setCurrentIndex(self.ui.stackedWidget_tip.currentIndex() + 1)

            if self.ui.change_page_tip_right.isHidden():
                self.ui.change_page_tip_right.show()

        if self.ui.stackedWidget_tip.currentIndex() + 1 == self.page_tip_count:
            self.ui.change_page_tip_right.hide()

    # 天气预警左翻页
    def change_page_tip_left(self):

        self.ui.stackedWidget_tip.setCurrentIndex(self.ui.stackedWidget_tip.currentIndex() - 1)

        if self.ui.change_page_tip_right.isHidden():
            self.ui.change_page_tip_right.show()

        if self.ui.stackedWidget_tip.currentIndex() == 0:
            self.ui.change_page_tip_left.hide()

    ##################################################################################################

    ##################################################################################################

    def change_to_now_weather_detailed(self):  # 转至获取当前天气详情页

        if self.ui.stackedWidget_weather.currentIndex() == 0:
            self.ui.stackedWidget_weather.setCurrentIndex(2)
        elif self.ui.stackedWidget_weather.currentIndex() == 2:
            self.ui.stackedWidget_weather.setCurrentIndex(0)

    def change_now_weather_detailed_icon(self):

        if self.ui.stackedWidget_weather.currentIndex() == 0:
            if self.theme_color == 'dark':
                self.ui.now_weather_detailed.setStyleSheet(u"QPushButton{background-color:transparent;"
                                                           u"border:none;image:url(icon/more-down.png);}"
                                                           u"QPushButton:hover{image: url(icon/more-downgray.png);}")
            elif self.theme_color == 'light':
                self.ui.now_weather_detailed.setStyleSheet(u"QPushButton{background-color:transparent;"
                                                           u"border:none;image:url(icon/more-downblack.png);}"
                                                           u"QPushButton:hover{image: url(icon/more-downgray.png);}")
        elif self.ui.stackedWidget_weather.currentIndex() == 2:
            if self.theme_color == 'dark':
                self.ui.now_weather_detailed.setStyleSheet(u"QPushButton{background-color:transparent;"
                                                           u"border:none;image:url(icon/more-up.png);}"
                                                           u"QPushButton:hover{image: url(icon/more-upgray.png);}")
            elif self.theme_color == 'light':
                self.ui.now_weather_detailed.setStyleSheet(u"QPushButton{background-color:transparent;"
                                                           u"border:none;image:url(icon/more-upblack.png);}"
                                                           u"QPushButton:hover{image: url(icon/more-upgray.png);}")

    ##################################################################################################

    ##################################################################################################

    def get_earthquake(self, text=''):

        self.ui.earthquake_massage.clear()

        a = 0

        try:
            for i in earthquake.more_information():
                for x in i:
                    text += x

                    if len(x) < 50:
                        a += 3
                    elif 80 > len(x) >= 50:
                        a += 4
                    elif len(x) >= 80:
                        a += 5

            self.ui.earthquake_massage.setAlignment(Qt.AlignLeft)

            self.ui.earthquake_massage.setFont(QFont("微软雅黑", 9))

            self.ui.scrollAreaWidgetContents_earthquake_massage.setGeometry(QRect(0, 0, 415, a * 20))
            self.ui.earthquake_massage.setGeometry(QRect(0, 25, 320, a * 20))

            self.ui.earthquake_massage.setText(text)

            self.loading_earthquake.stop()
            self.ui.movie_earthquake.hide()

        except requests.exceptions.ConnectionError or requests.exceptions.JSONDecodeError:

            self.loading_earthquake.stop()
            self.ui.movie_earthquake.hide()

            self.ui.earthquake_massage.setAlignment(Qt.AlignCenter)

            self.ui.earthquake_massage.setFont(QFont("微软雅黑", 11))

            self.ui.earthquake_massage.setText("网络错误")

            self.ui.scrollAreaWidgetContents_earthquake_massage.setGeometry(QRect(0, 30, 415, 100))
            self.ui.earthquake_massage.setGeometry(QRect(0, 30, 320, 100))

    ##################################################################################################

    ##################################################################################################

    def open_typhoon_web(self):

        QDesktopServices.openUrl(QUrl("http://typhoon.nmc.cn/web.html"))

    def get_api_key_web(self):

        QDesktopServices.openUrl(QUrl("https://id.qweather.com/#/login?redirect=https%3A%2F%2Fconsole.qweather.com%2F"
                                      "#/console?lang=zh&lang=zh"))

    def get_earthquake_web(self):

        QDesktopServices.openUrl(QUrl("https://news.ceic.ac.cn/"))

    ##################################################################################################

    ##################################################################################################

    def show_map(self):

        if self.ui.qwebengine.isHidden() and (self.map_lat is not None) and (self.map_lon is not None):
            self.map()
            self.ui.qwebengine.show()
        else:
            self.ui.qwebengine.hide()

    # http://online1.map.bdimg.com/onlinelabel/?qt=tile&x={x}&y={y}&z={z}  http://api0.map.bdimg.com/customimage/tile?&x={x}&y={y}&z={z}

    def map(self):
        Map = folium.Map(location=[self.map_lat, self.map_lon],
                         zoom_start=12,
                         control_scale=True,
                         tiles='http://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7&x={x}&y={y}&z={z}',
                         attr='default')
        # Map = folium.Map(location=[24.488555, 118.089695],
        #                  zoom_start=12,
        #                  control_scale=True,
        #                  tiles='http://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7&x={x}&y={y}&z={z}',
        #                  attr='default')

        Map.add_child(folium.LatLngPopup())  # 显示鼠标点击点经纬度
        # Map.add_child(folium.ClickForMarker(popup ='Waypoint'))  # 将鼠标点击点添加到地图上

        folium.Marker(
            location=[self.map_lat, self.map_lon],
            popup=folium.Popup("位置仅供参考(最高区级定位)", max_width=180),  # (位置仅参考(区级定位))
            icon=folium.Icon(color='green',icon="home")
        ).add_to(Map)

        o_time, epi_lon, epi_lat, epi_depth, m, location_c, num = earthquake_map.get_earthquake()

        for x in range(num-1):
            folium.Marker(
                location=[epi_lat[x], epi_lon[x]],
                popup=folium.Popup("地震" + '</br>' + "发生时间："+str(o_time[x]) + '</br>'
                                   "经度："+str(epi_lon[x]) + '</br>' + "纬度："+str(epi_lat[x]) + '</br>'
                                   "深度：" + str(epi_depth[x]) + '</br>' + "位置：" + str(location_c[x]) + '</br>'
                                   "震级：" + str(m[x]),
                                   max_width=180),
                icon=folium.Icon(color="red", icon="flag"),
            ).add_to(Map)

        num_t, time_c, epi_lon_t, epi_lat_t, wind_speed, pressure, moving_direction, moving_speed = \
            typhoon_map.get_typhoon()

        if num_t > 0:

            for x in range(num_t):
                folium.Marker(
                    location=[epi_lat_t[x], epi_lon_t[x]],
                    popup=folium.Popup("台风" + '</br>' + "时间："+str(time_c[x]) + '</br>'
                                       "经度："+str(epi_lon_t[x]) + '</br>' + "纬度："+str(epi_lat_t[x]) + '</br>'
                                       "风速：" + str(wind_speed[x]) + '米/秒</br>' + "气压：" + str(pressure[x]) + '百帕</br>'
                                       "移动方向：" + str(moving_direction[x]) + '</br>' +
                                       "移动速度：" + str(moving_speed[x]) + "公里/小时",
                                       max_width=180),
                    icon=folium.Icon(color="blue", icon="flag"),
                ).add_to(Map)

        Map.save("save_map.html")

        # 在QWebEngineView中加载网址
        path = "file:\\" + os.getcwd() + "\\save_map.html"
        path = path.replace('\\', '/')
        self.ui.qwebengine.load(QUrl(path))

    ##################################################################################################

    ##################################################################################################

    def ui_style_dark(self):

        self.ui.title.setStyleSheet(u"QPushButton{background-color:transparent;border:none;color:white;}")
        self.ui.location.setStyleSheet(u"QLabel{color:white;}")
        self.ui.background.setStyleSheet(u"QLabel{background-color:rgba(60, 63, 65,60%);}")
        self.ui.background_dialog.setStyleSheet(u"QLabel{background-color:rgba(60, 63, 65,60%);}")
        self.ui.select_way_ComboBox.setStyleSheet(u"font-size:15px;color:white;border:none;"
                                                  "background-color:rgba(60, 63, 65,60%);")
        self.ui.favorites_listView.setStyleSheet(u"QListView{background-color:rgb(60, 63, 65);color:white;}"
                                                 u"QScrollBar:vertical{background-color:rgb(60, 63, 65);}")

        self.ui.search.setStyleSheet(u"QLineEdit{font-size:16px;border-top:0px  solid;border-bottom:1px  solid;"
                                     "border-left:0px  solid;border-right: 0px  solid;border-bottom-color:white;"
                                     "background-color:transparent;color:white;}")

        self.ui.now_weather_tip.setStyleSheet(u"QLabel{color:white;}")
        self.ui.now_weather_temperature.setStyleSheet(u"QLabel{color:white;}")

        self.ui.lcdNumber.setStyleSheet(u"QLCDNumber{color:white;}")

        # lcdpat = QPalette(self.ui.lcdNumber.palette())  # 失去焦点时不可用
        # lcdpat.setColor(QPalette.Normal, QPalette.WindowText, Qt.white)
        # self.ui.lcdNumber.setPalette(lcdpat)

        for i in range(3):
            self.ui.get_3_day_weather_label_day_[i].setStyleSheet(u"QLabel{color:white;}")
            self.ui.get_3_day_weather_label_day_tip_[i].setStyleSheet(u"QLabel{color:white;}")
            self.ui.get_3_day_weather_label_night_tip_[i].setStyleSheet(u"QLabel{color:white;}")
            self.ui.get_3_day_weather_label_day_temp_[i].setStyleSheet(u"QLabel{color:white;}")
            self.ui.get_3_day_weather_label_day_precip_[i].setStyleSheet(u"QLabel{color:white;}")
            self.ui.get_3_day_weather_label_day_uvIndex_[i].setStyleSheet(u"QLabel{color:white;}")
            self.ui.get_3_day_weather_label_day_humidity_[i].setStyleSheet(u"QLabel{color:white;}")

        self.ui.check_system_QLabel.setStyleSheet(u"QLabel{color:white;}")
        self.ui.get_api_key_button.setStyleSheet(u"QPushButton{background-color:transparent;color:white;}")
        self.ui.check_api_key_QLabel.setStyleSheet(u"QLabel{color:white;}")
        self.ui.updatetime.setStyleSheet(u"QLabel{color:white;}")
        self.ui.location_ip.setStyleSheet(u"QLabel{color:white;}")
        self.ui.earthquake_web_button.setStyleSheet(u"QPushButton{background-color:transparent;color:white;}")
        self.ui.earthquake_massage.setStyleSheet(u"QLabel{background-color:transparent;color:white;}")
        self.ui.typhoon_web_button.setStyleSheet(u"QPushButton{background-color:transparent;color:white;}")

        for i in range(5):
            self.ui.weather_warn_tip_[i].setStyleSheet(u"QLabel{color:white;}")
            self.ui.weather_warn_icon_[i].setStyleSheet(u"QLabel{color:white;}")
            self.ui.warn_sender_[i].setStyleSheet(u"QLabel{color:white;}")
            self.ui.warn_pubTime_[i].setStyleSheet(u"QLabel{color:white;}")
            self.ui.warn_title_[i].setStyleSheet(u"QLabel{color:white;}")
            self.ui.warn_text_[i].setStyleSheet(u"QLabel{color:white;}")
            self.ui.line_h2_[i].setStyleSheet("background-color: white;")

        for i in range(16):
            self.ui.life_weather_label_title_[i].setStyleSheet(u"QLabel{color:white;}")
            self.ui.life_weather_label_level_[i].setStyleSheet(u"QLabel{color:white;}")
            self.ui.life_weather_label_text_[i].setStyleSheet(u"QLabel{color:white;}")

            self.ui.life_weather_checkBox_[i].setStyleSheet(u"QCheckBox{color:white;}"
                                                            u"QCheckBox:indicator:unchecked{max-width:50px;"
                                                            "image: url(icon/Selection box white.png);}"
                                                            u"QCheckBox:indicator:unchecked:hover{max-width:50px;"
                                                            "image: url(icon/Selection box gray.png);}"
                                                            u"QCheckBox:indicator:checked{max-width:50px;"
                                                            "image: url(icon/Selection box checked white.png);}"
                                                            u"QCheckBox:indicator:checked:hover{max-width:50px;"
                                                            "image: url(icon/Selection box checked gray.png);}")

        self.ui.more_weather_air_tip_title.setStyleSheet(u"QLabel{color:white;}")
        self.ui.more_weather_air_tip_pm10.setStyleSheet(u"QLabel{color:white;}")
        self.ui.more_weather_air_value_pm10.setStyleSheet(u"QLabel{color:white;}")
        self.ui.more_weather_air_tip_pm25.setStyleSheet(u"QLabel{color:white;}")
        self.ui.more_weather_air_value_pm25.setStyleSheet(u"QLabel{color:white;}")
        self.ui.more_weather_air_tip_no2.setStyleSheet(u"QLabel{color:white;}")
        self.ui.more_weather_air_value_no2.setStyleSheet(u"QLabel{color:white;}")
        self.ui.more_weather_air_tip_so2.setStyleSheet(u"QLabel{color:white;}")
        self.ui.more_weather_air_value_so2.setStyleSheet(u"QLabel{color:white;}")
        self.ui.more_weather_air_tip_co.setStyleSheet(u"QLabel{color:white;}")
        self.ui.more_weather_air_value_co.setStyleSheet(u"QLabel{color:white;}")
        self.ui.more_weather_air_tip_o3.setStyleSheet(u"QLabel{color:white;}")
        self.ui.more_weather_air_value_o3.setStyleSheet(u"QLabel{color:white;}")

        self.ui.api_key_QLineEdit.setStyleSheet(u"QLineEdit{font-size:14px;border-top:0px  solid;border-bottom:1px  "
                                                u"solid;border-left:0px  solid;border-right: 0px  "
                                                "solid;"
                                                "background-color:transparent;color:white;border-bottom-color:rgb(255, "
                                                "255, 255);}")

        self.ui.select_way_QLabel.setStyleSheet(u"QLabel{color:white;}")
        self.ui.select_color_QLabel.setStyleSheet(u"QLabel{color:white;}")
        self.ui.select_color_system.setStyleSheet(u"QLabel{color:white;}")

        self.ui.life_weather_all_checkBox.setStyleSheet(u"QCheckBox{color:white;}"
                                                        u"QCheckBox:indicator:unchecked{max-width:50px;"
                                                        "image: url(icon/Selection box white.png);}"
                                                        u"QCheckBox:indicator:unchecked:hover{max-width:50px;"
                                                        "image: url(icon/Selection box gray.png);}"
                                                        u"QCheckBox:indicator:checked{max-width:50px;"
                                                        "image: url(icon/Selection box checked white.png);}"
                                                        u"QCheckBox:indicator:checked:hover{max-width:50px;"
                                                        "image: url(icon/Selection box checked gray.png);}")

        self.ui.location_ip_Button.setStyleSheet(u"QPushButton{border:none;image:url(icon/location white.png);}"
                                                 "QPushButton:hover{image: url(icon/locationgray.png);}")

        self.ui.map_Button.setStyleSheet(u"QPushButton{border:none;image:url(icon/map white.png);}"
                                         "QPushButton:hover{image: url(icon/map gray.png);}")

        self.ui.search_favorites.setStyleSheet(u"QPushButton{border:none;image:url(icon/favoritesunselectwhite.png);}")

        self.ui.closeButton_dialog.setStyleSheet(u"QPushButton{font-size:15px;border:none;color:white;}"
                                                 u"QPushButton:hover{font-size:15px;border:none;color:rgb(230,230,230);}")

        self.ui.saveButton_dialog.setStyleSheet(u"QPushButton{font-size:15px;border:none;color:white;}"
                                                u"QPushButton:hover{font-size:15px;border:none;color:rgb(230,230,230);}")

        self.ui.select_life_weather_QLabel.setStyleSheet(u"QLabel{color:white;}")

        self.ui.line_4.setStyleSheet("background-color: white;")
        self.ui.line_3.setStyleSheet("background-color: white;")
        self.ui.line_h5_1.setStyleSheet("background-color: white;")
        self.ui.line_h1_1.setStyleSheet("background-color: white;")
        self.ui.line_h1_2.setStyleSheet("background-color: white;")
        self.ui.line_h1_3.setStyleSheet("background-color: white;")
        self.ui.line_h1_4.setStyleSheet("background-color: white;")
        self.ui.line_2.setStyleSheet("background-color: white;")
        self.ui.line.setStyleSheet("background-color: white;")
        self.ui.line_h_1.setStyleSheet("background-color: white;")
        self.ui.line_h.setStyleSheet("background-color: white;")

        self.ui.favorites.setStyleSheet(u"QPushButton{border:none;image:url(icon/favoriteswhite.png);}")

        if self.api_key_Check_success:
            self.ui.check_api_key_icon.setPixmap(QPixmap('icon/round_check.png'))
        else:
            self.ui.check_api_key_icon.setPixmap(QPixmap('icon/error.png'))

        if self.allow_follow_success_theme:
            self.ui.select_color_system_button.setStyleSheet(
                u"QPushButton{border:none;image: url(icon/buttonselect.png);}")
        else:
            self.ui.select_color_system_button.setStyleSheet(
                u"QPushButton{border:none;image: url(icon/buttonunselect.png);}")

        if not self.internet_connect_success:
            self.ui.check_api_key_icon.setPixmap(QPixmap('icon/question.png'))

        self.ui.searchButton.setStyleSheet(u"QPushButton{border:none;image: url(icon/search.png);}"
                                           "QPushButton:hover{image: url(icon/searchgray.png);}")

        self.ui.closeButton.setStyleSheet(u"QPushButton{border:none;image: url(icon/closewhite.png);}"
                                          "QPushButton:hover{background-color: rgb(255, 0, 0);"
                                          "image: url(icon/closewhite.png);}")

        self.ui.minButton.setStyleSheet(u"QPushButton{border:none;image: url(icon/minwhite.png);}"
                                        "QPushButton:hover{background-color: rgba(220, 220, 220, 60%);}")

        self.ui.now_weather_detailed.setStyleSheet(u"QPushButton{background-color:transparent;"
                                                   u"border:none;image:url(icon/more-down.png);}"
                                                   u"QPushButton:hover{image: url(icon/more-downgray.png);}")

        self.ui.change_page_life_weather_left.setStyleSheet(u"QPushButton{background-color:transparent;"
                                                            u"image:url(icon/arrow-left.png);}")

        self.ui.change_page_life_weather_right.setStyleSheet(u"QPushButton{background-color:transparent;"
                                                             u"image:url(icon/arrow-right.png);}")

        self.ui.change_page_tip_left.setStyleSheet(u"QPushButton{background-color:transparent;"
                                                   u"image:url(icon/arrow-left.png);}")

        self.ui.change_page_tip_right.setStyleSheet(u"QPushButton{background-color:transparent;"
                                                    u"image:url(icon/arrow-right.png);}")

        if 50 >= self.aqi_now >= 0:
            self.ui.more_weather_air_tip_all.setStyleSheet(
                u"QLabel{min-width: 80px; min-height: 80px;max-width:80px;"
                u"max-height: 80px;border-radius: 40px;color:white;"
                u"border:5px solid green;}")

        elif 150 >= self.aqi_now > 50:
            self.ui.more_weather_air_tip_all.setStyleSheet(
                u"QLabel{min-width: 80px; min-height: 80px;max-width:80px;"
                u"max-height: 80px;border-radius: 40px;color:white;"
                u"border:5px solid yellow;}")

        elif 300 >= self.aqi_now > 150:
            self.ui.more_weather_air_tip_all.setStyleSheet(
                u"QLabel{min-width: 80px; min-height: 80px;max-width:80px;"
                u"max-height: 80px;border-radius: 40px;color:white;"
                u"border:5px solid orange;}")

        elif self.aqi_now > 300:
            self.ui.more_weather_air_tip_all.setStyleSheet(
                u"QLabel{min-width: 80px; min-height: 80px;max-width:80px;"
                u"max-height: 80px;border-radius: 40px;color:white;"
                u"border:5px solid red;}")

        self.theme_color = 'dark'

        self.favorites_city()

        self.theme_color_dark_lock = False
        self.theme_color_light_lock = True

    def ui_style_light(self):

        self.ui.title.setStyleSheet(u"QPushButton{background-color:transparent;border:none;color:black;}")
        self.ui.location.setStyleSheet(u"QLabel{color:black;}")
        self.ui.background.setStyleSheet(u"QLabel{background-color:rgba(170, 255, 255,60%);}")
        self.ui.background_dialog.setStyleSheet(u"QLabel{background-color:rgba(170, 255, 255,60%);}")
        self.ui.select_way_ComboBox.setStyleSheet(u"font-size:15px;color:black;border:none;"
                                                  "background-color:rgba(170, 255, 255,60%);")
        self.ui.favorites_listView.setStyleSheet(u"QListView{background-color:rgb(120, 180, 180);color:black;}"
                                                 u"QScrollBar:vertical{background-color:rgb(120, 180, 180);}")

        self.ui.search.setStyleSheet(u"QLineEdit{font-size:16px;border-top:0px  solid;border-bottom:1px solid;"
                                     "border-left:0px  solid;border-right: 0px  solid;"
                                     "background-color:transparent;color:black;border-bottom-color:rgb(0, 0, 0);}")

        self.ui.now_weather_tip.setStyleSheet(u"QLabel{color:black;}")
        self.ui.now_weather_temperature.setStyleSheet(u"QLabel{color:black;}")

        self.ui.lcdNumber.setStyleSheet(u"QLCDNumber{color:black;}")

        # lcdpat = QPalette(self.ui.lcdNumber.palette())  # 失去焦点时不可用
        # lcdpat.setColor(QPalette.Normal, QPalette.WindowText, Qt.black)
        # self.ui.lcdNumber.setPalette(lcdpat)

        for i in range(3):
            self.ui.get_3_day_weather_label_day_[i].setStyleSheet(u"QLabel{color:black;}")
            self.ui.get_3_day_weather_label_day_tip_[i].setStyleSheet(u"QLabel{color:black;}")
            self.ui.get_3_day_weather_label_night_tip_[i].setStyleSheet(u"QLabel{color:black;}")
            self.ui.get_3_day_weather_label_day_temp_[i].setStyleSheet(u"QLabel{color:black;}")
            self.ui.get_3_day_weather_label_day_precip_[i].setStyleSheet(u"QLabel{color:black;}")
            self.ui.get_3_day_weather_label_day_uvIndex_[i].setStyleSheet(u"QLabel{color:black;}")
            self.ui.get_3_day_weather_label_day_humidity_[i].setStyleSheet(u"QLabel{color:black;}")

        self.ui.check_system_QLabel.setStyleSheet(u"QLabel{color:black;}")
        self.ui.get_api_key_button.setStyleSheet(u"QPushButton{background-color:transparent;color:black;}")
        self.ui.check_api_key_QLabel.setStyleSheet(u"QLabel{color:black;}")
        self.ui.updatetime.setStyleSheet(u"QLabel{color:black;}")
        self.ui.location_ip.setStyleSheet(u"QLabel{color:black;}")
        self.ui.earthquake_web_button.setStyleSheet(u"QPushButton{background-color:transparent;color:black;}")
        self.ui.earthquake_massage.setStyleSheet(u"QLabel{background-color:transparent;color:black;}")
        self.ui.typhoon_web_button.setStyleSheet(u"QPushButton{background-color:transparent;color:black;}")

        for i in range(5):
            self.ui.weather_warn_tip_[i].setStyleSheet(u"QLabel{color:black;}")
            self.ui.weather_warn_icon_[i].setStyleSheet(u"QLabel{color:black;}")
            self.ui.warn_sender_[i].setStyleSheet(u"QLabel{color:black;}")
            self.ui.warn_pubTime_[i].setStyleSheet(u"QLabel{color:black;}")
            self.ui.warn_title_[i].setStyleSheet(u"QLabel{color:black;}")
            self.ui.warn_text_[i].setStyleSheet(u"QLabel{color:black;}")
            self.ui.line_h2_[i].setStyleSheet("background-color: black;")

        for i in range(16):
            self.ui.life_weather_label_title_[i].setStyleSheet(u"QLabel{color:black;}")
            self.ui.life_weather_label_level_[i].setStyleSheet(u"QLabel{color:black;}")
            self.ui.life_weather_label_text_[i].setStyleSheet(u"QLabel{color:black;}")

            self.ui.life_weather_checkBox_[i].setStyleSheet(u"QCheckBox{color:black;}"
                                                            u"QCheckBox:indicator:unchecked{max-width:50px;"
                                                            "image: url(icon/Selection box black.png);}"
                                                            u"QCheckBox:indicator:unchecked:hover{max-width:50px;"
                                                            "image: url(icon/Selection box gray.png);}"
                                                            u"QCheckBox:indicator:checked{max-width:50px;"
                                                            "image: url(icon/Selection box checked black.png);}"
                                                            u"QCheckBox:indicator:checked:hover{max-width:50px;"
                                                            "image: url(icon/Selection box checked gray.png);}")

        self.ui.more_weather_air_tip_title.setStyleSheet(u"QLabel{color:black;}")
        self.ui.more_weather_air_tip_pm10.setStyleSheet(u"QLabel{color:black;}")
        self.ui.more_weather_air_value_pm10.setStyleSheet(u"QLabel{color:black;}")
        self.ui.more_weather_air_tip_pm25.setStyleSheet(u"QLabel{color:black;}")
        self.ui.more_weather_air_value_pm25.setStyleSheet(u"QLabel{color:black;}")
        self.ui.more_weather_air_tip_no2.setStyleSheet(u"QLabel{color:black;}")
        self.ui.more_weather_air_value_no2.setStyleSheet(u"QLabel{color:black;}")
        self.ui.more_weather_air_tip_so2.setStyleSheet(u"QLabel{color:black;}")
        self.ui.more_weather_air_value_so2.setStyleSheet(u"QLabel{color:black;}")
        self.ui.more_weather_air_tip_co.setStyleSheet(u"QLabel{color:black;}")
        self.ui.more_weather_air_value_co.setStyleSheet(u"QLabel{color:black;}")
        self.ui.more_weather_air_tip_o3.setStyleSheet(u"QLabel{color:black;}")
        self.ui.more_weather_air_value_o3.setStyleSheet(u"QLabel{color:black;}")

        self.ui.api_key_QLineEdit.setStyleSheet(u"QLineEdit{font-size:14px;border-top:0px  solid;border-bottom:1px  "
                                                u"solid;border-left:0px  solid;border-right: 0px  "
                                                "solid;"
                                                "background-color:transparent;color:black;border-bottom-color:rgb(0, "
                                                "0, 0);}")

        self.ui.select_way_QLabel.setStyleSheet(u"QLabel{color:black;}")
        self.ui.select_color_QLabel.setStyleSheet(u"QLabel{color:black;}")
        self.ui.select_color_system.setStyleSheet(u"QLabel{color:black;}")

        self.ui.life_weather_all_checkBox.setStyleSheet(u"QCheckBox{color:black;}"
                                                        u"QCheckBox:indicator:unchecked{max-width:50px;"
                                                        "image: url(icon/Selection box black.png);}"
                                                        u"QCheckBox:indicator:unchecked:hover{max-width:50px;"
                                                        "image: url(icon/Selection box gray.png);}"
                                                        u"QCheckBox:indicator:checked{max-width:50px;"
                                                        "image: url(icon/Selection box checked black.png);}"
                                                        u"QCheckBox:indicator:checked:hover{max-width:50px;"
                                                        "image: url(icon/Selection box checked gray.png);}")

        self.ui.location_ip_Button.setStyleSheet(u"QPushButton{border:none;image:url(icon/location black.png);}"
                                                 "QPushButton:hover{image: url(icon/locationgray.png);}")

        self.ui.map_Button.setStyleSheet(u"QPushButton{border:none;image:url(icon/map black.png);}"
                                         "QPushButton:hover{image: url(icon/map gray.png);}")

        self.ui.search_favorites.setStyleSheet(u"QPushButton{border:none;image:url(icon/favoritesunselectblack.png);}")

        self.ui.closeButton_dialog.setStyleSheet(u"QPushButton{font-size:15px;border:none;color:black;}"
                                                 u"QPushButton:hover{font-size:15px;border:none;color:rgb(230,230,230);}")

        self.ui.saveButton_dialog.setStyleSheet(u"QPushButton{font-size:15px;border:none;color:black;}"
                                                u"QPushButton:hover{font-size:15px;border:none;color:rgb(230,230,230);}")

        self.ui.select_life_weather_QLabel.setStyleSheet(u"QLabel{color:black;}")

        self.ui.line_4.setStyleSheet("background-color: black;")
        self.ui.line_3.setStyleSheet("background-color: black;")
        self.ui.line_h5_1.setStyleSheet("background-color: black;")
        self.ui.line_h1_1.setStyleSheet("background-color: black;")
        self.ui.line_h1_2.setStyleSheet("background-color: black;")
        self.ui.line_h1_3.setStyleSheet("background-color: black;")
        self.ui.line_h1_4.setStyleSheet("background-color: black;")
        self.ui.line_2.setStyleSheet("background-color: black;")
        self.ui.line.setStyleSheet("background-color: black;")
        self.ui.line_h_1.setStyleSheet("background-color: black;")
        self.ui.line_h.setStyleSheet("background-color: black;")

        self.ui.favorites.setStyleSheet(u"QPushButton{border:none;image:url(icon/favoritesblack.png);}")

        if self.api_key_Check_success:
            self.ui.check_api_key_icon.setPixmap(QPixmap('icon/round_checkblack.png'))
        else:
            self.ui.check_api_key_icon.setPixmap(QPixmap('icon/errorblack.png'))

        if not self.internet_connect_success:
            self.ui.check_api_key_icon.setPixmap(QPixmap('icon/questionblack.png'))

        if self.allow_follow_success_theme:
            self.ui.select_color_system_button.setStyleSheet(
                u"QPushButton{border:none;image: url(icon/buttonselectblack.png);}")
        else:
            self.ui.select_color_system_button.setStyleSheet(
                u"QPushButton{border:none;image: url(icon/buttonunselectblack.png);}")

        self.ui.searchButton.setStyleSheet(u"QPushButton{border:none;image: url(icon/searchblack.png);}"
                                           "QPushButton:hover{image: url(icon/searchgray.png);}")

        self.ui.closeButton.setStyleSheet(u"QPushButton{border:none;image: url(icon/closeblack.png);}"
                                          "QPushButton:hover{background-color: rgb(255, 0, 0);"
                                          "image: url(icon/closeblack.png);}")

        self.ui.minButton.setStyleSheet(u"QPushButton{border:none;image: url(icon/minblack.png);}"
                                        "QPushButton:hover{background-color: rgba(220, 220, 220, 60%);}")

        self.ui.now_weather_detailed.setStyleSheet(u"QPushButton{background-color:transparent;"
                                                   u"border:none;image:url(icon/more-downblack.png);}"
                                                   u"QPushButton:hover{image: url(icon/more-downgray.png);}")

        self.ui.change_page_life_weather_left.setStyleSheet(u"QPushButton{background-color:transparent;"
                                                            u"image:url(icon/arrow-leftblack.png);}")

        self.ui.change_page_life_weather_right.setStyleSheet(u"QPushButton{background-color:transparent;"
                                                             u"image:url(icon/arrow-rightblack.png);}")

        self.ui.change_page_tip_left.setStyleSheet(u"QPushButton{background-color:transparent;"
                                                   u"image:url(icon/arrow-leftblack.png);}")

        self.ui.change_page_tip_right.setStyleSheet(u"QPushButton{background-color:transparent;"
                                                    u"image:url(icon/arrow-rightblack.png);}")

        if 50 >= self.aqi_now >= 0:
            self.ui.more_weather_air_tip_all.setStyleSheet(
                u"QLabel{min-width: 80px; min-height: 80px;max-width:80px;"
                u"max-height: 80px;border-radius: 40px;color:black;"
                u"border:5px solid green;}")

        elif 150 >= self.aqi_now > 50:
            self.ui.more_weather_air_tip_all.setStyleSheet(
                u"QLabel{min-width: 80px; min-height: 80px;max-width:80px;"
                u"max-height: 80px;border-radius: 40px;color:black;"
                u"border:5px solid yellow;}")

        elif 300 >= self.aqi_now > 150:
            self.ui.more_weather_air_tip_all.setStyleSheet(
                u"QLabel{min-width: 80px; min-height: 80px;max-width:80px;"
                u"max-height: 80px;border-radius: 40px;color:black;"
                u"border:5px solid orange;}")

        elif self.aqi_now > 300:
            self.ui.more_weather_air_tip_all.setStyleSheet(
                u"QLabel{min-width: 80px; min-height: 80px;max-width:80px;"
                u"max-height: 80px;border-radius: 40px;color:black;"
                u"border:5px solid red;}")

        self.theme_color = 'light'

        self.favorites_city()

        self.theme_color_dark_lock = True
        self.theme_color_light_lock = False

    def select_ui_style(self):

        if self.theme_color == 'dark':
            self.ui_style_dark()

        elif self.theme_color == 'light':
            self.ui_style_light()

    def allow_follow_system_theme_click(self):

        if self.allow_follow_success_theme:
            if self.theme_color == 'dark':
                self.ui.select_color_system_button.setStyleSheet(
                    u"QPushButton{border:none;image: url(icon/buttonunselect.png);}")
            elif self.theme_color == 'light':
                self.ui.select_color_system_button.setStyleSheet(
                    u"QPushButton{border:none;image: url(icon/buttonunselectblack.png);}")
            self.allow_follow_success_theme = False
            self.ui.select_color_dark.setEnabled(1)
            self.ui.select_color_light.setEnabled(1)
        else:
            if self.theme_color == 'dark':
                self.ui.select_color_system_button.setStyleSheet(
                    u"QPushButton{border:none;image: url(icon/buttonselect.png);}")
            elif self.theme_color == 'light':
                self.ui.select_color_system_button.setStyleSheet(
                    u"QPushButton{border:none;image: url(icon/buttonselectblack.png);}")
            self.allow_follow_success_theme = True
            self.ui.select_color_dark.setEnabled(0)
            self.ui.select_color_light.setEnabled(0)

    def allow_follow_system_theme(self):

        if self.allow_follow_success_theme:
            if self.theme_color == 'dark':
                self.ui.select_color_system_button.setStyleSheet(
                    u"QPushButton{border:none;image: url(icon/buttonselect.png);}")
            elif self.theme_color == 'light':
                self.ui.select_color_system_button.setStyleSheet(
                    u"QPushButton{border:none;image: url(icon/buttonselectblack.png);}")
            self.ui.select_color_dark.setEnabled(0)
            self.ui.select_color_light.setEnabled(0)

        else:
            if self.theme_color == 'dark':
                self.ui.select_color_system_button.setStyleSheet(
                    u"QPushButton{border:none;image: url(icon/buttonunselect.png);}")
            elif self.theme_color == 'light':
                self.ui.select_color_system_button.setStyleSheet(
                    u"QPushButton{border:none;image: url(icon/buttonunselectblack.png);}")
            self.ui.select_color_dark.setEnabled(1)
            self.ui.select_color_light.setEnabled(1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    translator = QTranslator()
    translator.load("translator/widgets_zh_CN_all.qm")
    app.installTranslator(translator)
    MyWelcomeWindow = MyWelcomeWindow()
    MyWelcomeWindow.show()
    sys.exit(app.exec_())
