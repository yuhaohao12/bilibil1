import os
import sys
import time
import json
import logging
import threading
import schedule
import pyautogui
import win32gui
import win32con
from datetime import datetime
from pystray import Icon, Menu, MenuItem
from PIL import Image
import config_gui

# 配置文件路径
CONFIG_FILE = "config.json"
LOG_FILE = "auto_stream.log"

# 默认配置
DEFAULT_CONFIG = {
    "start_time": "19:00",
    "end_time": "22:00",
    "stop_method": "image",
    "stop_button_image": "stop_button.png",
    "stop_coordinates": [100, 200],
    "close_coordinates": [300, 400],
    "confidence": 0.85,
    "retry_times": 3,
    "window_title": "直播姬",
    "hotkey": "ctrl+f9",
    "minimize_to_tray": True
}

class BilibiliAutoStream:
    def __init__(self):
        self.config = self.load_config()
        self.tray_icon = None
        self.running = True
        self.tray_thread = None
        self.schedule_thread = None
        self.setup_logging()
        
    def setup_logging(self):
        """配置日志系统"""
        logging.basicConfig(
            filename=LOG_FILE,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filemode='a'
        )
        # 同时输出到控制台
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console.setFormatter(formatter)
        logging.getLogger().addHandler(console)

    def load_config(self):
        """加载配置文件"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except:
                logging.error("配置文件损坏，使用默认配置")
                return DEFAULT_CONFIG
        return DEFAULT_CONFIG

    def save_config(self):
        """保存配置文件"""
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=4)
        logging.info("配置文件已更新")

    def set_focus_to_window(self):
        """激活直播姬窗口"""
        try:
            hwnd = win32gui.FindWindow(None, self.config['window_title'])
            if hwnd:
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(hwnd)
                time.sleep(0.5)  # 等待窗口激活
                return True
        except:
            logging.warning("未找到直播姬窗口")
        return False

    def start_stream(self):
        """执行开播操作"""
        if not self.set_focus_to_window():
            return False
            
        logging.info("执行开播操作")
        try:
            # 发送开播快捷键
            hotkey = self.config['hotkey'].split('+')
            pyautogui.hotkey(*hotkey)
            time.sleep(5)  # 等待开播完成
            logging.info("开播成功")
            return True
        except Exception as e:
            logging.error(f"开播失败: {str(e)}")
            return False

    def stop_stream(self):
        """执行关播操作"""
        if not self.set_focus_to_window():
            return False
            
        logging.info("执行关播操作")
        
        # 图像识别关播
        if self.config['stop_method'] == 'image':
            image_path = self.config['stop_button_image']
            for _ in range(self.config['retry_times']):
                try:
                    location = pyautogui.locateCenterOnScreen(
                        image_path,
                        confidence=self.config['confidence']
                    )
                    if location:
                        pyautogui.click(location)
                        time.sleep(2)  # 等待弹窗出现
                        self.close_settlement()
                        logging.info("关播成功 (图像识别)")
                        return True
                except Exception as e:
                    logging.warning(f"图像识别失败: {str(e)}")
                time.sleep(1)
        
        # 坐标点击关播
        else:
            try:
                x, y = self.config['stop_coordinates']
                pyautogui.click(x, y)
                time.sleep(2)
                self.close_settlement()
                logging.info("关播成功 (坐标点击)")
                return True
            except Exception as e:
                logging.error(f"坐标点击失败: {str(e)}")
        
        logging.error("关播失败")
        return False

    def close_settlement(self):
        """关闭结算弹窗"""
        try:
            x, y = self.config['close_coordinates']
            pyautogui.click(x, y)
            logging.info("已关闭结算弹窗")
            time.sleep(1)
        except Exception as e:
            logging.error(f"关闭结算弹窗失败: {str(e)}")

    def run_schedule(self):
        """运行定时任务"""
        schedule.every().day.at(self.config['start_time']).do(self.start_stream)
        schedule.every().day.at(self.config['end_time']).do(self.stop_stream)
        
        logging.info(f"定时任务已启动: 开播 {self.config['start_time']}, 关播 {self.config['end_time']}")
        
        while self.running:
            schedule.run_pending()
            time.sleep(30)  # 每30秒检查一次

    def open_config_gui(self):
        """打开配置界面"""
        config_gui.show_gui(self)

    def start_tray_icon(self):
        """创建系统托盘图标"""
        # 创建菜单
        menu = Menu(
            MenuItem('打开配置', self.open_config_gui),
            MenuItem('退出', lambda: self.exit_app())
        )
        
        # 加载图标
        image = Image.open("images/tray_icon.ico") if os.path.exists("images/tray_icon.ico") else Image.new('RGB', (64, 64), 'white')
        
        # 创建托盘图标
        self.tray_icon = Icon("B站直播助手", image, "B站直播助手", menu)
        self.tray_icon.run()

    def exit_app(self):
        """退出应用程序"""
        self.running = False
        logging.info("程序正在退出...")
        if self.tray_icon:
            self.tray_icon.stop()
        os._exit(0)

    def run(self):
        """启动主程序"""
        logging.info("程序启动")
        
        # 启动定时任务线程
        self.schedule_thread = threading.Thread(target=self.run_schedule, daemon=True)
        self.schedule_thread.start()
        
        # 如果配置为最小化到托盘，则启动托盘图标
        if self.config.get('minimize_to_tray', True):
            self.tray_thread = threading.Thread(target=self.start_tray_icon, daemon=True)
            self.tray_thread.start()
        else:
            # 否则打开配置界面
            self.open_config_gui()
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.exit_app()

if __name__ == "__main__":
    # 创建必要目录
    os.makedirs("images", exist_ok=True)
    
    app = BilibiliAutoStream()
    app.run()