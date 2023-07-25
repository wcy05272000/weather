import math

from PySide2.QtCore import Qt, QRect, QRegularExpression, QSize
from PySide2.QtGui import QFont, QRegularExpressionValidator, QIcon
from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtWidgets import QWidget, QLabel, QPushButton, QLCDNumber, QFrame, QLineEdit, QStackedWidget, QListView, \
    QHBoxLayout, QScrollArea, QVBoxLayout, QComboBox, QDialog, QCheckBox


class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")

        # screen = QGuiApplication.primaryScreen().geometry()  # 获取屏幕类并调用geometry()方法获取屏幕大小
        # screen_width = screen.width()  # 获取屏幕的宽
        # screen_height = screen.height()  # 获取屏幕的高

        screen_width = 1920
        screen_height = 1080

        Form.resize(screen_width / 2, screen_height / 2)
        icon = QIcon()
        icon.addFile(u"icon/windowsicon.ico", QSize(), QIcon.Normal, QIcon.Off)
        Form.setWindowIcon(icon)

        Form.setWindowFlag(Qt.FramelessWindowHint)
        Form.setWindowFlag(Qt.WindowStaysOnTopHint)
        Form.setAttribute(Qt.WA_TranslucentBackground)

        self.background = QLabel(Form)
        self.background.setObjectName(u"background")
        self.background.setGeometry(QRect(10, 10, screen_width / 2, screen_width / 2))

        self.closeButton = QPushButton(Form)
        self.closeButton.setObjectName(u"closeButton")
        self.closeButton.setGeometry(QRect(screen_width / 2 - 30, 10, 30, 30))
        self.closeButton.setToolTip("关闭")

        self.minButton = QPushButton(Form)
        self.minButton.setObjectName(u"minButton")
        self.minButton.setGeometry(QRect(screen_width / 2 - 60, 10, 30, 30))

        self.minButton.setToolTip("最小化")

        self.movie_earthquake = QLabel(Form)
        self.movie_earthquake.setGeometry(QRect(710, 330, 170, 140))
        self.movie_earthquake.setScaledContents(True)

        self.movie_day_weather = QLabel(Form)
        self.movie_day_weather.setGeometry(QRect(380, 110, 170, 140))
        self.movie_day_weather.setScaledContents(True)

        self.title = QPushButton(Form)
        self.title.setObjectName(u"title")
        self.title.setGeometry(QRect(15, 12, 35, 25))
        self.title.setFont(QFont("微软雅黑", 10))
        # strT = '<div style=\" color:black;font-size:20px;text-align:left;\">%s</div>' \
        #        '<div style=\" color:gray;font-size:20px;text-align:left;\">%s</div>' % ('现在开始', '添加模式')
        # self.tip.setText("%s" % strT)
        self.title.setCursor(Qt.PointingHandCursor)

        self.title.setText("天气")
        self.title.setToolTip("设置")

        self.lcdNumber = QLCDNumber(Form)
        self.lcdNumber.setObjectName(u"lcdNumber")
        self.lcdNumber.setGeometry(QRect(10, 40, 300, 40))
        self.lcdNumber.setLineWidth(0)  # 设置边框宽度
        self.lcdNumber.setDigitCount(19)  # 设置LCD数字数量
        self.lcdNumber.setSegmentStyle(QLCDNumber.Flat)


        self.favorites = QPushButton(Form)
        self.favorites.setObjectName(u"favorites")
        self.favorites.setGeometry(QRect(70, 12, 35, 25))
        self.favorites.setCursor(Qt.PointingHandCursor)
        self.favorites.setToolTip("收藏夹")

        self.location = QLabel(Form)
        self.location.setObjectName(u"location")
        self.location.setGeometry(QRect(140, 12, 400, 25))
        self.location.setAlignment(Qt.AlignCenter)
        self.location.setAlignment(Qt.AlignHCenter)
        self.location.setFont(QFont("微软雅黑", 10))


        self.line_h = QFrame(Form)
        self.line_h.setObjectName(u"line_h")
        self.line_h.setGeometry(QRect(screen_width / 2 - 60, 10, 2, 30))
        self.line_h.setFrameShape(QFrame.VLine)
        self.line_h.setFrameShadow(QFrame.Sunken)

        self.line_h_1 = QFrame(Form)
        self.line_h_1.setObjectName(u"line_h_1")
        self.line_h_1.setGeometry(QRect(screen_width / 2 - 285, 10, 1, 30))
        self.line_h_1.setFrameShape(QFrame.VLine)
        self.line_h_1.setFrameShadow(QFrame.Sunken)

        self.line = QFrame(Form)
        self.line.setObjectName(u"line")
        self.line.setGeometry(QRect(10, 40, screen_width / 2, 1))
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.search_favorites = QPushButton(Form)
        self.search_favorites.setObjectName(u"search_favorites")
        self.search_favorites.setGeometry(QRect(screen_width / 2 - 325, 12, 30, 25))
        self.search_favorites.setCursor(Qt.PointingHandCursor)
        self.search_favorites.setToolTip("未收藏")

        self.search = QLineEdit(Form)
        self.search.setObjectName(u"search")
        self.search.setTextMargins(0, 0, 31, 0)
        self.search.setGeometry(QRect(screen_width / 2 - 280, 10, 210, 31))
        self.search.setPlaceholderText("市/县/区")
        # self.search.setClearButtonEnabled(True)

        self.searchButton = QPushButton(self.search)
        self.searchButton.setObjectName(u"searchButton")
        self.searchButton.setGeometry(185, 2, 26, 26)
        self.searchButton.setCursor(Qt.PointingHandCursor)
        self.searchButton.setToolTip("搜索")

        self.now_weather_icon = QLabel(Form)
        self.now_weather_icon.setObjectName(u"now_weather_icon")
        self.now_weather_icon.setGeometry(360, 40, 40, 40)
        # self.now_weather.setStyleSheet(u"QLabel{background-color:white;}")

        self.now_weather_tip = QLabel(Form)
        self.now_weather_tip.setObjectName(u"now_weather_tip")
        self.now_weather_tip.setGeometry(420, 40, 180, 40)
        self.now_weather_tip.setAlignment(Qt.AlignCenter)
        self.now_weather_tip.setFont(QFont("微软雅黑", 11))

        self.now_weather_temperature = QLabel(Form)
        self.now_weather_temperature.setObjectName(u"now_weather_temperature")
        self.now_weather_temperature.setGeometry(620, 40, 40, 40)
        self.now_weather_temperature.setAlignment(Qt.AlignCenter)
        self.now_weather_temperature.setFont(QFont("微软雅黑", 11))

        self.now_weather_detailed = QPushButton(Form)
        self.now_weather_detailed.setObjectName(u"now_weather_detailed")
        self.now_weather_detailed.setGeometry(screen_width / 2 - 60, 48, 24, 24)
        self.now_weather_detailed.setCursor(Qt.PointingHandCursor)
        self.now_weather_detailed.setToolTip("详细信息")
        self.now_weather_detailed.hide()

        self.line_2 = QFrame(Form)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setGeometry(QRect(10, 80, screen_width / 2, 1))
        self.line_2.setFrameShape(QFrame.HLine)
        self.line_2.setFrameShadow(QFrame.Sunken)

        ##############################################################################
        ##############################################################################
        #  天气图标示表
        self.stackedWidget_weather = QStackedWidget(Form)
        self.stackedWidget_weather.setObjectName(u"stackedWidget_weather")
        self.stackedWidget_weather.setGeometry(QRect(10, 85, screen_width / 2, 200))
        # self.stackedWidget.setStyleSheet(u"QStackedWidget{background-color: rgb(94, 255, 183);}")
        self.page_weather = QWidget()
        self.page_weather.setObjectName(u"page_weather")
        self.stackedWidget_weather.addWidget(self.page_weather)
        self.page_weather_2 = QWidget()
        self.page_weather_2.setObjectName(u"page_weather_2")
        self.stackedWidget_weather.addWidget(self.page_weather_2)
        self.page_weather_3 = QWidget()
        self.page_weather_3.setObjectName(u"page_weather_3")
        self.stackedWidget_weather.addWidget(self.page_weather_3)

        ##############################################################################
        ##############################################################################
        self.get_3_day_weather_label_day_ = {}
        self.get_3_day_weather_label_day_icon_ = {}
        self.get_3_day_weather_label_night_icon_ = {}
        self.get_3_day_weather_label_day_tip_ = {}
        self.get_3_day_weather_label_night_tip_ = {}
        self.get_3_day_weather_label_day_temp_ = {}
        self.get_3_day_weather_label_day_precip_ = {}
        self.get_3_day_weather_label_day_uvIndex_ = {}
        self.get_3_day_weather_label_day_humidity_ = {}

        # 未来3日天气预报

        for i in range(3):
            # (时间)
            self.get_3_day_weather_label_day_[i] = QLabel(self.page_weather)
            self.get_3_day_weather_label_day_[i].setObjectName(u"get_3_day_weather_label_day_"[i])
            self.get_3_day_weather_label_day_[i].setGeometry(QRect(80 + (i * screen_width / 6), 0, 120, 40))
            self.get_3_day_weather_label_day_[i].setFont(QFont("微软雅黑", 11))
            self.get_3_day_weather_label_day_[i].setAlignment(Qt.AlignHCenter)

            # （白天图标）
            self.get_3_day_weather_label_day_icon_[i] = QLabel(self.page_weather)
            self.get_3_day_weather_label_day_icon_[i].setObjectName(u"get_3_day_weather_label_day_icon_"[i])
            self.get_3_day_weather_label_day_icon_[i].setGeometry(QRect(60 + (i * screen_width / 6), 20, 60, 60))
            self.get_3_day_weather_label_day_icon_[i].setScaledContents(True)
            # self.get_3_day_weather_label1_day_icon.setStyleSheet(u"QLabel{background-color:white;}")

            # （夜晚图标）
            self.get_3_day_weather_label_night_icon_[i] = QLabel(self.page_weather)
            self.get_3_day_weather_label_night_icon_[i].setObjectName(u"get_3_day_weather_label_night_icon_"[i])
            self.get_3_day_weather_label_night_icon_[i].setGeometry(QRect(160 + (i * screen_width / 6), 20, 60, 60))
            self.get_3_day_weather_label_night_icon_[i].setScaledContents(True)

            # （白天描述）
            self.get_3_day_weather_label_day_tip_[i] = QLabel(self.page_weather)
            self.get_3_day_weather_label_day_tip_[i].setObjectName(u"get_3_day_weather_label1_day_tip_"[i])
            self.get_3_day_weather_label_day_tip_[i].setGeometry(QRect(55 + (i * screen_width / 6), 75, 70, 30))
            self.get_3_day_weather_label_day_tip_[i].setFont(QFont("微软雅黑", 9))
            self.get_3_day_weather_label_day_tip_[i].setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

            # （夜晚描述）
            self.get_3_day_weather_label_night_tip_[i] = QLabel(self.page_weather)
            self.get_3_day_weather_label_night_tip_[i].setObjectName(u"get_3_day_weather_label1_night_tip_"[i])
            self.get_3_day_weather_label_night_tip_[i].setGeometry(QRect(155 + (i * screen_width / 6), 75, 70, 30))
            self.get_3_day_weather_label_night_tip_[i].setFont(QFont("微软雅黑", 9))
            self.get_3_day_weather_label_night_tip_[i].setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

            # （气温）
            self.get_3_day_weather_label_day_temp_[i] = QLabel(self.page_weather)
            self.get_3_day_weather_label_day_temp_[i].setObjectName(u"get_3_day_weather_label1_day_tip_"[i])
            self.get_3_day_weather_label_day_temp_[i].setGeometry(QRect(100 + (i * screen_width / 6), 100, 80, 30))
            self.get_3_day_weather_label_day_temp_[i].setFont(QFont("微软雅黑", 9))
            self.get_3_day_weather_label_day_temp_[i].setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

            # （降水量）
            self.get_3_day_weather_label_day_precip_[i] = QLabel(self.page_weather)
            self.get_3_day_weather_label_day_precip_[i].setObjectName(u"get_3_day_weather_label1_day_precip_"[i])
            self.get_3_day_weather_label_day_precip_[i].setGeometry(QRect(50 + (i * screen_width / 6), 125, 180, 30))
            self.get_3_day_weather_label_day_precip_[i].setFont(QFont("微软雅黑", 9))
            self.get_3_day_weather_label_day_precip_[i].setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

            # （紫外线强度）
            self.get_3_day_weather_label_day_uvIndex_[i] = QLabel(self.page_weather)
            self.get_3_day_weather_label_day_uvIndex_[i].setObjectName(u"get_3_day_weather_label1_day_uvIndex_"[i])
            self.get_3_day_weather_label_day_uvIndex_[i].setGeometry(QRect(50 + (i * screen_width / 6), 145, 180, 30))
            self.get_3_day_weather_label_day_uvIndex_[i].setFont(QFont("微软雅黑", 9))
            self.get_3_day_weather_label_day_uvIndex_[i].setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

            # （相对湿度）
            self.get_3_day_weather_label_day_humidity_[i] = QLabel(self.page_weather)
            self.get_3_day_weather_label_day_humidity_[i].setObjectName(u"get_3_day_weather_label1_day_humidity_"[i])
            self.get_3_day_weather_label_day_humidity_[i].setGeometry(QRect(50 + (i * screen_width / 6), 165, 180, 30))
            self.get_3_day_weather_label_day_humidity_[i].setFont(QFont("微软雅黑", 9))
            self.get_3_day_weather_label_day_humidity_[i].setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        ##############################################################################
        ##############################################################################

        self.favorites_listView = QListView(Form)
        self.favorites_listView.setObjectName(u"favorites_listView")
        self.favorites_listView.setGeometry(QRect(55, 40, 180, 100))
        favorites_listView_font = QFont()
        favorites_listView_font.setPointSize(10)
        self.favorites_listView.setFont(favorites_listView_font)
        self.favorites_listView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.favorites_listView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.favorites_listView.hide()

        ##############################################################################
        ##############################################################################
        # 第一页 竖切线
        self.line_h1_1 = QFrame(self.page_weather)
        self.line_h1_1.setObjectName(u"line_h1_1")
        self.line_h1_1.setGeometry(QRect(300, 0, 1, 200))
        self.line_h1_1.setFrameShape(QFrame.VLine)
        self.line_h1_1.setFrameShadow(QFrame.Sunken)

        self.line_h1_2 = QFrame(self.page_weather)
        self.line_h1_2.setObjectName(u"line_h1_2")
        self.line_h1_2.setGeometry(QRect(620, 0, 1, 200))
        self.line_h1_2.setFrameShape(QFrame.VLine)
        self.line_h1_2.setFrameShadow(QFrame.Sunken)

        # 第二页 竖切线
        self.line_h1_3 = QFrame(self.page_weather_2)
        self.line_h1_3.setObjectName(u"line_h1_3")
        self.line_h1_3.setGeometry(QRect(300, 0, 1, 200))
        self.line_h1_3.setFrameShape(QFrame.VLine)
        self.line_h1_3.setFrameShadow(QFrame.Sunken)

        self.line_h1_4 = QFrame(self.page_weather_2)
        self.line_h1_4.setObjectName(u"line_h1_4")
        self.line_h1_4.setGeometry(QRect(620, 0, 1, 200))
        self.line_h1_4.setFrameShape(QFrame.VLine)
        self.line_h1_4.setFrameShadow(QFrame.Sunken)

        #  当日天气指数详情
        #  标题
        self.more_weather_air_tip_title = QLabel(self.page_weather_3)
        self.more_weather_air_tip_title.setObjectName(u"more_weather_air_tip_title")
        self.more_weather_air_tip_title.setGeometry(QRect(10, 0, 120, 30))
        self.more_weather_air_tip_title.setFont(QFont("微软雅黑", 10))
        self.more_weather_air_tip_title.setText("空气质量指数")

        ##############################################################################

        self.more_weather_air_tip_all = QLabel(self.page_weather_3)
        self.more_weather_air_tip_all.setObjectName(u"more_weather_air_tip_all")
        self.more_weather_air_tip_all.setGeometry(QRect(200, 30, 100, 100))
        self.more_weather_air_tip_all.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        self.more_weather_air_tip_all.setFont(QFont("微软雅黑", 12))

        ##############################################################################

        self.widget_all_air = QWidget(self.page_weather_3)
        self.widget_all_air.setObjectName(u"widget_all_air")
        self.widget_all_air.setGeometry(QRect(10, 120, 480, 80))
        self.horizontalLayout = QHBoxLayout(self.widget_all_air)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)

        ##############################################################################
        #  组合框(pm10)
        self.widget_pm10 = QWidget(self.page_weather_3)
        self.widget_pm10.setObjectName(u"widget_pm10")
        # self.widget_pm10.setGeometry(QRect(10, 120, 50, 80))
        self.verticalLayout_pm10 = QVBoxLayout()
        self.verticalLayout_pm10.setObjectName(u"verticalLayout_pm10")
        self.verticalLayout_pm10.setContentsMargins(0, 0, 0, 0)

        #  空气成分质量指数(pm10文字描述)
        self.more_weather_air_tip_pm10 = QLabel(self.widget_pm10)
        self.more_weather_air_tip_pm10.setObjectName(u"more_weather_air_tip_pm10")
        self.more_weather_air_tip_pm10.setFont(QFont("微软雅黑", 9))
        self.more_weather_air_tip_pm10.setText("PM10")
        self.verticalLayout_pm10.addWidget(self.more_weather_air_tip_pm10, 0, Qt.AlignCenter)

        #  空气成分质量指数(pm10数值)
        self.more_weather_air_value_pm10 = QLabel(self.widget_pm10)
        self.more_weather_air_value_pm10.setObjectName(u"more_weather_air_value_pm10")
        self.more_weather_air_value_pm10.setFont(QFont("微软雅黑", 9))
        self.verticalLayout_pm10.addWidget(self.more_weather_air_value_pm10, 0, Qt.AlignCenter)

        #  空气成分质量指数(pm10图标)
        self.more_weather_air_icon_pm10 = QLabel(self.widget_pm10)
        self.more_weather_air_icon_pm10.setObjectName(u"more_weather_air_icon_pm10")
        self.verticalLayout_pm10.addWidget(self.more_weather_air_icon_pm10, 0, Qt.AlignCenter)

        self.horizontalLayout.addLayout(self.verticalLayout_pm10)

        ##############################################################################
        #  组合框(pm2.5)
        self.widget_pm25 = QWidget(self.page_weather_3)
        self.widget_pm25.setObjectName(u"widget_pm25")
        # self.widget_pm25.setGeometry(QRect(70, 120, 50, 80))
        self.verticalLayout_pm25 = QVBoxLayout()
        self.verticalLayout_pm25.setObjectName(u"verticalLayout_pm25")
        self.verticalLayout_pm25.setContentsMargins(0, 0, 0, 0)

        #  空气成分质量指数(pm2.5文字描述)
        self.more_weather_air_tip_pm25 = QLabel(self.widget_pm25)
        self.more_weather_air_tip_pm25.setObjectName(u"more_weather_air_tip_pm25")
        self.more_weather_air_tip_pm25.setFont(QFont("微软雅黑", 9))
        self.more_weather_air_tip_pm25.setText("PM2.5")
        self.verticalLayout_pm25.addWidget(self.more_weather_air_tip_pm25, 0, Qt.AlignCenter)

        #  空气成分质量指数(pm2.5数值)
        self.more_weather_air_value_pm25 = QLabel(self.widget_pm25)
        self.more_weather_air_value_pm25.setObjectName(u"more_weather_air_value_pm25")
        self.more_weather_air_value_pm25.setFont(QFont("微软雅黑", 9))
        self.verticalLayout_pm25.addWidget(self.more_weather_air_value_pm25, 0, Qt.AlignCenter)

        #  空气成分质量指数(pm2.5图标)
        self.more_weather_air_icon_pm25 = QLabel(self.widget_pm25)
        self.more_weather_air_icon_pm25.setObjectName(u"more_weather_air_icon_pm25")
        self.verticalLayout_pm25.addWidget(self.more_weather_air_icon_pm25, 0, Qt.AlignCenter)

        self.horizontalLayout.addLayout(self.verticalLayout_pm25)

        ##############################################################################
        #  组合框(no2)
        self.widget_no2 = QWidget(self.page_weather_3)
        self.widget_no2.setObjectName(u"widget_no2")
        # self.widget_no2.setGeometry(QRect(120, 120, 50, 80))
        self.verticalLayout_no2 = QVBoxLayout()
        self.verticalLayout_no2.setObjectName(u"verticalLayout_no2")
        self.verticalLayout_no2.setContentsMargins(0, 0, 0, 0)

        #  空气成分质量指数(no2文字描述)
        self.more_weather_air_tip_no2 = QLabel(self.widget_no2)
        self.more_weather_air_tip_no2.setObjectName(u"more_weather_air_tip_no2")
        self.more_weather_air_tip_no2.setFont(QFont("微软雅黑", 9))
        self.more_weather_air_tip_no2.setText("NO2")
        self.verticalLayout_no2.addWidget(self.more_weather_air_tip_no2, 0, Qt.AlignCenter)

        #  空气成分质量指数(no2数值)
        self.more_weather_air_value_no2 = QLabel(self.widget_no2)
        self.more_weather_air_value_no2.setObjectName(u"more_weather_air_value_no2")
        self.more_weather_air_value_no2.setFont(QFont("微软雅黑", 9))
        self.verticalLayout_no2.addWidget(self.more_weather_air_value_no2, 0, Qt.AlignCenter)

        #  空气成分质量指数(no2图标)
        self.more_weather_air_icon_no2 = QLabel(self.widget_no2)
        self.more_weather_air_icon_no2.setObjectName(u"more_weather_air_icon_no2")
        self.verticalLayout_no2.addWidget(self.more_weather_air_icon_no2, 0, Qt.AlignCenter)

        self.horizontalLayout.addLayout(self.verticalLayout_no2)

        ##############################################################################
        #  组合框(so2)
        self.widget_so2 = QWidget(self.page_weather_3)
        self.widget_so2.setObjectName(u"widget_so2")
        # self.widget_so2.setGeometry(QRect(170, 120, 50, 80))
        self.verticalLayout_so2 = QVBoxLayout()
        self.verticalLayout_so2.setObjectName(u"verticalLayout_so2")
        self.verticalLayout_so2.setContentsMargins(0, 0, 0, 0)

        #  空气成分质量指数(so2文字描述)
        self.more_weather_air_tip_so2 = QLabel(self.widget_so2)
        self.more_weather_air_tip_so2.setObjectName(u"more_weather_air_tip_so2")
        self.more_weather_air_tip_so2.setFont(QFont("微软雅黑", 9))
        self.more_weather_air_tip_so2.setText("SO2")
        self.verticalLayout_so2.addWidget(self.more_weather_air_tip_so2, 0, Qt.AlignCenter)

        #  空气成分质量指数(so2数值)
        self.more_weather_air_value_so2 = QLabel(self.widget_so2)
        self.more_weather_air_value_so2.setObjectName(u"more_weather_air_value_so2")
        self.more_weather_air_value_so2.setFont(QFont("微软雅黑", 9))
        self.verticalLayout_so2.addWidget(self.more_weather_air_value_so2, 0, Qt.AlignCenter)

        #  空气成分质量指数(so2图标)
        self.more_weather_air_icon_so2 = QLabel(self.widget_so2)
        self.more_weather_air_icon_so2.setObjectName(u"more_weather_air_icon_so2")
        self.verticalLayout_so2.addWidget(self.more_weather_air_icon_so2, 0, Qt.AlignCenter)

        self.horizontalLayout.addLayout(self.verticalLayout_so2)

        ##############################################################################
        #  组合框(co)
        self.widget_co = QWidget(self.page_weather_3)
        self.widget_co.setObjectName(u"widget_co")
        # self.widget_co.setGeometry(QRect(220, 120, 50, 80))
        self.verticalLayout_co = QVBoxLayout()
        self.verticalLayout_co.setObjectName(u"verticalLayout_co")
        self.verticalLayout_co.setContentsMargins(0, 0, 0, 0)

        #  空气成分质量指数(co文字描述)
        self.more_weather_air_tip_co = QLabel(self.widget_co)
        self.more_weather_air_tip_co.setObjectName(u"more_weather_air_tip_co")
        self.more_weather_air_tip_co.setFont(QFont("微软雅黑", 9))
        self.more_weather_air_tip_co.setText("CO")
        self.verticalLayout_co.addWidget(self.more_weather_air_tip_co, 0, Qt.AlignCenter)

        #  空气成分质量指数(co数值)
        self.more_weather_air_value_co = QLabel(self.widget_co)
        self.more_weather_air_value_co.setObjectName(u"more_weather_air_value_co")
        self.more_weather_air_value_co.setFont(QFont("微软雅黑", 9))
        self.verticalLayout_co.addWidget(self.more_weather_air_value_co, 0, Qt.AlignCenter)

        #  空气成分质量指数(co图标)
        self.more_weather_air_icon_co = QLabel(self.widget_co)
        self.more_weather_air_icon_co.setObjectName(u"more_weather_air_icon_co")
        self.verticalLayout_co.addWidget(self.more_weather_air_icon_co, 0, Qt.AlignCenter)

        self.horizontalLayout.addLayout(self.verticalLayout_co)

        ##############################################################################
        #  组合框(o3)
        self.widget_o3 = QWidget(self.page_weather_3)
        self.widget_o3.setObjectName(u"widget_o3")
        # self.widget_o3.setGeometry(QRect(270, 120, 50, 80))
        self.verticalLayout_o3 = QVBoxLayout()
        self.verticalLayout_o3.setObjectName(u"verticalLayout_o3")
        self.verticalLayout_o3.setContentsMargins(0, 0, 0, 0)

        #  空气成分质量指数(o3文字描述)
        self.more_weather_air_tip_o3 = QLabel(self.widget_o3)
        self.more_weather_air_tip_o3.setObjectName(u"more_weather_air_tip_o3")
        self.more_weather_air_tip_o3.setFont(QFont("微软雅黑", 9))
        self.more_weather_air_tip_o3.setText("O3")
        self.verticalLayout_o3.addWidget(self.more_weather_air_tip_o3, 0, Qt.AlignCenter)

        #  空气成分质量指数(o3数值)
        self.more_weather_air_value_o3 = QLabel(self.widget_o3)
        self.more_weather_air_value_o3.setObjectName(u"more_weather_air_value_o3")
        self.more_weather_air_value_o3.setFont(QFont("微软雅黑", 9))
        self.verticalLayout_o3.addWidget(self.more_weather_air_value_o3, 0, Qt.AlignCenter)

        #  空气成分质量指数(o3图标)
        self.more_weather_air_icon_o3 = QLabel(self.widget_o3)
        self.more_weather_air_icon_o3.setObjectName(u"more_weather_air_io3n_o3")
        self.verticalLayout_o3.addWidget(self.more_weather_air_icon_o3, 0, Qt.AlignCenter)

        self.horizontalLayout.addLayout(self.verticalLayout_o3)

        ##############################################################################
        ##############################################################################

        ##############################################################################
        ##############################################################################
        # 生活天气指数
        self.stackedWidget_life_weather = QStackedWidget(self.page_weather_3)
        self.stackedWidget_life_weather.setObjectName(u"stackedWidget_life_weather")
        self.stackedWidget_life_weather.setGeometry(QRect(520, 0, 420, 200))
        # self.stackedWidget_life_weather.setStyleSheet(u"QStackedWidget{background-color: white;}")

        self.page_life_weather_ = {}
        self.scrollArea_life_weather_ = {}
        self.scrollAreaWidgetContents_life_weather_ = {}

        self.life_weather_label_title_ = {}
        self.life_weather_label_level_ = {}
        self.life_weather_label_text_ = {}

        life_weather_x = -1
        for i in range(16):
            if life_weather_x != math.floor(i / 2):
                life_weather_x = math.floor(i / 2)

                self.page_life_weather_[life_weather_x] = QWidget()
                self.page_life_weather_[life_weather_x].setObjectName(u"page_life_weather_"[life_weather_x])
                self.stackedWidget_life_weather.addWidget(self.page_life_weather_[life_weather_x])

            # （生活天气指数）滚动界面(仅具体文本内容部分)
            self.scrollArea_life_weather_[i] = QScrollArea(self.page_life_weather_[life_weather_x])
            self.scrollArea_life_weather_[i].setObjectName(u"scrollArea_life_weather_"[i])
            self.scrollArea_life_weather_[i].setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.scrollArea_life_weather_[i].setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            # self.scrollArea.setWidgetResizable(True)
            self.scrollAreaWidgetContents_life_weather_[i] = QWidget()
            self.scrollAreaWidgetContents_life_weather_[i].setObjectName(u"scrollAreaWidgetContents_life_weather_"[i])
            self.scrollArea_life_weather_[i].setWidget(self.scrollAreaWidgetContents_life_weather_[i])
            self.scrollArea_life_weather_[i].setStyleSheet("border:none;background-color:transparent;")
            # self.scrollArea_life_weather_[i].setStyleSheet("background-color:white;")

            if i % 2 == 0:
                self.scrollArea_life_weather_[i].setGeometry(QRect(5, 50, 400, 50))

            else:
                self.scrollArea_life_weather_[i].setGeometry(QRect(5, 150, 400, 50))

            # （生活天气指数）
            self.life_weather_label_title_[i] = QLabel(self.page_life_weather_[life_weather_x])
            self.life_weather_label_title_[i].setObjectName(u"life_weather_label_title_"[i])
            self.life_weather_label_title_[i].setFont(QFont("微软雅黑", 10))
            self.life_weather_label_title_[i].setAlignment(Qt.AlignLeft)

            self.life_weather_label_level_[i] = QLabel(self.page_life_weather_[life_weather_x])
            self.life_weather_label_level_[i].setObjectName(u"life_weather_label_level_"[i])
            self.life_weather_label_level_[i].setFont(QFont("微软雅黑", 9))
            self.life_weather_label_level_[i].setAlignment(Qt.AlignLeft)

            self.life_weather_label_text_[i] = QLabel(self.scrollAreaWidgetContents_life_weather_[i])
            self.life_weather_label_text_[i].setObjectName(u"life_weather_label_text_"[i])
            self.life_weather_label_text_[i].setFont(QFont("微软雅黑", 8))
            self.life_weather_label_text_[i].setAlignment(Qt.AlignLeft)
            self.life_weather_label_text_[i].setWordWrap(True)  # 自动换行

            if i % 2 == 0:
                self.life_weather_label_title_[i].setGeometry(QRect(5, 0, 220, 20))
                self.life_weather_label_level_[i].setGeometry(QRect(5, 25, 220, 20))

            else:
                self.life_weather_label_title_[i].setGeometry(QRect(5, 100, 220, 20))
                self.life_weather_label_level_[i].setGeometry(QRect(5, 125, 220, 20))

        ##############################################################################

        #  生活天气指数（切换界面按钮）
        self.change_page_life_weather_left = QPushButton(self.page_weather_3)
        self.change_page_life_weather_left.setObjectName(u"change_page_life_weather_left")
        self.change_page_life_weather_left.setGeometry(QRect((screen_width / 2) - 70, 0, 25, 20))
        self.change_page_life_weather_left.setCursor(Qt.PointingHandCursor)

        self.change_page_life_weather_left.hide()

        self.change_page_life_weather_right = QPushButton(self.page_weather_3)
        self.change_page_life_weather_right.setObjectName(u"change_page_life_weather_right")
        self.change_page_life_weather_right.setGeometry(QRect((screen_width / 2) - 35, 0, 25, 20))
        self.change_page_life_weather_right.setCursor(Qt.PointingHandCursor)


        self.change_page_life_weather_right.hide()

        ##############################################################################
        ##############################################################################

        ##############################################################################
        ##############################################################################
        #  天气提示示表
        self.stackedWidget_tip = QStackedWidget(Form)
        self.stackedWidget_tip.setObjectName(u"stackedWidget_tip")
        self.stackedWidget_tip.setGeometry(QRect(10, 295, 620, 210))
        # self.stackedWidget_tip.setStyleSheet(u"QStackedWidget{background-color: rgb(94, 255, 183);}")

        self.page_tip_ = {}
        self.weather_warn_tip_ = {}
        self.weather_warn_icon_ = {}
        self.line_h2_ = {}

        self.scrollArea_ = {}
        self.scrollAreaWidgetContents_ = {}

        self.warn_sender_ = {}
        self.warn_pubTime_ = {}
        self.warn_title_ = {}
        self.warn_text_ = {}

        for i in range(5):
            self.page_tip_[i] = QWidget()
            self.page_tip_[i].setObjectName(u"page_tip_"[i])
            self.stackedWidget_tip.addWidget(self.page_tip_[i])

            ##############################################################################

            self.weather_warn_tip_[i] = QLabel(self.page_tip_[i])
            self.weather_warn_tip_[i].setObjectName(u"weather_warn_tip_"[i])
            self.weather_warn_tip_[i].setGeometry(QRect(5, 0, 195, 30))
            self.weather_warn_tip_[i].setFont(QFont("微软雅黑", 11))
            self.weather_warn_tip_[i].setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
            self.weather_warn_tip_[i].setText("天气预警")

            ##############################################################################

            self.weather_warn_icon_[i] = QLabel(self.page_tip_[i])
            self.weather_warn_icon_[i].setObjectName(u"weather_warn_icon_"[i])
            self.weather_warn_icon_[i].setGeometry(QRect(33, 45, 140, 120))
            self.weather_warn_icon_[i].setFont(QFont("微软雅黑", 10))
            self.weather_warn_icon_[i].setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
            self.weather_warn_icon_[i].setText("暂无数据")

            ##############################################################################

            self.line_h2_[i] = QFrame(self.page_tip_[i])
            self.line_h2_[i].setObjectName(u"line_h2_"[i])
            self.line_h2_[i].setGeometry(QRect(200, 0, 1, 210))
            self.line_h2_[i].setFrameShape(QFrame.VLine)
            self.line_h2_[i].setFrameShadow(QFrame.Sunken)

            ##############################################################################

            self.scrollArea_[i] = QScrollArea(self.page_tip_[i])
            self.scrollArea_[i].setObjectName(u"scrollArea_"[i])
            self.scrollArea_[i].setGeometry(QRect(205, 0, 415, 210))
            self.scrollArea_[i].setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.scrollArea_[i].setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            # self.scrollArea_[i].setWidgetResizable(True)
            self.scrollAreaWidgetContents_[i] = QWidget()
            self.scrollAreaWidgetContents_[i].setObjectName(u"scrollAreaWidgetContents_"[i])
            self.scrollAreaWidgetContents_[i].setGeometry(QRect(0, 0, 415, 150))
            self.scrollArea_[i].setWidget(self.scrollAreaWidgetContents_[i])
            self.scrollArea_[i].setStyleSheet("background-color:transparent;border:none;")

            #  发布单位
            self.warn_sender_[i] = QLabel(self.scrollAreaWidgetContents_[i])
            self.warn_sender_[i].setObjectName(u"warn_sender_"[i])
            self.warn_sender_[i].setGeometry(QRect(5, 0, 390, 25))
            self.warn_sender_[i].setFont(QFont("微软雅黑", 9))
            self.warn_sender_[i].setAlignment(Qt.AlignLeft)
            self.warn_sender_[i].setText("发布单位：")

            #  发布时间
            self.warn_pubTime_[i] = QLabel(self.scrollAreaWidgetContents_[i])
            self.warn_pubTime_[i].setObjectName(u"warn_pubTime_"[i])
            self.warn_pubTime_[i].setGeometry(QRect(5, 25, 390, 25))
            self.warn_pubTime_[i].setFont(QFont("微软雅黑", 9))
            self.warn_pubTime_[i].setAlignment(Qt.AlignLeft)
            self.warn_pubTime_[i].setText("发布时间：")

            #  警告标题
            self.warn_title_[i] = QLabel(self.scrollAreaWidgetContents_[i])
            self.warn_title_[i].setObjectName(u"warn_title_"[i])
            self.warn_title_[i].setGeometry(QRect(5, 50, 390, 25))
            self.warn_title_[i].setFont(QFont("微软雅黑", 9))
            self.warn_title_[i].setAlignment(Qt.AlignLeft)
            self.warn_title_[i].setText("警告内容：")
            self.warn_title_[i].setWordWrap(True)  # 自动换行

            #  警告详情
            self.warn_text_[i] = QLabel(self.scrollAreaWidgetContents_[i])
            self.warn_text_[i].setObjectName(u"warn_text_"[i])
            self.warn_text_[i].setGeometry(QRect(5, 75, 400, 25))
            self.warn_text_[i].setFont(QFont("微软雅黑", 9))
            self.warn_text_[i].setAlignment(Qt.AlignLeft)
            self.warn_text_[i].setText("警告详情：")
            self.warn_text_[i].setWordWrap(True)  # 自动换行

        # self.browser = QWebEngineView(Form)
        # self.browser.setGeometry(640, 300, 200, 200)
        # self.browser.load(QUrl('http://typhoon.nmc.cn/web.html'))
        # self.browser.show()

        self.typhoon_web_button = QPushButton(Form)
        self.typhoon_web_button.setObjectName(u"typhoon_web_button")
        self.typhoon_web_button.setGeometry(QRect(50, 475, 120, 20))
        self.typhoon_web_button.setCursor(Qt.PointingHandCursor)
        self.typhoon_web_button.setText("中央气象台台风网")
        self.typhoon_web_button.hide()
        ##############################################################################
        ##############################################################################

        self.scrollArea_earthquake_massage = QScrollArea(Form)
        self.scrollArea_earthquake_massage.setObjectName(u"scrollArea_earthquake_massage")
        self.scrollArea_earthquake_massage.setGeometry(QRect(635, 300, 320, 210))
        self.scrollArea_earthquake_massage.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea_earthquake_massage.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.scrollArea_[i].setWidgetResizable(True)
        self.scrollAreaWidgetContents_earthquake_massage = QWidget()
        self.scrollAreaWidgetContents_earthquake_massage.setObjectName(u"scrollAreaWidgetContents_earthquake_massage")
        self.scrollAreaWidgetContents_earthquake_massage.setGeometry(QRect(0, 0, 320, 420))
        self.scrollArea_earthquake_massage.setWidget(self.scrollAreaWidgetContents_earthquake_massage)
        self.scrollArea_earthquake_massage.setStyleSheet("background-color:transparent;border:none;")

        self.earthquake_massage = QLabel(self.scrollAreaWidgetContents_earthquake_massage)
        self.earthquake_massage.setObjectName(u"earthquake_massage")
        self.earthquake_massage.setGeometry(QRect(0, 30, 320, 420))
        self.earthquake_massage.setWordWrap(True)  # 自动换行

        self.earthquake_web_button = QPushButton(self.scrollAreaWidgetContents_earthquake_massage)
        self.earthquake_web_button.setObjectName(u"typhoon_web_button")
        self.earthquake_web_button.setGeometry(QRect(110, 0, 100, 20))
        self.earthquake_web_button.setCursor(Qt.PointingHandCursor)
        self.earthquake_web_button.setText("中国地震台网")

        ##############################################################################
        ##############################################################################

        #  天气提示示表（切换界面按钮）
        self.change_page_tip_left = QPushButton(Form)
        self.change_page_tip_left.setObjectName(u"change_page_tip_left")
        self.change_page_tip_left.setGeometry(QRect(15, 485, 25, 20))
        self.change_page_tip_left.setCursor(Qt.PointingHandCursor)

        self.change_page_tip_left.hide()

        self.change_page_tip_right = QPushButton(Form)
        self.change_page_tip_right.setObjectName(u"change_page_tip_left")
        self.change_page_tip_right.setGeometry(QRect(185, 485, 25, 20))
        self.change_page_tip_right.setCursor(Qt.PointingHandCursor)

        self.change_page_tip_right.hide()

        ##############################################################################
        ##############################################################################

        self.line_h5_1 = QFrame(Form)
        self.line_h5_1.setObjectName(u"line_h5_1")
        self.line_h5_1.setGeometry(QRect(630, 295, 1, 210))
        self.line_h5_1.setFrameShape(QFrame.VLine)
        self.line_h5_1.setFrameShadow(QFrame.Sunken)

        self.line_3 = QFrame(Form)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setGeometry(QRect(10, 290, screen_width / 2, 2))
        self.line_3.setFrameShape(QFrame.HLine)
        self.line_3.setFrameShadow(QFrame.Sunken)

        # 定位按钮
        self.location_ip_Button = QPushButton(Form)
        self.location_ip_Button.setObjectName(u"loaction_ip_Button")
        self.location_ip_Button.setGeometry(QRect(10, 510, 30, 30))
        # self.location_ip_Button.setStyleSheet(u"QLabel{background-color:white;}")
        self.location_ip_Button.setCursor(Qt.PointingHandCursor)
        self.location_ip_Button.setToolTip("定位")

        # 定位信息
        self.location_ip = QLabel(Form)
        self.location_ip.setObjectName(u"loaction_ip")
        self.location_ip.setGeometry(QRect(40, 510, 300, 30))
        self.location_ip.setFont(QFont("微软雅黑", 10))
        self.location_ip.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # 地图
        self.map_Button = QPushButton(Form)
        self.map_Button.setObjectName(u"loaction_ip")
        self.map_Button.setGeometry(QRect(350, 510, 30, 30))
        self.map_Button.setCursor(Qt.PointingHandCursor)
        self.map_Button.setToolTip("地图")

        # 新建一个QWebEngineView()对象
        self.qwebengine = QWebEngineView(Form)
        # 设置网页在窗口中显示的位置和大小
        self.qwebengine.setGeometry(10, 85, 950, 420)
        self.qwebengine.hide()

        # 更新时间
        self.updatetime = QLabel(Form)
        self.updatetime.setObjectName(u"updatetime")
        self.updatetime.setGeometry(QRect((screen_width / 2) - 260, 510, 260, 30))
        self.updatetime.setFont(QFont("微软雅黑", 10))
        self.updatetime.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.updatetime.setText("更新时间: 无")

        self.line_4 = QFrame(Form)
        self.line_4.setObjectName(u"line_4")
        self.line_4.setGeometry(QRect(10, 510, screen_width / 2, 1))
        self.line_4.setFrameShape(QFrame.HLine)
        self.line_4.setFrameShadow(QFrame.Sunken)

        self.closeButton.clicked.connect(Form.close)  # 窗口关闭
        self.minButton.clicked.connect(Form.showMinimized)  # 窗口最小化

        ##############################################################################
        ##############################################################################

        self.dialog = QDialog(Form)
        self.dialog.setGeometry((screen_width / 2) - 300, (screen_height / 2) - 175, 600, 350)
        self.dialog.setWindowFlag(Qt.FramelessWindowHint)
        self.dialog.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.dialog.setAttribute(Qt.WA_TranslucentBackground)
        self.dialog.setWindowModality(Qt.ApplicationModal)  # 阻塞其他窗口

        self.background_dialog = QLabel(self.dialog)
        self.background_dialog.setObjectName(u"background_dialog")
        self.background_dialog.setGeometry(QRect(0, 0, self.dialog.width(), self.dialog.height()))

        ####################################################################################################

        #  操作系统检查

        self.check_system_QLabel = QLabel(self.dialog)
        self.check_system_QLabel.setObjectName(u"check_system_QLabel")
        self.check_system_QLabel.setGeometry(QRect(10, 270, 180, 30))
        self.check_system_QLabel.setFont(QFont("微软雅黑", 9))
        self.check_system_QLabel.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        #  key获取

        self.get_api_key_button = QPushButton(self.dialog)
        self.get_api_key_button.setObjectName(u"typhoon_web_button")
        self.get_api_key_button.setGeometry(QRect(200, 80, 60, 30))
        self.get_api_key_button.setCursor(Qt.PointingHandCursor)
        self.get_api_key_button.setFont(QFont("微软雅黑", 7))
        self.get_api_key_button.setText("获取认证码")

        #  key检查

        self.check_api_key_QLabel = QLabel(self.dialog)
        self.check_api_key_QLabel.setObjectName(u"check_api_key_QLabel")
        self.check_api_key_QLabel.setGeometry(QRect(110, 20, 100, 30))
        self.check_api_key_QLabel.setFont(QFont("微软雅黑", 11))
        self.check_api_key_QLabel.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.check_api_key_QLabel.setText("认证码(Key)")

        self.api_key_QLineEdit = QLineEdit(self.dialog)
        self.api_key_QLineEdit.setObjectName(u"api_key_QLineEdit")
        self.api_key_QLineEdit.setGeometry(QRect(10, 50, 260, 20))
        self.api_key_QLineEdit.setValidator(QRegularExpressionValidator(QRegularExpression("^[0-9a-zA-Z]+$")))
        # self.api_key_QLineEdit.setClearButtonEnabled(True)

        self.check_api_key_icon = QLabel(self.dialog)
        self.check_api_key_icon.setObjectName(u"check_api_key_icon")
        self.check_api_key_icon.setGeometry(QRect(280, 50, 20, 20))
        self.check_api_key_icon.setScaledContents(True)

        # 搜索框查询方式
        self.select_way_QLabel = QLabel(self.dialog)
        self.select_way_QLabel.setObjectName(u"select_way_QLabel")
        self.select_way_QLabel.setGeometry(QRect(10, 80, 120, 30))
        self.select_way_QLabel.setFont(QFont("微软雅黑", 10))
        self.select_way_QLabel.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.select_way_QLabel.setText("搜索框查询方式")

        # 选择城市id查询数据模式，获取城市id方式（1.网络查询2.本地excel查询）
        self.select_way_ComboBox = QComboBox(self.dialog)
        self.select_way_ComboBox.setObjectName(u"select_way_ComboBox")
        self.select_way_ComboBox.setGeometry(QRect(10, 120, 140, 30))
        self.select_way_ComboBox.addItems(['在线查询', '本地查询'])

        ####################################################################################################
        ####################################################################################################

        # 主题颜色
        self.select_color_QLabel = QLabel(self.dialog)
        self.select_color_QLabel.setObjectName(u"select_color_QLabel")
        self.select_color_QLabel.setGeometry(QRect(10, 160, 120, 30))
        self.select_color_QLabel.setFont(QFont("微软雅黑", 10))
        self.select_color_QLabel.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.select_color_QLabel.setText("主题颜色")

        self.select_color_light = QPushButton(self.dialog)
        self.select_color_light.setObjectName(u"select_color_light")
        self.select_color_light.setCursor(Qt.PointingHandCursor)
        self.select_color_light.setGeometry(QRect(10, 200, 30, 30))
        self.select_color_light.setFont(QFont("微软雅黑", 11))
        self.select_color_light.setStyleSheet(u"QPushButton{background-color:rgb(170, 255, 255);}")
        self.select_color_light.setToolTip("浅色")

        self.select_color_dark = QPushButton(self.dialog)
        self.select_color_dark.setObjectName(u"select_color_dark")
        self.select_color_dark.setCursor(Qt.PointingHandCursor)
        self.select_color_dark.setGeometry(QRect(50, 200, 30, 30))
        self.select_color_dark.setFont(QFont("微软雅黑", 10))
        self.select_color_dark.setStyleSheet(u"QPushButton{background-color:rgb(60, 63, 65);}")
        self.select_color_dark.setToolTip("深色")

        self.select_color_system = QLabel(self.dialog)
        self.select_color_system.setObjectName(u"sselect_color_system")
        self.select_color_system.setGeometry(QRect(10, 240, 90, 30))
        self.select_color_system.setFont(QFont("微软雅黑", 9))
        self.select_color_system.setText("跟随系统主题")

        self.select_color_system_button = QPushButton(self.dialog)
        self.select_color_system_button.setObjectName(u"select_color_system_button")
        self.select_color_system_button.setCursor(Qt.PointingHandCursor)
        self.select_color_system_button.setGeometry(QRect(100, 245, 22, 22))
        self.select_color_system_button.setFont(QFont("微软雅黑", 10))

        ####################################################################################################
        ####################################################################################################

        # 天气生活指数
        self.select_life_weather_QLabel = QLabel(self.dialog)
        self.select_life_weather_QLabel.setObjectName(u"select_life_weather_QLabel")
        self.select_life_weather_QLabel.setGeometry(QRect(380, 20, 120, 30))
        self.select_life_weather_QLabel.setFont(QFont("微软雅黑", 10))
        self.select_life_weather_QLabel.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.select_life_weather_QLabel.setText("天气生活指数")

        self.life_weather_all_checkBox = QCheckBox(self.dialog)
        self.life_weather_all_checkBox.setObjectName(u"life_weather_all_checkBox")
        self.life_weather_all_checkBox.setGeometry(QRect(520, 25, 60, 20))
        self.life_weather_all_checkBox.setText("全选")

        self.life_weather_checkBox_ = {}

        self.life_weather_checkBox_text = ["运动", "洗车", "穿衣", "钓鱼", "紫外线", "旅游", "花粉过敏", "舒适度", "感冒",
                                           "空气污染扩散", "空调开启", "太阳镜", "化妆", "晾晒", "交通", "防晒"]

        for i in range(16):

            self.life_weather_checkBox_[i] = QCheckBox(self.dialog)
            self.life_weather_checkBox_[i].setObjectName(u"life_weather_checkBox_"[i])

            self.life_weather_checkBox_[i].setText(self.life_weather_checkBox_text[i])

            if i < 8:
                self.life_weather_checkBox_[i].setGeometry(QRect(360, 60 + i * 30, 90, 20))

            else:
                self.life_weather_checkBox_[i].setGeometry(QRect(460, 60 + (i - 8) * 30, 120, 20))

        ####################################################################################################

        # 取消和保存按钮

        self.closeButton_dialog = QPushButton(self.dialog)
        self.closeButton_dialog.setObjectName(u"closeButton_dialog")
        self.closeButton_dialog.setGeometry(QRect(200, 310, 60, 30))
        self.closeButton_dialog.setCursor(Qt.PointingHandCursor)
        self.closeButton_dialog.setText("取消保存")

        self.saveButton_dialog = QPushButton(self.dialog)
        self.saveButton_dialog.setObjectName(u"closeButton_dialog")
        self.saveButton_dialog.setGeometry(QRect(360, 310, 30, 30))
        self.saveButton_dialog.setCursor(Qt.PointingHandCursor)
        self.saveButton_dialog.setText("保存")

        self.closeButton_dialog.clicked.connect(self.dialog.hide)  # 窗口关闭
        ##############################################################################
        ##############################################################################

        # 安装事件筛选器
        self.background.installEventFilter(Form)
        self.title.installEventFilter(Form)
        self.location.installEventFilter(Form)
        self.search.installEventFilter(Form)
        self.favorites.installEventFilter(Form)
        self.lcdNumber.installEventFilter(Form)

        self.dialog.installEventFilter(Form)

        self.lcdNumber.installEventFilter(Form)
        self.now_weather_icon.installEventFilter(Form)
        self.now_weather_tip.installEventFilter(Form)
        self.now_weather_temperature.installEventFilter(Form)
        self.now_weather_detailed.installEventFilter(Form)

        self.line.installEventFilter(Form)
        self.line_h.installEventFilter(Form)
        self.line_2.installEventFilter(Form)

        self.stackedWidget_weather.installEventFilter(Form)
        self.stackedWidget_tip.installEventFilter(Form)

        self.updatetime.installEventFilter(Form)
        self.location_ip.installEventFilter(Form)

        # color_num = None
        #
        # weather_num = None
        #
        # color = ['蓝色', '黄色', '橙色', '红色']
        #
        # weather = ['台风', '暴雨', '暴雪', '寒潮', '大风', '沙尘暴', '高温', '干旱', '雷电', '冰雹', '霜冻', '大雾',
        #            '道路结冰', '霾', '雷雨大风']
        #
        # for i in range(len(color)):
        #     if str(text.json()['warning'][0]['title']).find(color[i]) != -1:
        #         color_num = i
        #
        # for i in range(len(weather)):
        #     if str(text.json()['warning'][0]['title']).find(weather[i]) != -1:
        #         weather_num = i

        # self.ui.headimage.setMask(QRegion(self.ui.headimage.rect(), QRegion.RegionType.Ellipse))
