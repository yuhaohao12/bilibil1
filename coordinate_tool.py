import pyautogui
import keyboard
import time
from PIL import ImageGrab

def get_coordinates():
    """获取当前鼠标坐标"""
    print("按F9获取坐标，按ESC退出...")
    while True:
        if keyboard.is_pressed('f9'):
            x, y = pyautogui.position()
            return x, y
        if keyboard.is_pressed('esc'):
            return 0, 0
        time.sleep(0.1)

def capture_screen_area(filename):
    """截取屏幕区域"""
    print("按F10开始选择区域，按ESC退出...")
    
    start_x, start_y = 0, 0
    end_x, end_y = 0, 0
    selecting = False
    
    while True:
        if keyboard.is_pressed('f10'):
            start_x, start_y = pyautogui.position()
            selecting = True
            print("开始选择区域...")
            time.sleep(0.5)  # 防止连续触发
            
        if selecting and keyboard.is_pressed('esc'):
            end_x, end_y = pyautogui.position()
            break
            
        time.sleep(0.1)
    
    # 确保坐标正确
    if start_x > end_x:
        start_x, end_x = end_x, start_x
    if start_y > end_y:
        start_y, end_y = end_y, start_y
    
    width = end_x - start_x
    height = end_y - start_y
    
    if width > 10 and height > 10:
        # 截取区域
        screenshot = ImageGrab.grab(bbox=(start_x, start_y, end_x, end_y))
        screenshot.save(filename)
        print(f"截图已保存为 {filename}")
        return True
    else:
        print("区域选择无效")
        return False

def run_coordinate_tool(log_callback=None):
    """运行坐标获取工具"""
    def log(message):
        if log_callback:
            log_callback(message)
        else:
            print(message)
    
    log("坐标工具已启动...")
    log("按F9获取当前坐标")
    log("按ESC退出工具")
    
    while True:
        if keyboard.is_pressed('f9'):
            x, y = pyautogui.position()
            log(f"当前坐标: ({x}, {y})")
            time.sleep(0.5)  # 防止连续触发
            
        if keyboard.is_pressed('esc'):
            log("坐标工具已退出")
            break
            
        time.sleep(0.1)