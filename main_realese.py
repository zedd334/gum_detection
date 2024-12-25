# -*- coding: utf-8 -*-  # 设置文件编码为UTF-8
import csv  # 导入CSV模块
import sqlite3  # 导入SQLite3模块
import sys  # 导入系统模块
import threading  # 导入线程模块
import time  # 导入时间模块
import inspect  # 导入检查模块
import ctypes  # 导入C类型模块
import os  # 导入操作系统模块
import datetime  # 导入日期时间模块
import os  # 再次导入操作系统模块（重复）
print("PYTHONPATH:", os.environ.get("PYTHONPATH"))  # 打印PYTHONPATH环境变量
print("LD_LIBRARY_PATH:", os.environ.get("LD_LIBRARY_PATH"))  # 打印LD_LIBRARY_PATH环境变量

import cv2  # 导入OpenCV模块
import numpy as np  # 导入NumPy模块
from ctypes import cast, POINTER, byref, sizeof, c_ubyte, cdll  # 从ctypes模块导入特定函数和类型
from PyQt5.QtWidgets import (  # 从PyQt5.QtWidgets导入各种GUI组件
    QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QScrollArea, QSizePolicy, QDialog, QAction, QFileDialog, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QGroupBox, QCheckBox, QInputDialog, QFormLayout, QLineEdit,
    QDesktopWidget, QStackedWidget, QDateEdit, QMenu, QListWidget
)
from PyQt5.QtGui import QPixmap, QImage, QFont, QIcon  # 从PyQt5.QtGui导入图形相关组件
from PyQt5.QtCore import QTimer, Qt, pyqtSignal, QSize, QMetaObject, Q_ARG  # 从PyQt5.QtCore导入核心模块

# 导入相机控制模块（请确保这些模块已正确安装和导入）
from MvCameraControl_class import *
from MvErrorDefine_const import *
from CameraParams_header import *
from ultralytics import YOLO  # 导入YOLO模型
from database import create_connection  # 从database模块导入create_connection函数
import os  # 再次导入操作系统模块（重复）
from PyQt5.QtWidgets import (  # 再次从PyQt5.QtWidgets导入各种GUI组件（重复）
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QFileDialog, QCheckBox, QComboBox, QDateTimeEdit, QScrollArea
)
from PyQt5.QtCore import Qt, QDateTime  # 从PyQt5.QtCore导入核心模块（重复）

# 强制关闭线程
def Async_raise(tid, exctype):
    tid = ctypes.c_long(tid)  # 将线程ID转换为长整型
    if not inspect.isclass(exctype):  # 如果异常类型不是类
        exctype = type(exctype)  # 将异常类型转换为类
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(  # 异步抛出异常
        tid, ctypes.py_object(exctype)
    )
    if res == 0:  # 如果返回值为0，说明线程ID无效
        raise ValueError("invalid thread id")
    elif res != 1:  # 如果返回值不为1，说明设置失败
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)  # 取消设置
        raise SystemError("PyThreadState_SetAsyncExc failed")

# 停止线程
def Stop_thread(thread):
    Async_raise(thread.ident, SystemExit)  # 异步抛出SystemExit异常，停止线程

# 转为16进制字符串
def To_hex_str(num):
    chaDic = {  # 定义一个字典，将10-15转换为a-f
        10: 'a', 11: 'b', 12: 'c', 13: 'd',
        14: 'e', 15: 'f'
    }
    hexStr = ""
    if num < 0:  # 如果数字为负数
        num = num + 2 ** 32  # 转换为正数
    while num >= 16:  # 当数字大于等于16时
        digit = num % 16  # 取余数
        hexStr = chaDic.get(digit, str(digit)) + hexStr  # 将余数转换为对应的16进制字符
        num //= 16  # 整除16
    hexStr = chaDic.get(num, str(num)) + hexStr  # 将最后的数字转换为16进制字符
    return hexStr

# 是否是Mono图像
def Is_mono_data(enGvspPixelType):
    mono_pixel_types = [  # 定义Mono图像的像素类型
        PixelType_Gvsp_Mono8, PixelType_Gvsp_Mono10,
        PixelType_Gvsp_Mono10_Packed, PixelType_Gvsp_Mono12,
        PixelType_Gvsp_Mono12_Packed
    ]
    return enGvspPixelType in mono_pixel_types  # 判断输入的像素类型是否在Mono图像类型中

# 是否是彩色图像
def Is_color_data(enGvspPixelType):
    color_pixel_types = [  # 定义彩色图像的像素类型
        PixelType_Gvsp_BayerGR8, PixelType_Gvsp_BayerRG8,
        PixelType_Gvsp_BayerGB8, PixelType_Gvsp_BayerBG8,
        PixelType_Gvsp_BayerGR10, PixelType_Gvsp_BayerRG10,
        PixelType_Gvsp_BayerGB10, PixelType_Gvsp_BayerBG10,
        PixelType_Gvsp_BayerGR12, PixelType_Gvsp_BayerRG12,
        PixelType_Gvsp_BayerGB12, PixelType_Gvsp_BayerBG12,
        PixelType_Gvsp_BayerGR10_Packed,
        PixelType_Gvsp_BayerRG10_Packed,
        PixelType_Gvsp_BayerGB10_Packed,
        PixelType_Gvsp_BayerBG10_Packed,
        PixelType_Gvsp_BayerGR12_Packed,
        PixelType_Gvsp_BayerRG12_Packed,
        PixelType_Gvsp_BayerGB12_Packed,
        PixelType_Gvsp_BayerBG12_Packed,
        PixelType_Gvsp_YUV422_Packed,
        PixelType_Gvsp_YUV422_YUYV_Packed
    ]
    return enGvspPixelType in color_pixel_types  # 判断输入的像素类型是否在彩色图像类型中


# 定义一个可点击的 QLabel
class ClickableLabel(QLabel):
    """
    一个可点击的 QLabel，用于显示图片并响应点击事件。
    """
    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()

class GPIOAlarm:
    def __init__(self, green_pin=4, red_pin=17, buzzer_pin=22, close_pin=27):
        self.green_pin = green_pin
        self.red_pin = red_pin
        self.buzzer_pin = buzzer_pin
        self.close_pin = close_pin
        try:
            import RPi.GPIO as GPIO
            self.GPIO_AVAILABLE = True
            GPIO.setmode(GPIO.BCM)
            # set output mode
            GPIO.setup(self.green_pin, GPIO.OUT)
            GPIO.setup(self.red_pin, GPIO.OUT)
            GPIO.setup(self.buzzer_pin, GPIO.OUT)
            GPIO.setup(self.close_pin, GPIO.OUT)
            # initial GPIO
            GPIO.output(self.green_pin, GPIO.LOW)
            GPIO.output(self.red_pin, GPIO.HIGH)
            GPIO.output(self.buzzer_pin, GPIO.HIGH)
            GPIO.output(self.close_pin, GPIO.HIGH)
            self.GPIO = GPIO
        except ImportError:
            self.GPIO_AVAILABLE = False
            print("RPi.GPIO库未找到，GPIO报警功能将被禁用。")

    def trigger_alarm(self):
        if self.GPIO_AVAILABLE:
            self.GPIO.output(self.green_pin, self.GPIO.HIGH)
            self.GPIO.output(self.red_pin, self.GPIO.LOW)
            self.GPIO.output(self.buzzer_pin, self.GPIO.LOW)
            print("报警已触发！")
        else:
            print("GPIO不可用，无法触发报警。")

    def reset_alarm(self):
        if self.GPIO_AVAILABLE:
            self.GPIO.output(self.green_pin, self.GPIO.LOW)
            self.GPIO.output(self.red_pin, self.GPIO.HIGH)
            self.GPIO.output(self.buzzer_pin, self.GPIO.HIGH)
            print("报警已重置。")
        else:
            print("GPIO不可用，无法重置报警。")

    def cleanup(self):
        if self.GPIO_AVAILABLE:
            self.GPIO.output(self.green_pin, self.GPIO.LOW)
            self.GPIO.output(self.red_pin, self.GPIO.HIGH)
            self.GPIO.output(self.buzzer_pin, self.GPIO.HIGH)
            self.GPIO.output(self.close_pin, self.GPIO.HIGH)
            self.GPIO.cleanup()

    def close_mechine(self):
        if self.GPIO_AVAILABLE:
            self.GPIO.output(self.green_pin, self.GPIO.LOW)
            print("closing")


