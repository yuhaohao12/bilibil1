import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pyautogui
from PIL import Image, ImageTk
import coordinate_tool

class ConfigGUI:
    def __init__(self, master, app):
        self.master = master
        self.app = app
        self.config = app.config
        
        # 设置窗口属性
        self.master.title("B站直播助手配置")
        self.master.geometry("600x500")
        self.master.resizable(True, True)
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # 创建标签页
        self.tab_control = ttk.Notebook(self.master)
        
        # 基本设置标签页
        self.basic_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.basic_tab, text='基本设置')
        self.create_basic_tab()
        
        # 关播设置标签页
        self.stop_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.stop_tab, text='关播设置')
        self.create_stop_tab()
        
        # 高级设置标签页
        self.advanced_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.advanced_tab, text='高级设置')
        self.create_advanced_tab()
        
        self.tab_control.pack(expand=1, fill="both")
        
        # 按钮区域
        button_frame = ttk.Frame(self.master)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="保存配置", command=self.save_config).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="关闭", command=self.on_close).pack(side=tk.RIGHT, padx=5)
        
        # 加载当前配置
        self.load_config_to_ui()

    def create_basic_tab(self):
        """创建基本设置标签页"""
        frame = ttk.LabelFrame(self.basic_tab, text="直播时间设置")
        frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 开播时间
        ttk.Label(frame, text="开播时间:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.start_time_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.start_time_var, width=8).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # 关播时间
        ttk.Label(frame, text="关播时间:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.end_time_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.end_time_var, width=8).grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        # 热键设置
        ttk.Label(frame, text="开播热键:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.hotkey_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.hotkey_var, width=15).grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        # 窗口标题
        ttk.Label(frame, text="窗口标题:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.window_title_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.window_title_var, width=30).grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        
        # 最小化到托盘
        self.minimize_var = tk.BooleanVar()
        ttk.Checkbutton(frame, text="最小化到托盘", variable=self.minimize_var).grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)
        
        # 测试按钮
        ttk.Button(frame, text="测试开播", command=self.test_start).grid(row=5, column=0, padx=5, pady=10)
        ttk.Button(frame, text="测试关播", command=self.test_stop).grid(row=5, column=1, padx=5, pady=10)

    def create_stop_tab(self):
        """创建关播设置标签页"""
        frame = ttk.LabelFrame(self.stop_tab, text="关播设置")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 关播方法选择
        method_frame = ttk.Frame(frame)
        method_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(method_frame, text="关播方法:").pack(side=tk.LEFT, padx=5)
        
        self.stop_method_var = tk.StringVar()
        ttk.Radiobutton(method_frame, text="图像识别", variable=self.stop_method_var, value="image").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(method_frame, text="坐标点击", variable=self.stop_method_var, value="coordinates").pack(side=tk.LEFT, padx=5)
        
        # 图像识别设置
        self.image_frame = ttk.LabelFrame(frame, text="图像识别设置")
        self.image_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(self.image_frame, text="按钮截图:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.image_path_var = tk.StringVar()
        ttk.Entry(self.image_frame, textvariable=self.image_path_var, width=30).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.image_frame, text="浏览...", command=self.browse_image).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(self.image_frame, text="截取按钮", command=self.capture_button).grid(row=0, column=3, padx=5, pady=5)
        
        # 置信度设置
        ttk.Label(self.image_frame, text="置信度:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.confidence_var = tk.DoubleVar()
        ttk.Scale(self.image_frame, from_=0.5, to=1.0, variable=self.confidence_var, 
                 orient=tk.HORIZONTAL, length=200).grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky=tk.W)
        ttk.Label(self.image_frame, textvariable=self.confidence_var).grid(row=1, column=3, padx=5, pady=5)
        
        # 坐标设置
        self.coord_frame = ttk.LabelFrame(frame, text="坐标设置")
        self.coord_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 关播坐标
        ttk.Label(self.coord_frame, text="关播按钮坐标:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.stop_x_var = tk.StringVar()
        self.stop_y_var = tk.StringVar()
        ttk.Entry(self.coord_frame, textvariable=self.stop_x_var, width=6).grid(row=0, column=1, padx=2, pady=5)
        ttk.Entry(self.coord_frame, textvariable=self.stop_y_var, width=6).grid(row=0, column=2, padx=2, pady=5)
        ttk.Button(self.coord_frame, text="获取坐标", command=lambda: self.get_coordinates("stop")).grid(row=0, column=3, padx=5, pady=5)
        
        # 关闭弹窗坐标
        ttk.Label(self.coord_frame, text="关闭弹窗坐标:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.close_x_var = tk.StringVar()
        self.close_y_var = tk.StringVar()
        ttk.Entry(self.coord_frame, textvariable=self.close_x_var, width=6).grid(row=1, column=1, padx=2, pady=5)
        ttk.Entry(self.coord_frame, textvariable=self.close_y_var, width=6).grid(row=1, column=2, padx=2, pady=5)
        ttk.Button(self.coord_frame, text="获取坐标", command=lambda: self.get_coordinates("close")).grid(row=1, column=3, padx=5, pady=5)
        
        # 重试次数
        ttk.Label(frame, text="重试次数:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.retry_var = tk.IntVar()
        ttk.Spinbox(frame, from_=1, to=10, textvariable=self.retry_var, width=5).grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

    def create_advanced_tab(self):
        """创建高级设置标签页"""
        frame = ttk.LabelFrame(self.advanced_tab, text="坐标获取工具")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 坐标获取工具说明
        desc = "坐标获取工具使用说明:\n\n" \
               "1. 点击'启动坐标工具'按钮\n" \
               "2. 将鼠标移动到目标位置\n" \
               "3. 按F9键获取当前坐标\n" \
               "4. 按ESC键退出工具\n\n" \
               "获取的坐标将自动填充到对应字段"
        ttk.Label(frame, text=desc, justify=tk.LEFT).pack(padx=10, pady=10, anchor=tk.W)
        
        # 启动工具按钮
        ttk.Button(frame, text="启动坐标工具", command=self.start_coordinate_tool).pack(pady=20)
        
        # 日志区域
        log_frame = ttk.LabelFrame(frame, text="日志")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.log_text = tk.Text(log_frame, height=8)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.log_text.config(state=tk.DISABLED)
        
        # 清空日志按钮
        ttk.Button(log_frame, text="清空日志", command=self.clear_log).pack(side=tk.RIGHT, padx=5, pady=5)

    def load_config_to_ui(self):
        """将配置加载到UI"""
        # 基本设置
        self.start_time_var.set(self.config.get('start_time', '19:00'))
        self.end_time_var.set(self.config.get('end_time', '22:00'))
        self.hotkey_var.set(self.config.get('hotkey', 'ctrl+f9'))
        self.window_title_var.set(self.config.get('window_title', '直播姬'))
        self.minimize_var.set(self.config.get('minimize_to_tray', True))
        
        # 关播设置
        self.stop_method_var.set(self.config.get('stop_method', 'image'))
        self.image_path_var.set(self.config.get('stop_button_image', 'stop_button.png'))
        self.confidence_var.set(self.config.get('confidence', 0.85))
        self.retry_var.set(self.config.get('retry_times', 3))
        
        # 坐标设置
        stop_coords = self.config.get('stop_coordinates', [100, 200])
        self.stop_x_var.set(str(stop_coords[0]))
        self.stop_y_var.set(str(stop_coords[1]))
        
        close_coords = self.config.get('close_coordinates', [300, 400])
        self.close_x_var.set(str(close_coords[0]))
        self.close_y_var.set(str(close_coords[1]))
        
        # 更新UI状态
        self.update_ui_state()

    def update_ui_state(self):
        """根据选择的关播方法更新UI状态"""
        if self.stop_method_var.get() == 'image':
            self.image_frame.pack(fill=tk.X, padx=5, pady=5)
            self.coord_frame.pack_forget()
        else:
            self.image_frame.pack_forget()
            self.coord_frame.pack(fill=tk.X, padx=5, pady=5)

    def save_config(self):
        """保存配置到文件"""
        try:
            # 基本设置
            self.config['start_time'] = self.start_time_var.get()
            self.config['end_time'] = self.end_time_var.get()
            self.config['hotkey'] = self.hotkey_var.get()
            self.config['window_title'] = self.window_title_var.get()
            self.config['minimize_to_tray'] = self.minimize_var.get()
            
            # 关播设置
            self.config['stop_method'] = self.stop_method_var.get()
            self.config['stop_button_image'] = self.image_path_var.get()
            self.config['confidence'] = self.confidence_var.get()
            self.config['retry_times'] = self.retry_var.get()
            
            # 坐标设置
            self.config['stop_coordinates'] = [
                int(self.stop_x_var.get()),
                int(self.stop_y_var.get())
            ]
            
            self.config['close_coordinates'] = [
                int(self.close_x_var.get()),
                int(self.close_y_var.get())
            ]
            
            # 保存配置
            self.app.save_config()
            messagebox.showinfo("成功", "配置已保存！")
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {str(e)}")

    def browse_image(self):
        """浏览图像文件"""
        file_path = filedialog.askopenfilename(
            title="选择按钮截图",
            filetypes=[("图像文件", "*.png;*.jpg;*.jpeg")]
        )
        if file_path:
            self.image_path_var.set(file_path)

    def capture_button(self):
        """截取按钮图像"""
        messagebox.showinfo("提示", "请将鼠标移动到目标按钮位置，按F10键截取屏幕区域")
        coordinate_tool.capture_screen_area("stop_button.png")
        self.image_path_var.set("stop_button.png")
        messagebox.showinfo("成功", "按钮截图已保存为 stop_button.png")

    def get_coordinates(self, coord_type):
        """获取坐标"""
        messagebox.showinfo("提示", f"请将鼠标移动到目标位置，按F9键获取{coord_type}坐标")
        x, y = coordinate_tool.get_coordinates()
        
        if coord_type == "stop":
            self.stop_x_var.set(str(x))
            self.stop_y_var.set(str(y))
        else:
            self.close_x_var.set(str(x))
            self.close_y_var.set(str(y))
        
        messagebox.showinfo("成功", f"已获取坐标: ({x}, {y})")

    def test_start(self):
        """测试开播功能"""
        if messagebox.askyesno("确认", "确定要测试开播吗？"):
            if self.app.start_stream():
                messagebox.showinfo("成功", "开播测试成功！")
            else:
                messagebox.showerror("失败", "开播测试失败，请查看日志")

    def test_stop(self):
        """测试关播功能"""
        if messagebox.askyesno("确认", "确定要测试关播吗？"):
            if self.app.stop_stream():
                messagebox.showinfo("成功", "关播测试成功！")
            else:
                messagebox.showerror("失败", "关播测试失败，请查看日志")

    def start_coordinate_tool(self):
        """启动坐标获取工具"""
        self.log("坐标工具已启动，按F9获取坐标，按ESC退出")
        coordinate_tool.run_coordinate_tool(self.log)

    def log(self, message):
        """记录日志"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def clear_log(self):
        """清空日志"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

    def on_close(self):
        """关闭窗口事件处理"""
        self.master.destroy()

def show_gui(app):
    """显示配置界面"""
    root = tk.Tk()
    ConfigGUI(root, app)
    root.mainloop()