# 相机操作类
class CameraOperation:
    def __init__(
            self, obj_cam=None, st_device_list=None,
            n_connect_num=0, b_open_device=False,
            b_start_grabbing=False, h_thread_handle=None,
            b_thread_closed=False, st_frame_info=None,
            b_exit=False, b_save_bmp=False, b_save_jpg=False,
            buf_save_image=None, n_save_image_size=0,
            n_win_gui_id=0, frame_rate=0, exposure_time=0,
            gain=0
    ):
        self.obj_cam = obj_cam
        self.st_device_list = st_device_list
        self.n_connect_num = n_connect_num
        self.b_open_device = b_open_device
        self.b_start_grabbing = b_start_grabbing
        self.b_thread_closed = b_thread_closed
        self.st_frame_info = st_frame_info
        self.b_exit = b_exit
        self.b_save_bmp = b_save_bmp
        self.b_save_jpg = b_save_jpg
        self.buf_save_image = buf_save_image
        self.buf_convert_image = None
        self.n_save_image_size = n_save_image_size
        self.h_thread_handle = h_thread_handle
        self.frame_rate = frame_rate
        self.exposure_time = exposure_time
        self.gain = gain
        self.buf_lock = threading.Lock()  # 取图和存图的buffer锁
        self.latest_frame = None  # 最新的图像帧

    # 打开相机
    def Open_device(self):
        if not self.b_open_device:
            if self.n_connect_num < 0:
                return MV_E_CALLORDER

            # 选择设备并创建句柄
            nConnectionNum = int(self.n_connect_num)
            stDeviceList = self.st_device_list
            if nConnectionNum >= stDeviceList.nDeviceNum:
                print("连接编号超出设备列表范围！")
                return MV_E_CALLORDER
            stDeviceInfo = cast(
                stDeviceList.pDeviceInfo[nConnectionNum],
                POINTER(MV_CC_DEVICE_INFO)
            ).contents

            # 创建相机对象并打开设备
            self.obj_cam = MvCamera()
            ret = self.obj_cam.MV_CC_CreateHandle(stDeviceInfo)
            if ret != MV_OK:
                self.obj_cam.MV_CC_DestroyHandle()
                return ret

            ret = self.obj_cam.MV_CC_OpenDevice()
            if ret != MV_OK:
                return ret
            print("open device successfully!")
            self.b_open_device = True
            self.b_thread_closed = False

            # 探测网络最佳包大小(只对GigE相机有效)
            if stDeviceInfo.nTLayerType in [
                MV_GIGE_DEVICE, MV_GENTL_GIGE_DEVICE
            ]:
                nPacketSize = self.obj_cam.MV_CC_GetOptimalPacketSize()
                if int(nPacketSize) > 0:
                    ret = self.obj_cam.MV_CC_SetIntValue(
                        "GevSCPSPacketSize", nPacketSize
                    )
                    if ret != MV_OK:
                        print(
                            "warning: set packet size fail! ret[0x%x]" % ret
                        )
                else:
                    print(
                        "warning: set packet size fail! ret[0x%x]"
                        % nPacketSize
                    )
            # 设置自动增益模式为连续模式
            ret = self.obj_cam.MV_CC_SetEnumValue("GainAuto", 2)  # 2 = MV_GAIN_MODE_CONTINUOUS
            if ret != 0:
                print(f"Failed to set gain mode to continuous. Error code: {ret}")
                return ret
            print("Gain mode set to continuous.")

            # 设置曝光模式为连续曝光模式
            ret = self.obj_cam.MV_CC_SetEnumValue("ExposureAuto", 2)  # 2 = MV_EXPOSURE_MODE_CONTINUOUS
            if ret != 0:
                print(f"Failed to set exposure mode to continuous. Error code: {ret}")
                return ret
            print("Exposure mode set to continuous.")
            # 设置触发模式为off
            ret = self.obj_cam.MV_CC_SetEnumValue(
                "TriggerMode", MV_TRIGGER_MODE_OFF
            )
            if ret != MV_OK:
                print("set trigger mode fail! ret[0x%x]" % ret)
            return MV_OK

    # 开始取图
    def Start_grabbing(self):
        if not self.b_start_grabbing and self.b_open_device:
            self.b_exit = False
            ret = self.obj_cam.MV_CC_StartGrabbing()
            if ret != MV_OK:
                return ret
            self.b_start_grabbing = True
            print("start grabbing successfully!")
            try:
                self.h_thread_handle = threading.Thread(
                    target=self.Work_thread
                )
                self.h_thread_handle.start()
                self.b_thread_closed = True
            except Exception as e:
                print(f"启动取图线程失败: {e}")
                return ret
            return MV_OK

        return MV_E_CALLORDER

    # 停止取图
    def Stop_grabbing(self):
        if self.b_start_grabbing and self.b_open_device:
            # 退出线程
            if self.b_thread_closed:
                Stop_thread(self.h_thread_handle)
                self.b_thread_closed = False
            ret = self.obj_cam.MV_CC_StopGrabbing()
            if ret != MV_OK:
                return ret
            print("stop grabbing successfully!")
            self.b_start_grabbing = False
            self.b_exit = True
            return MV_OK
        else:
            return MV_E_CALLORDER

    # 关闭相机
    def Close_device(self):
        if self.b_open_device:
            # 退出线程
            if self.b_thread_closed:
                Stop_thread(self.h_thread_handle)
                self.b_thread_closed = False
            ret = self.obj_cam.MV_CC_CloseDevice()
            if ret != MV_OK:
                return ret

        # 销毁句柄
        self.obj_cam.MV_CC_DestroyHandle()
        self.b_open_device = False
        self.b_start_grabbing = False
        self.b_exit = True
        print("close device successfully!")

        return MV_OK

        # 取图线程函数

    def Work_thread(self):
        stOutFrame = MV_FRAME_OUT()
        memset(byref(stOutFrame), 0, sizeof(stOutFrame))

        while True:
            ret = self.obj_cam.MV_CC_GetImageBuffer(stOutFrame, 1000)
            if 0 == ret:
                # 拷贝图像和图像信息
                if self.buf_save_image is None or self.buf_save_image._length_ != stOutFrame.stFrameInfo.nFrameLen:
                    self.buf_save_image = (c_ubyte * stOutFrame.stFrameInfo.nFrameLen)()
                self.st_frame_info = stOutFrame.stFrameInfo
                libc = CDLL("libc.so.6")
                # print(f"Frame width: {self.st_frame_info.nWidth}")
                # print(f"Frame height: {self.st_frame_info.nHeight}")
                # print(f"Expected frame length (RGB8): {self.st_frame_info.nWidth * self.st_frame_info.nHeight * 3}")
                # print(f"Expected frame length (YUV422): {self.st_frame_info.nWidth * self.st_frame_info.nHeight * 2}")
                # print(f"Frame length: {self.st_frame_info.nFrameLen}")
                # print(f"pBufAddr: {stOutFrame.pBufAddr}")  # 打印内存地址，确认是否正确

                # 获取缓存锁
                self.buf_lock.acquire()
                # print(f"Before memcpy:")
                # print(f"  - buf_save_image length: {len(self.buf_save_image)}")
                # print(f"  - stOutFrame.pBufAddr (raw address): {stOutFrame.pBufAddr}")
                # print(f"  - Expected image length: {self.st_frame_info.nFrameLen}")
                #确保正确获取内存地址并进行内存拷贝
                try:
                    # 通过 ctypes.cast() 确保 `pBufAddr` 指向的是正确的内存地址
                    src_addr = ctypes.cast(stOutFrame.pBufAddr, ctypes.POINTER(c_ubyte))
                   # print(f"Memory copy from address {stOutFrame.pBufAddr} to buf_save_image.")
                    libc.memcpy(byref(self.buf_save_image), src_addr, self.st_frame_info.nFrameLen)
                except Exception as e:
                    print(f"Error during memory copy: {e}")

                # 打印复制后的数据长度
                # print(f"After memcpy:")
                # print(f"  - buf_save_image length: {len(self.buf_save_image)}")
                # print(f"  - Expected image length: {self.st_frame_info.nFrameLen}")

                self.buf_lock.release()

                # 转换图像数据为numpy数组
                data = np.frombuffer(self.buf_save_image, count=int(self.st_frame_info.nFrameLen), dtype=np.uint8)

                if Is_mono_data(self.st_frame_info.enPixelType):
                    image = data.reshape((self.st_frame_info.nHeight, self.st_frame_info.nWidth))
                elif Is_color_data(self.st_frame_info.enPixelType):
                    # 转换Bayer格式到RGB
                    stConvertParam = MV_CC_PIXEL_CONVERT_PARAM()
                    memset(byref(stConvertParam), 0, sizeof(stConvertParam))
                    nConvertSize = self.st_frame_info.nWidth * self.st_frame_info.nHeight * 3

                    if self.buf_convert_image is None or self.buf_convert_image._length_ != nConvertSize:
                        self.buf_convert_image = (c_ubyte * nConvertSize)()

                    stConvertParam.nWidth = self.st_frame_info.nWidth
                    stConvertParam.nHeight = self.st_frame_info.nHeight
                    stConvertParam.pSrcData = cast(data.ctypes.data, POINTER(c_ubyte))
                    stConvertParam.nSrcDataLen = self.st_frame_info.nFrameLen
                    stConvertParam.enSrcPixelType = self.st_frame_info.enPixelType
                    stConvertParam.enDstPixelType = PixelType_Gvsp_RGB8_Packed  # 目标RGB格式
                    stConvertParam.pDstBuffer = cast(self.buf_convert_image, POINTER(c_ubyte))
                    stConvertParam.nDstBufferSize = nConvertSize

                    ret = self.obj_cam.MV_CC_ConvertPixelType(stConvertParam)
                    if ret != 0:
                        print("Convert pixel type fail! ret[0x%x]" % ret)
                        continue

                    # 调试：检查转换后的数据形状和类型
                    data_convert = np.ctypeslib.as_array(self.buf_convert_image, shape=(nConvertSize,))
                    image = data_convert.reshape((self.st_frame_info.nHeight, self.st_frame_info.nWidth, 3))

                    # 调整颜色通道顺序（如果转换后颜色不对，可能是通道顺序问题）
                    # 假设原始转换结果是BGRA格式，调整为RGB格式
                    if image.shape[2] == 3:
                        image = image[..., [2, 1, 0]]  # 交换B和R通道

                else:
                    print("unsupported pixel format")
                    continue

                self.latest_frame = image

                # 释放缓存
                self.obj_cam.MV_CC_FreeImageBuffer(stOutFrame)
            else:
                print("no data, ret = " + To_hex_str(ret))
                continue

            # 是否退出
            if self.b_exit:
                if self.buf_save_image is not None:
                    del self.buf_save_image
                break
def create_connection(db_file):
    """ 创建与SQLite数据库的连接 """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(e)
    return conn
def initialize_database():
    """初始化数据库并创建表。"""
    conn = create_connection('defect_data.db')
    cursor = conn.cursor()

    # 创建 defect_records 表（如果不存在）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS defect_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            defect_types TEXT NOT NULL,
            image BLOB
        )
    """)
    conn.commit()
    conn.close()

#主窗口类
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        # 设置窗口标题和图标
        icon_path = '智能检测系统切图/背景.png'  # 替换为您的图标路径
        if not os.path.exists(icon_path):
            print(f"图标文件未找到: {icon_path}")
        self.setWindowTitle('莞造智能科技口香糖缺陷检测系统')
        self.setWindowIcon(QIcon(icon_path))

        self.resize(1920, 1080)
        self.alarm_active = False

        # 初始化计数
        self.total_defect_counts = {'缺肉': 0,  '拥堵': 0}  # 各缺陷类型的总数量

        # 数据列表，用于存储每次的缺陷记录
        self.data_records = []

        # 初始化相机操作对象
        self.camera = None

        # 初始化YOLO模型
        self.model = YOLO('best.torchscript', task='detect')  # 替换为您的模型路径

        # 添加标签映射，将模型标签映射为中文
        self.label_map = {
            '缺肉': '缺肉',
            # '起泡': '起泡',
            '拥堵': '拥堵',
        }

        # 初始化GPIO报警
        self.alarm = GPIOAlarm(green_pin=4, red_pin=17, buzzer_pin=22, close_pin=27)  # GPIO引脚根据实际连接调整

        # 初始化状态栏
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("系统已启动。")

        # 创建布局和部件
        self.initUI()

        # 启动相机
        self.start_camera()

        # 设置定时器用于更新实时视频和处理图像
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(166)  # 每166ms更新一次，即每秒约6帧

    def initUI(self):
        screen = QDesktopWidget().screenGeometry()
        self.setGeometry(screen)
        self.show()
        # 设置主窗口背景颜色
        self.setStyleSheet("background-color: rgba(226, 234, 245, 1);")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
# 顶部栏
        self.top_bar = QWidget()
        self.top_bar.setFixedHeight(60)
        top_bar_bg_path = '智能检测系统切图/顶部.png'  # 替换为您的背景图片路径
        if not os.path.exists(top_bar_bg_path):
            print(f"顶部栏背景图片未找到: {top_bar_bg_path}")
        self.top_bar.setStyleSheet(f"""
              background-image: url('{top_bar_bg_path}');
              background-repeat: no-repeat;
              background-size: cover;
          """)
        top_bar_layout = QHBoxLayout(self.top_bar)
        top_bar_layout.setContentsMargins(0, 0, 0, 0)

        # 标题
        self.title_label = QLabel('莞造智能科技口香糖缺陷检测系统')
        self.title_label.setObjectName("titleLabel")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
              color: rgba(255, 255, 255, 1);
              font-size: 36px;  /* 增大字体 */
              letter-spacing: 4px;
              font-family: '宋体';  /* 更改为宋体 */
              font-weight: bold;
          """)

        top_bar_layout.addStretch()
        top_bar_layout.addWidget(self.title_label)
        top_bar_layout.addStretch()

        # button
        button_style = """
                              QPushButton {
                                  background-color: rgba(118, 134, 230, 1);
                                  color: white;
                                  font-size: 20px;
                                  font-family: '宋体';
                                  font-weight: bold;
                                  border: none;
                                  border-radius: 19px;
                                  width: 143px;
                                  height: 38px;
                              }
                              QPushButton:hover {
                                  background-color: rgba(100, 120, 220, 1);
                              }
                          """
        manage_button = QPushButton()

        manage_icon_path = '智能检测系统切图/管理后台/Frame.png'
        manage_icon = QIcon(manage_icon_path)
        manage_button.setIcon(manage_icon)
        manage_button.setText('  管理后台')
        manage_button.setStyleSheet(button_style)

        manage_button.clicked.connect(self.open_management_interface)

        main_layout.addWidget(manage_button)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        # 退出系统按钮
        exit_button = QPushButton()
        exit_icon_path = '智能检测系统切图/退出系统/Frame.png'  # 替换为您的图标路径
        if not os.path.exists(exit_icon_path):
            print(f"退出系统图标未找到: {exit_icon_path}")
        exit_icon = QIcon(exit_icon_path)
        exit_button.setIcon(exit_icon)
        exit_button.setText('  退出系统')
        exit_button.setStyleSheet(button_style)
        exit_button.clicked.connect(self.close)

        # 最小化按钮
        minimize_button = QPushButton()
        minimize_icon_path = '智能检测系统切图/最小化/Frame.png'  # 替换为您的图标路径
        if not os.path.exists(minimize_icon_path):
            print(f"最小化图标未找到: {minimize_icon_path}")
        minimize_icon = QIcon(minimize_icon_path)
        minimize_button.setIcon(minimize_icon)
        minimize_button.setText('  最小化')
        minimize_button.setStyleSheet(button_style)
        minimize_button.clicked.connect(self.showMinimized)

        top_bar_layout.addWidget(manage_button)
        top_bar_layout.addWidget(exit_button)
        top_bar_layout.addWidget(minimize_button)
        top_bar_layout.addSpacing(40)

        main_layout.addWidget(self.top_bar)

        # 主内容区域
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(40, 0, 40, 0)
        content_layout.setSpacing(20)

        # 左侧区域
        left_layout = QVBoxLayout()
        left_layout.setSpacing(20)

        # 视频预览区域
        video_container = QWidget()
        video_container.setStyleSheet("""
              background-color: rgba(255, 255, 255, 1);
              border-radius: 24px;
          """)
        video_container_layout = QVBoxLayout(video_container)
        video_container_layout.setContentsMargins(24, 20, 24, 24)

        # 视频预览标题
        video_title_container = QWidget()
        video_title_container.setFixedHeight(50)
        video_title_bg_path = '智能检测系统切图/视频预览/Rectangle 4185.png'  # 替换为您的背景图片路径
        if not os.path.exists(video_title_bg_path):
            print(f"视频预览标题背景图片未找到: {video_title_bg_path}")
        video_title_container.setStyleSheet(f"""
              background-image: url('{video_title_bg_path}');
              background-repeat: no-repeat;
              background-size: cover;
          """)
        video_title_layout = QHBoxLayout(video_title_container)
        video_title_layout.setContentsMargins(11, 0, 0, 0)

        video_title_label = QLabel('视频预览')
        video_title_label.setStyleSheet("""
              background-image: url('智能检测系统切图/视频预览/Rectangle 4200.png');  /* 替换为您的背景图片路径 */
              color: rgba(23, 46, 197, 1);
              font-size: 24px;  /* 增大字体 */
              font-family: '宋体';  /* 更改为宋体 */
              font-weight: bold;
          """)

        video_title_layout.addWidget(video_title_label)
        video_title_layout.addStretch()

        video_container_layout.addWidget(video_title_container)

        # 视频显示区域
        self.real_time_video_label = QLabel()
        self.real_time_video_label.setAlignment(Qt.AlignCenter)
        self.real_time_video_label.setStyleSheet("""
              background-color: rgba(0, 0, 0, 1);
              border-radius: 24px;
          """)
        self.real_time_video_label.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )
        self.real_time_video_label.setMinimumSize(640, 480)  # 设置最小尺寸
        video_container_layout.addWidget(self.real_time_video_label)

        left_layout.addWidget(video_container)

        # 缺陷数量区域
        defect_counts_container = QWidget()
        defect_counts_container.setFixedHeight(250)  # 增加高度
        defect_counts_container.setStyleSheet("""
              background-color: rgba(255, 255, 255, 1);
              border-radius: 24px;
          """)
        defect_counts_layout = QHBoxLayout(defect_counts_container)
        defect_counts_layout.setContentsMargins(128, 10, 128, 10)
        defect_counts_layout.setSpacing(50)

        # 缺陷数量项样式
        defect_label_style = """
              color: rgba(0, 0, 0, 0.6);
              font-size: 36px;  /* 增大字体 */
              font-family: '宋体';  /* 更改为宋体 */
              font-weight: bold;
          """
        defect_count_style = """
              color: rgba(0, 0, 0, 1);
              font-size: 90px;  /* 增大字体 */
              font-family: '宋体';  /* 更改为宋体 */
              font-weight: bold;
          """

        # 缺肉数量
        self.defect_missing_label = QLabel('缺肉数量')
        self.defect_missing_label.setStyleSheet("""
            color: rgba(255, 0, 0, 1);  /* 将文字颜色改为红色 */
            font-size: 36px;  
            font-family: '宋体';  
            font-weight: bold;
        """)

        self.defect_missing_count = QLabel('0')
        self.defect_missing_count.setStyleSheet("""
            color: rgba(255, 0, 0, 1);  /* 将数字颜色改为红色 */
            font-size: 90px;  
            font-family: '宋体';  
            font-weight: bold;
        """)

        # 水平布局，将文字和数字水平排列
        missing_horizontal_layout = QHBoxLayout()
        missing_horizontal_layout.addWidget(self.defect_missing_label)
        missing_horizontal_layout.addWidget(self.defect_missing_count)
        missing_horizontal_layout.setSpacing(10)  # 设置文字与数字之间的间距

        missing_layout = QVBoxLayout()
        missing_layout.addLayout(missing_horizontal_layout)
        missing_layout.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        # 起泡数量
        self.defect_bubble_icon = QLabel()
        bubble_icon_path = '智能检测系统切图/起泡-icon.png'  # 替换为起泡图标路径
        if not os.path.exists(bubble_icon_path):
            print(f"起泡图标未找到: {bubble_icon_path}")
        bubble_pixmap = QPixmap(bubble_icon_path)
        if bubble_pixmap.isNull():
            print(f"加载起泡图标失败: {bubble_icon_path}")
        bubble_pixmap = bubble_pixmap.scaled(
            80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.defect_bubble_icon.setPixmap(bubble_pixmap)
        self.defect_bubble_icon.setFixedSize(120, 120)
        self.defect_bubble_icon.setAlignment(Qt.AlignCenter)
        self.defect_bubble_icon.setStyleSheet(
            "background-color: rgba(255, 249, 216, 1); border-radius: 60px;"
        )

        self.defect_bubble_label = QLabel('起泡数量')
        self.defect_bubble_label.setStyleSheet(defect_label_style)

        self.defect_bubble_count = QLabel('0')
        self.defect_bubble_count.setStyleSheet(defect_count_style)

        bubble_text_layout = QVBoxLayout()
        bubble_text_layout.setSpacing(10)
        bubble_text_layout.addWidget(
            self.defect_bubble_label, alignment=Qt.AlignCenter
        )
        bubble_text_layout.addWidget(
            self.defect_bubble_count, alignment=Qt.AlignCenter
        )

        bubble_layout = QHBoxLayout()
        bubble_layout.addWidget(self.defect_bubble_icon)
        bubble_layout.addLayout(bubble_text_layout)
        bubble_layout.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        # 拥堵数量
        self.defect_congestion_label = QLabel('拥堵次数')
        self.defect_congestion_label.setStyleSheet("""
            color: rgba(128, 0, 128, 1);  
            font-size: 36px;  
            font-family: '宋体';  
            font-weight: bold;
        """)

        self.defect_congestion_count = QLabel('0')
        self.defect_congestion_count.setStyleSheet("""
            color: rgba(128, 0, 128, 1);  
            font-size: 90px;  
            font-family: '宋体';  
            font-weight: bold;
        """)

        # 水平布局，将文字和数字水平排列
        congestion_horizontal_layout = QHBoxLayout()
        congestion_horizontal_layout.addWidget(self.defect_congestion_label)
        congestion_horizontal_layout.addWidget(self.defect_congestion_count)
        congestion_horizontal_layout.setSpacing(10)  # 设置文字与数字之间的间距

        congestion_layout = QVBoxLayout()
        congestion_layout.addLayout(congestion_horizontal_layout)
        congestion_layout.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        # 将每个缺陷布局添加到主布局
        defect_counts_layout.addLayout(missing_layout)
        # defect_counts_layout.addLayout(bubble_layout)
        defect_counts_layout.addLayout(congestion_layout)

        left_layout.addWidget(defect_counts_container)
        buttons_container = QWidget()
        buttons_container.setFixedHeight(120)
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setSpacing(20)
        buttons_layout.setContentsMargins(0, 0, 0, 0)

        # 手动报警按钮
        self.alarm_button = QPushButton()
        self.alarm_button.setText('手动报警')
        self.alarm_button.setStyleSheet("""
              QPushButton {
                  background-color: rgba(255, 92, 84, 1);
                  color: white;
                  font-size: 36px;
                  font-family: '宋体';
                  font-weight: bold;
                  border: none;
                  border-radius: 24px;
                  min-width: 320px;
                  min-height: 100px;
              }
              QPushButton:hover {
                  background-color: rgba(255, 66, 66, 1);
              }
              QPushButton:checked {
                  background-color: rgba(200, 0, 0, 1);
              }
          """)
        alarm_icon_path = '智能检测系统切图/手动报警-icon.png'
        if not os.path.exists(alarm_icon_path):
            print(f"手动报警图标未找到: {alarm_icon_path}")
        alarm_icon = QIcon(alarm_icon_path)
        self.alarm_button.setIcon(alarm_icon)
        self.alarm_button.setIconSize(QSize(40, 45))  # 可根据需要调整图标大小
        self.alarm_button.setCheckable(True)
        self.alarm_button.toggled.connect(self.handle_alarm_toggle)

        # 取消报警按钮
        self.cancel_alarm_button = QPushButton()
        self.cancel_alarm_button.setText('取消报警')
        self.cancel_alarm_button.setStyleSheet("""
              QPushButton {
                  background-color: rgba(55, 224, 114, 1);
                  color: white;
                  font-size: 36px;
                  font-family: '宋体';
                  font-weight: bold;
                  border: none;
                  border-radius: 24px;
                  min-width: 320px;
                  min-height: 100px;
              }
              QPushButton:hover {
                  background-color: rgba(50, 200, 100, 1);
              }
          """)
        cancel_icon_path = '智能检测系统切图/取消报警-icon.png'
        if not os.path.exists(cancel_icon_path):
            print(f"取消报警图标未找到: {cancel_icon_path}")
        cancel_icon = QIcon(cancel_icon_path)
        self.cancel_alarm_button.setIcon(cancel_icon)
        self.cancel_alarm_button.setIconSize(QSize(40, 45))  # 可根据需要调整图标大小
        self.cancel_alarm_button.clicked.connect(self.cancel_alarm)

        buttons_layout.addWidget(self.alarm_button)
        buttons_layout.addWidget(self.cancel_alarm_button)

        left_layout.addWidget(buttons_container)

        content_layout.addLayout(left_layout, 3)

        # 右侧区域
        right_layout = QVBoxLayout()
        right_layout.setSpacing(20)

        # 检测结果区域
        result_container = QWidget()
        result_bg_path = '智能检测系统切图/检测结果/Rectangle 4193.png'  # 替换为您的背景图片路径
        if not os.path.exists(result_bg_path):
            print(f"检测结果背景图片未找到: {result_bg_path}")
        result_container.setStyleSheet(f"""
              background-image: url('{result_bg_path}');
              background-color: rgba(255, 255, 255, 1);
              border-radius: 24px;
          """)
        result_container_layout = QVBoxLayout(result_container)
        result_container_layout.setContentsMargins(24, 20, 24, 24)

        # 检测结果标题
        result_title_container = QWidget()
        result_title_container.setFixedHeight(50)
        result_title_bg_path = '智能检测系统切图/检测结果/Rectangle 4192.png'  # 替换为您的背景图片路径
        if not os.path.exists(result_title_bg_path):
            print(f"检测结果标题背景图片未找到: {result_title_bg_path}")
        result_title_container.setStyleSheet(f"""
              background-image: url('{result_title_bg_path}');
              background-repeat: no-repeat;
              background-size: cover;
          """)
        result_title_layout = QHBoxLayout(result_title_container)
        result_title_layout.setContentsMargins(11, 0, 0, 0)

        result_title_label = QLabel('检测结果')
        result_title_label.setStyleSheet("""
              color: rgba(23, 46, 197, 1);
              font-size: 24px;  /* 增大字体 */
              font-family: '宋体';  /* 更改为宋体 */
              font-weight: bold;
          """)

        result_title_layout.addWidget(result_title_label)
        result_title_layout.addStretch()

        result_container_layout.addWidget(result_title_container)

        # 检测结果滚动区域
        self.snapshot_scroll_area = QScrollArea()
        self.snapshot_scroll_area.setWidgetResizable(True)
        self.snapshot_container = QWidget()
        self.snapshot_layout = QVBoxLayout(self.snapshot_container)
        self.snapshot_layout.setAlignment(Qt.AlignTop)
        self.snapshot_layout.setSpacing(12)
        self.snapshot_scroll_area.setWidget(self.snapshot_container)
        self.snapshot_scroll_area.setStyleSheet("""
              background-color: rgba(255, 255, 255, 1);
              border-radius: 24px;
          """)

        result_container_layout.addWidget(self.snapshot_scroll_area)

        right_layout.addWidget(result_container)

        content_layout.addLayout(right_layout, 1)

        main_layout.addLayout(content_layout)

    def get_total_defect_counts(self):
        """返回各缺陷类型的总数量字典"""
        return self.total_defect_counts

    def get_data_records(self):
        """返回缺陷记录列表"""
        return self.data_records
    def start_camera(self):
        try:
            # 使用您提供的相机初始化代码
            print("开始初始化相机...")
            deviceList = MV_CC_DEVICE_INFO_LIST()
            tlayerType = MV_GIGE_DEVICE | MV_USB_DEVICE

            ret = MvCamera.MV_CC_EnumDevices(tlayerType, deviceList)
            if ret != MV_OK:
                error_message = f"枚举设备失败! ret[0x{ret:X}]"
                print(error_message)
                self.status_bar.showMessage(error_message, 5000)
                return

            if deviceList.nDeviceNum == 0:
                error_message = "未发现设备!"
                print(error_message)
                self.status_bar.showMessage(error_message, 5000)
                return

            print(f"发现 {deviceList.nDeviceNum} 个设备!")

            # 选择第一个设备
            nConnectionNum = 0
            st_device_list = deviceList
            self.camera = CameraOperation(
                st_device_list=st_device_list, n_connect_num=nConnectionNum
            )

            ret = self.camera.Open_device()
            if ret != MV_OK:
                error_message = f"打开设备失败! ret[0x{ret:X}]"
                print(error_message)
                self.status_bar.showMessage(error_message, 5000)
                return

            ret = self.camera.Start_grabbing()
            if ret != MV_OK:
                error_message = f"开始取流失败! ret[0x{ret:X}]"
                print(error_message)
                self.status_bar.showMessage(error_message, 5000)
                return

            print("相机初始化并开始取流成功！")
            self.status_bar.showMessage("相机初始化并开始取流成功。", 5000)

        except Exception as e:
            error_message = f"相机初始化时发生错误: {str(e)}"
            print(error_message)
            self.status_bar.showMessage(error_message, 5000)

    def update_frame(self):
        try:
            frame = self.get_camera_frame()
            if frame is not None:
                # Detect defects and process the frame
                defects_detected, processed_frame = self.detect_defect(frame)
                image = self.convert_frame_to_qimage(processed_frame)
                if image is not None:
                    pixmap = QPixmap.fromImage(image)
                    label_size = self.real_time_video_label.size()
                    scaled_pixmap = pixmap.scaled(label_size, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
                    self.real_time_video_label.setPixmap(scaled_pixmap)

                # Update defect image queue if defects detected
                if defects_detected:
                    self.update_snapshot(processed_frame, defects_detected)
            else:
                # If no frame, clear the display
                self.real_time_video_label.clear()
        except Exception as e:
            error_message = f"update_frame发生错误: {str(e)}"
            print(error_message)
            self.status_bar.showMessage(error_message, 5000)

    def get_camera_frame(self):
        if (
                self.camera is not None
                and self.camera.latest_frame is not None
        ):
            frame = self.camera.latest_frame.copy()
            return frame
        else:
            return None

    def detect_defect(self, frame):
        """
        使用YOLOv8模型进行缺陷检测，返回检测到的缺陷类型列表和标注后的图像
        """
        defects = []

        # 模型推理
        results = self.model.predict(source=frame, conf=0.25, verbose=False)
        boxes = results[0].boxes.xyxy.cpu().numpy() if results[0].boxes is not None else np.array([])
        confidences = results[0].boxes.conf.cpu().numpy() if results[0].boxes is not None else np.array([])
        class_ids = results[0].boxes.cls.cpu().numpy() if results[0].boxes is not None else np.array([])
        labels = self.model.names  # 获取类别名称

        # 创建一个副本用于绘制
        processed_frame = frame.copy()

        # 如果检测到目标
        if len(boxes) > 0:
            for box, conf, cls_id in zip(boxes, confidences, class_ids):
                x_min, y_min, x_max, y_max = map(int, box)
                label = labels[int(cls_id)]
                defects.append(label)

                # 在图像上绘制框和标签，颜色改为红色
                cv2.rectangle(processed_frame, (x_min, y_min), (x_max, y_max), (0, 0, 255), 2)
                text = f"{label} {conf:.2f}"
                cv2.putText(processed_frame, text, (x_min, y_min - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        # 执行拥堵检测
        congestion_detected = False
        if len(boxes) > 0:
            detected_boxes = boxes.tolist()  # 将numpy数组转换为列表
            congestion_detected = self.is_congestion(detected_boxes, threshold=4, distance_threshold=50)
            if congestion_detected:
                defects.append('拥堵')
                # 在图像上标注拥堵信息
                cv2.putText(processed_frame, "拥堵检测到!", (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # 显示缺陷数量（即使未检测到，也显示0）
        defect_count = len(defects)
        count_text = f"Defect Count: {defect_count}"
        cv2.putText(processed_frame, count_text, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        return defects, processed_frame

    def is_congestion(self, detected_boxes, threshold=4, distance_threshold=50):
        """
        判断是否发生堵塞，堵塞条件：同一位置的口香糖超过 `threshold` 个且静止。

        detected_boxes: 形如 [(x1, y1, x2, y2),...] 的检测框列表
        threshold: 静止口香糖的数量阈值，超过该数量判断为堵塞
        distance_threshold: 口香糖之间的最大距离，超过该距离不算静止
        """
        if len(detected_boxes) < threshold:
            return False

        # 计算每个口香糖框的中心位置
        centers = [(int((box[0] + box[2]) / 2), int((box[1] + box[3]) / 2)) for box in detected_boxes]

        # 计算中心点之间的距离
        congestion_regions = []
        for i, center1 in enumerate(centers):
            congestion_region = [center1]
            for j, center2 in enumerate(centers):
                if i!= j:
                    dist = np.linalg.norm(np.array(center1) - np.array(center2))
                    if dist < distance_threshold:
                        congestion_region.append(center2)

            # 如果某个区域内有足够的口香糖数目，则认为发生了堵塞
            if len(congestion_region) >= threshold:
                congestion_regions.append(congestion_region)

        # 如果检测到任何一个区域符合堵塞条件，返回 True
        return len(congestion_regions) > 0

    def update_snapshot(self, processed_frame, defects_detected):
        """
        更新检测结果快照，并实时更新各缺陷类型的计数。
        """
        try:
            # 转换帧为 QImage 并添加到 UI
            image = self.convert_frame_to_qimage(processed_frame)
            if image is not None:
                pixmap = QPixmap.fromImage(image)

                # 创建一个容器来包含图像和信息
                snapshot_widget = QWidget()
                snapshot_layout = QVBoxLayout(snapshot_widget)
                snapshot_layout.setSpacing(5)  # 图像和文字之间的间隔

                # 定义最大宽度和高度
                max_width = 400
                max_height = 300

                # 缩放图像以适应最大尺寸，同时保持宽高比
                scaled_pixmap = pixmap.scaled(
                    max_width,
                    max_height,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                image_label = QLabel()
                image_label.setPixmap(scaled_pixmap)
                image_label.setAlignment(Qt.AlignCenter)

                # 设置边框颜色，如果检测到缺陷则为红色，否则为灰色
                border_color = "#FF0000" if defects_detected else "#CCCCCC"
                image_label.setStyleSheet(
                    f"border: 4px solid {border_color}; border-radius: 10px;"
                )
                image_label.setFixedSize(scaled_pixmap.size())  # 固定大小以避免留白

                # 添加点击放大功能
                image_label.setCursor(Qt.PointingHandCursor)
                image_label.mousePressEvent = lambda event, p=pixmap: self.show_enlarged_image(p)

                snapshot_layout.addWidget(image_label)

                # 创建一个垂直布局来放置缺陷类型和时间信息
                defect_info_layout = QVBoxLayout()
                defect_info_layout.setAlignment(Qt.AlignLeft)

                # 缺陷类型
                defect_type_text = "缺陷类型: " + ', '.join(defects_detected)
                defect_type_label = QLabel(defect_type_text)
                defect_type_label.setStyleSheet("""
                      color: rgba(0, 0, 0, 1);
                      font-size: 14px;
                      font-family: '宋体';
                  """)

                # 时间信息
                current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                defect_time_text = "时间: " + current_time
                defect_time_label = QLabel(defect_time_text)
                defect_time_label.setStyleSheet("""
                      color: rgba(0, 0, 0, 1);
                      font-size: 14px;
                      font-family: '宋体';
                  """)

                # 将缺陷类型和时间信息添加到垂直布局
                defect_info_layout.addWidget(defect_type_label)
                defect_info_layout.addWidget(defect_time_label)

                snapshot_layout.addLayout(defect_info_layout)

                # 添加到主布局
                self.snapshot_layout.addWidget(snapshot_widget)

                # 自动滚动到最底部
                self.snapshot_scroll_area.verticalScrollBar().setValue(
                    self.snapshot_scroll_area.verticalScrollBar().maximum()
                )

                # 更新各缺陷类型的计数
                for defect_type in defects_detected:
                    if defect_type in self.total_defect_counts:
                        self.total_defect_counts['缺肉'] += 1
                        self.defect_missing_count.setText(str(self.total_defect_counts['缺肉']))
                        self.trigger_alarm()
                    else:
                        self.total_defect_counts[defect_type] = 1  # 如果有新的缺陷类型

                # 在主线程中更新 UI 显示
                QMetaObject.invokeMethod(
                    self.defect_missing_count,
                    "setText",
                    Qt.QueuedConnection,
                    Q_ARG(str, str(self.total_defect_counts.get('缺肉', 0)))
                )
                QMetaObject.invokeMethod(
                    self.defect_bubble_count,
                    "setText",
                    Qt.QueuedConnection,
                    Q_ARG(str, str(self.total_defect_counts.get('起泡', 0)))
                )
                QMetaObject.invokeMethod(
                    self.defect_congestion_count,
                    "setText",
                    Qt.QueuedConnection,
                    Q_ARG(str, str(self.total_defect_counts.get('拥堵', 0)))
                )
# 记录检测结果
                record = {
                    'pixmap': pixmap if image is not None else None,
                    'timestamp': current_time,
                    'defect_types': defects_detected,
                }
                self.data_records.append(record)

                # 如果检测到缺陷，触发报警
                if defects_detected:
                    self.trigger_alarm()
                self.save_defect_to_db(defects_detected, processed_frame)
        except Exception as e:
            error_message = f"update_snapshot 发生错误: {str(e)}"
            print(error_message)
            self.status_bar.showMessage(error_message, 5000)


    def save_defect_to_db(self, defects_detected, processed_frame):
        """将检测到的缺陷保存到数据库。"""
        try:
            # 初始化数据库
            initialize_database()

            conn = create_connection('defect_data.db')
            cursor = conn.cursor()

            # 检查表是否存在（调试用）
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print("Existing tables:", tables)

            # 将图像转换为二进制数据
            success, buffer = cv2.imencode('.jpg', processed_frame)
            image_data = buffer.tobytes() if success else None

            # 准备数据
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            defect_types = ', '.join(defects_detected)

            # 插入到数据库
            cursor.execute("""
                INSERT INTO defect_records (timestamp, defect_types, image)
                VALUES (?, ?, ?)
            """, (timestamp, defect_types, image_data))
            conn.commit()
            conn.close()

        except Exception as e:
            print(f"Error saving defect to database: {str(e)}")

    def show_enlarged_image(self, pixmap):
        """
        显示放大图像的窗口，使放大的图片占屏幕大约四分之三大小，再次点击即可取消放大。
        """
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        # 获取屏幕可用大小（去除任务栏等占用的空间）
        screen_rect = app.primaryScreen().availableGeometry()
        screen_width = screen_rect.width()
        screen_height = screen_rect.height()

        # 计算图片缩放后的大小，使其占屏幕大约四分之三
        target_width = int(screen_width * 0.9)
        target_height = int(screen_height * 0.9)
        scaled_pixmap = pixmap.scaled(target_width, target_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        enlarged_window = QDialog(self)
        enlarged_window.setWindowTitle("放大图像")
        enlarged_window.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowSystemMenuHint | Qt.WindowTitleHint)

        enlarged_label = QLabel(enlarged_window)
        enlarged_label.setPixmap(scaled_pixmap)
        enlarged_label.setAlignment(Qt.AlignCenter)

        # 使图片能自适应窗口大小（保持比例）
        enlarged_label.setScaledContents(True)

        # 设置窗口大小为图片缩放后的大小
        enlarged_window.setFixedSize(scaled_pixmap.size())

        # 标记是否正在显示放大图片，用于判断点击时是显示还是关闭窗口
        is_showing = True

        def handle_mouse_press(event):
            nonlocal is_showing
            if is_showing:
                enlarged_window.close()
                is_showing = False
            else:
                enlarged_window.show()
                is_showing = True

        enlarged_label.mousePressEvent = handle_mouse_press

        enlarged_window.exec_()

    def convert_frame_to_qimage(self, frame):
        if frame.ndim == 2:
            # 灰度图像
            height, width = frame.shape
            bytesPerLine = width
            qimg = QImage(
                frame.data, width, height,
                bytesPerLine, QImage.Format_Grayscale8
            )
        elif frame.ndim == 3:
            # 彩色图像
            height, width, channel = frame.shape
            bytesPerLine = 3 * width
            # 将 BGR 格式转换为 RGB 格式
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            qimg = QImage(
                frame_rgb.data, width, height,
                bytesPerLine, QImage.Format_RGB888
            )
        else:
            return None
        return qimg

    def open_management_interface(self):
        try:
            if not hasattr(self, 'management_window') or self.management_window is None:
                self.management_window = ManagementWindow(self)  # 传递自身实例
            self.management_window.show()
        except Exception as e:
            print(f"打开管理后台时发生错误: {e}")

    def handle_alarm_toggle(self, checked):
        self.alarm_active = checked
        if self.alarm_active:
            self.alarm_button.setText('报警中...')
            # 触发报警
            self.trigger_alarm()
        else:
            self.alarm_button.setText('手动报警')
            # 取消报警
            self.reset_alarm()

    def cancel_alarm(self):
        if self.alarm_active:
            self.alarm_button.setChecked(False)
        print("报警已取消")
        # 取消报警的其他代码
        self.reset_alarm()

    def trigger_alarm(self):
        # 触发GPIO报警
        self.alarm.trigger_alarm()

    def reset_alarm(self):
        # 重置GPIO报警
        self.alarm.reset_alarm()

    def closeEvent(self, event):
        # 停止相机并清理
        self.stop_camera()
        # 清理GPIO
        self.alarm.cleanup()
        event.accept()

    def stop_camera(self):
        if self.camera is not None:
            try:
                ret = self.camera.Stop_grabbing()
                if ret != MV_OK:
                    error_message = f"停止取流失败! ret[0x{ret:X}]"
                    print(error_message)
                    self.status_bar.showMessage(error_message, 5000)
                ret = self.camera.Close_device()
                if ret != MV_OK:
                    error_message = f"关闭设备失败! ret[0x{ret:X}]"
                    print(error_message)
                    self.status_bar.showMessage(error_message, 5000)
                self.camera = None
                print("相机已停止并关闭。")
                self.status_bar.showMessage("相机已停止并关闭。", 5000)
            except Exception as e:
                error_message = f"停止相机时发生错误: {str(e)}"
                print(error_message)
                self.status_bar.showMessage(error_message, 5000)




from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QPushButton, QCheckBox, QComboBox,
    QDateTimeEdit, QLineEdit, QFileDialog, QScrollArea
)

import csv
class ManagementWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window  # 保存 MainWindow 实例引用

        # 无边框窗口
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.setWindowTitle("管理系统")
        self.resize(1200, 800)

        # 初始化数据库
        conn = create_connection('defect_data.db')
        conn.close()

        self.initUI()

    def exit_system(self):
        """关闭管理后台窗口并返回主窗口。"""
        self.close()
        self.main_window.show()  # 假设 main_window 是主窗口实例
    def open_management_interface(self):
        """打开管理后台。"""
        QMessageBox.information(self, "管理后台", "管理后台功能暂未实现！")

    def initUI(self):
        # 全局样式大幅提升字体大小和美化
        self.setStyleSheet("""
            QWidget {
                font-family: 'Microsoft YaHei';
                font-size: 20px;  /* 全局基础字号提高到20px */
                background-color: #f5f7fa;
                color: #333333;
            }
            QLabel {
                font-size: 22px; /* 标签更大字号 */
                color: #333333;
            }
            QPushButton {
                background-color: #7886e6;
                color: #ffffff;
                font-size: 20px;
                padding: 10px 20px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #667ad9;
            }
            QLineEdit, QComboBox {
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 8px;
                font-size: 20px;
                background-color: #ffffff;
            }
            QCheckBox {
                font-size: 20px;
            }
            QTableWidget {
                background-color: #ffffff;
                gridline-color: #aaaaaa; /* 网格线更明显 */
                font-size: 20px;
            }
            QHeaderView::section {
                background-color: #e2eaf5;
                font-size: 20px;
                font-weight: bold;
                border: none;
                height: 50px; /* 表头更高 */
            }
            QScrollArea {
                border: none;
            }
        """)

        main_layout = QVBoxLayout(self)
        self.showFullScreen()

        # 顶部栏
        self.top_bar = QWidget()
        self.top_bar.setFixedHeight(60)
        top_bar_bg_path = '智能检测系统切图/顶部.png'  # 替换为您的背景图片路径
        if not os.path.exists(top_bar_bg_path):
            print(f"顶部栏背景图片未找到: {top_bar_bg_path}")

        self.top_bar.setStyleSheet(f"""
            background-image: url('{top_bar_bg_path}');
            background-repeat: no-repeat;
            background-position: center;
            background-size: cover;
        """)

        top_bar_layout = QHBoxLayout(self.top_bar)
        top_bar_layout.setContentsMargins(0, 0, 0, 0)
        # 此处使用纯色背景，不改动为背景图，如需背景图请自行添加
        self.top_bar.setStyleSheet("""
            QWidget {
                background-color: #4a60d1;
            }
        """)

        # 标题（保持原有设置，可稍微加大字体）
        self.title_label = QLabel('莞造智能科技口香糖缺陷检测系统')
        self.title_label.setAlignment(Qt.AlignCenter)
        font = QFont("Microsoft YaHei", 28, QFont.Bold)  # 字号更大
        self.title_label.setFont(font)
        self.title_label.setStyleSheet("color: #ffffff;")

        top_bar_layout.addStretch()
        top_bar_layout.addWidget(self.title_label)
        top_bar_layout.addStretch()

        # 按钮样式（保持逻辑，字体已在全局QSS中变大）
        button_style = """
            QPushButton {
                background-color: #7886e6;
                color: white;
                font-size: 20px;
                font-family: 'Microsoft YaHei';
                font-weight: bold;
                border-radius: 8px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #667ad9;
            }
        """

        # 退出管理后台按钮
        manage_button = QPushButton()
        manage_button.setText('退出管理后台')
        manage_button.setStyleSheet(button_style)
        manage_button.clicked.connect(self.close)
        top_bar_layout.addWidget(manage_button)

        # 退出系统按钮
        exit_button = QPushButton()
        exit_button.setText('退出系统')
        exit_button.setStyleSheet(button_style)
        exit_button.clicked.connect(self.exit_system)
        top_bar_layout.addWidget(exit_button)

        # 最小化按钮
        minimize_button = QPushButton('最小化')
        minimize_button.setStyleSheet(button_style)
        minimize_button.clicked.connect(self.showMinimized)
        top_bar_layout.addWidget(minimize_button)

        main_layout.addWidget(self.top_bar)

        # 左侧导航菜单
        self.nav_menu = QWidget()
        nav_layout = QVBoxLayout(self.nav_menu)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(10)

        nav_button_style = """
            QPushButton {
                background-color: #e2eaf5;
                color: #333333;
                font-size: 22px;
                font-family: 'Microsoft YaHei';
                border: none;
                padding: 20px 30px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #c8dcf0;
            }
        """

        nav_buttons = [
            ("系统设置", self.show_system_settings),
            ("监测管理", self.show_monitoring_management),
            ("关于软件", self.show_about_software),
        ]

        for text, callback in nav_buttons:
            button = QPushButton(text)
            button.setStyleSheet(nav_button_style)
            button.clicked.connect(callback)
            nav_layout.addWidget(button)

        nav_layout.addStretch()

        # 内容显示区域
        self.content_area = QScrollArea()
        self.content_area.setWidgetResizable(True)
        self.content_container = QWidget()
        self.content_area.setWidget(self.content_container)
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(30, 30, 30, 30)  # 增大边距
        self.content_layout.setSpacing(20)  # 增大间距

        # 将布局分为导航和内容
        content_main_layout = QHBoxLayout()
        content_main_layout.addWidget(self.nav_menu, 1)
        content_main_layout.addWidget(self.content_area, 4)
        main_layout.addLayout(content_main_layout)

        # 显示默认部分
        self.show_system_settings()


    def clear_content_layout(self):
        """切换部分前清除内容布局。"""
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def show_system_settings(self):
        """显示系统设置界面。"""
        self.clear_content_layout()

        # 备份按钮
        backup_button = QPushButton("系统数据备份")
        backup_button.clicked.connect(self.backup_data)

        # 密码修改
        password_label = QLabel("修改管理员密码:")
        password_input = QLineEdit()
        password_input.setEchoMode(QLineEdit.Password)
        change_password_button = QPushButton("确认修改")

        # 系统日志
        logs_label = QLabel("系统日志")
        start_time = QDateTimeEdit(QDateTime.currentDateTime())
        end_time = QDateTimeEdit(QDateTime.currentDateTime())
        query_button = QPushButton("查询")
        logs_table = QTableWidget(10, 2)
        logs_table.setHorizontalHeaderLabels(["时间", "日志内容"])
        logs_table.horizontalHeader().setStretchLastSection(True)

        self.content_layout.addWidget(backup_button)
        self.content_layout.addWidget(password_label)
        self.content_layout.addWidget(password_input)
        self.content_layout.addWidget(change_password_button)
        self.content_layout.addWidget(logs_label)
        self.content_layout.addWidget(start_time)
        self.content_layout.addWidget(end_time)
        self.content_layout.addWidget(query_button)
        self.content_layout.addWidget(logs_table)

    def show_monitoring_management(self):
        """显示监测管理界面。"""
        self.clear_content_layout()

        # 缺陷类型选择
        defect_types_label = QLabel("缺陷监测类别设置:")
        defect_missing = QCheckBox("缺肉")
        defect_bubble = QCheckBox("起泡")
        defect_congestion = QCheckBox("拥堵")
        defect_missing.setChecked(True)
        defect_bubble.setChecked(True)
        defect_congestion.setChecked(True)

        # 缺陷记录
        defect_records_label = QLabel("缺陷历史记录:")
        self.defect_type_filter = QComboBox()
        self.defect_type_filter.addItems(["所有缺陷", "缺肉", "起泡", "拥堵"])
        self.start_time = QDateTimeEdit(QDateTime.currentDateTime())
        self.end_time = QDateTimeEdit(QDateTime.currentDateTime())
        query_button = QPushButton("查询")
        query_button.clicked.connect(self.load_defect_records)

        # 缺陷表格
        self.records_table = QTableWidget(0, 3)
        self.records_table.setHorizontalHeaderLabels(["时间", "缺陷类型", "缺陷图片"])
        self.records_table.horizontalHeader().setStretchLastSection(True)

        # 导出数据
        export_button = QPushButton("缺陷数据导出")
        export_button.clicked.connect(self.export_data)

        # 同步到后台
        sync_button = QPushButton("同步到后台")
        sync_button.clicked.connect(self.sync_defect_records_to_backend)

        # 布局添加
        self.content_layout.addWidget(defect_types_label)
        self.content_layout.addWidget(defect_missing)
        self.content_layout.addWidget(defect_bubble)
        self.content_layout.addWidget(defect_congestion)
        self.content_layout.addWidget(defect_records_label)
        self.content_layout.addWidget(self.defect_type_filter)
        self.content_layout.addWidget(self.start_time)
        self.content_layout.addWidget(self.end_time)
        self.content_layout.addWidget(query_button)
        self.content_layout.addWidget(self.records_table)
        self.content_layout.addWidget(export_button)
        self.content_layout.addWidget(sync_button)

    # def show_upgrade_management(self):
    #     """显示升级管理界面。"""
    #     self.clear_content_layout()
    #
    #     upgrade_button = QPushButton("选择升级包")
    #     upgrade_button.clicked.connect(self.perform_upgrade)
    #     upgrade_label = QLabel("离线升级功能")
    #
    #     self.content_layout.addWidget(upgrade_label)
    #     self.content_layout.addWidget(upgrade_button)

    def show_about_software(self):
        """显示关于软件界面。"""
        self.clear_content_layout()

        # 定义本地样式表，加大字体到28px
        label_style = "font-size: 28px; font-weight: bold;"

        about_label = QLabel("软件介绍：智能科技检测系统")
        about_label.setStyleSheet(label_style)

        version_label = QLabel("版本号：1.0.0")
        version_label.setStyleSheet(label_style)

        features_label = QLabel("版本功能：缺陷检测、管理和升级")
        features_label.setStyleSheet(label_style)

        self.content_layout.addWidget(about_label)
        self.content_layout.addWidget(version_label)
        self.content_layout.addWidget(features_label)

    def backup_data(self):
        """执行数据备份。"""
        directory = QFileDialog.getExistingDirectory(self, "选择备份目录")
        if directory:
            # 在这里实现数据备份逻辑
            QMessageBox.information(self, "备份成功", f"数据已备份到: {directory}")

    def export_data(self):
        """导出缺陷数据。"""
        file_path, _ = QFileDialog.getSaveFileName(self, "保存数据导出", "", "CSV 文件 (*.csv)")
        if file_path:
            conn = create_connection('defect_data.db')
            cursor = conn.cursor()
            cursor.execute("SELECT timestamp, defect_types, image FROM defect_records")
            records = cursor.fetchall()
            conn.close()

            # 创建导出目录
            export_dir = os.path.dirname(file_path)
            images_dir = os.path.join(export_dir, 'exported_images')
            os.makedirs(images_dir, exist_ok=True)

            # 写入 CSV 文件并导出图片
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(['时间', '缺陷类型', '图片路径'])
                for idx, (timestamp, defect_types, image_data) in enumerate(records):
                    image_filename = f"defect_image_{idx+1}.jpg"
                    image_filepath = os.path.join(images_dir, image_filename)
                    # 保存图像文件
                    if image_data:
                        image = QImage.fromData(image_data)
                        image.save(image_filepath)
                    else:
                        image_filepath = "无图像"
                    csv_writer.writerow([timestamp, defect_types, image_filepath])
            QMessageBox.information(self, "导出成功", f"数据已导出到: {file_path}")

    def perform_upgrade(self):
        """执行离线升级。"""
        file_path, _ = QFileDialog.getOpenFileName(self, "选择升级包", "", "升级包 (*.zip *.tar)")
        if file_path:
            # 实现升级逻辑
            QMessageBox.information(self, "升级", f"升级包路径: {file_path}")

    # def create_table_if_not_exists(self):
    #     conn = create_connection('defect_data.db')
    #     cursor = conn.cursor()
    #     # 创建表，如果不存在
    #     cursor.execute('''
    #         CREATE TABLE IF NOT EXISTS defect_records (
    #             id INTEGER PRIMARY KEY AUTOINCREMENT,
    #             timestamp TEXT NOT NULL,
    #             defect_types TEXT NOT NULL,
    #             image BLOB
    #         )
    #     ''')
    #     conn.commit()
    #     conn.close()
    #
    # # 在项目启动时调用
    # create_table_if_not_exists()

    def load_defect_records(self):
        """加载并显示缺陷记录。"""
        try:
            # 创建数据库连接
            conn = create_connection('defect_data.db')
            cursor = conn.cursor()

            # 获取过滤条件
            defect_type = self.defect_type_filter.currentText()
            start_time = self.start_time.dateTime().toString('yyyy-MM-dd HH:mm:ss')
            end_time = self.end_time.dateTime().toString('yyyy-MM-dd HH:mm:ss')

            # 构建查询
            query = "SELECT timestamp, defect_types, image FROM defect_records WHERE timestamp BETWEEN ? AND ?"
            params = [start_time, end_time]

            if defect_type != "所有缺陷":
                query += " AND defect_types LIKE ?"
                params.append(f"%{defect_type}%")

            # 执行查询
            cursor.execute(query, params)
            records = cursor.fetchall()

            # 填充表格
            self.records_table.setRowCount(len(records))
            for row_index, (timestamp, defect_types, image_data) in enumerate(records):
                self.records_table.setItem(row_index, 0, QTableWidgetItem(timestamp))
                self.records_table.setItem(row_index, 1, QTableWidgetItem(defect_types))

                # 显示图像
                if image_data:
                    image = QImage.fromData(image_data)
                    pixmap = QPixmap.fromImage(image)
                    image_label = QLabel()
                    image_label.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio))
                    self.records_table.setCellWidget(row_index, 2, image_label)
                else:
                    self.records_table.setItem(row_index, 2, QTableWidgetItem("无图像"))

            self.records_table.resizeColumnsToContents()
        except sqlite3.OperationalError as e:
            QMessageBox.warning(self, "加载失败", f"加载缺陷记录失败: {str(e)}")
        finally:
            if conn:
                conn.close()

    def sync_defect_records_to_backend(self):
        """同步缺陷记录到后台。"""
        try:
            # 获取记录
            conn = create_connection('defect_data.db')
            cursor = conn.cursor()
            cursor.execute("SELECT timestamp, defect_types, image FROM defect_records")
            records = cursor.fetchall()
            conn.close()

            if not records:
                QMessageBox.information(self, "无记录", "没有缺陷记录需要同步。")
                return

            # 同步记录
            for record in records:
                timestamp, defect_types, image_data = record
                try:
                    self.sync_record_to_backend(timestamp, defect_types, image_data)
                except Exception as e:
                    print(f"同步记录失败: {timestamp} - {defect_types}, 错误: {str(e)}")

            QMessageBox.information(self, "同步成功", "缺陷记录已同步到后台。")
        except Exception as e:
            QMessageBox.warning(self, "同步失败", f"同步缺陷记录失败: {str(e)}")

    def sync_record_to_backend(self, timestamp, defect_types, image_data):
        """同步单条记录到后台。"""
        try:
            import requests

            # 后台 API 地址
            url = 'http://backend.example.com/api/upload'

            # 准备数据
            data = {
                'timestamp': timestamp,
                'defect_types': defect_types,
            }
            files = {}
            if image_data:
                files['image'] = ('defect.jpg', image_data, 'image/jpeg')

            # POST 请求
            response = requests.post(url, data=data, files=files)
            response.raise_for_status()  # 如果状态码不是 200，会抛出 HTTPError
        except requests.exceptions.RequestException as e:
            print(f"同步到后台失败: {str(e)}")
            raise e


import safe
if __name__ == '__main__':
    if safe.check_license():

        app = QApplication(sys.argv)
        window = MainWindow()

        window.show()
        sys.exit(app.exec_())
