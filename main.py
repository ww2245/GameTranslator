import os
import keyboard
import threading
import tkinter as tk
from tkinter import messagebox
from utils.logger import logger
from utils.ui_transparent import TransparentTranslator
from utils.utils_corestep import ScreenshotTranslator


class EnhancedTranslator:
    def __init__(self):
        logger.info("初始化翻译工具")
        self.root = tk.Tk()  # 主窗口
        self.root.withdraw()  # 隐藏主窗口，仅用于事件循环

        # 初始化组件

        self.game_lens = ScreenshotTranslator()

        self.translator = TransparentTranslator(self.root)

        # 注册快捷键
        self.register_hotkeys()

        # 显示初始指引
        self.show_guide_message()

    def show_guide_message(self):
        """显示操作指引"""
        guide = """翻译工具已就绪
        快捷键:\t
        Ctrl+Alt+S - 截图翻译\t
        Ctrl+Alt+Q - 退出程序\t
        操作提示:\t
        1.按下截图快捷键后，拖动鼠标选择区域\t
        2.双击翻译窗口可关闭单个结果\t
        3.双击可关闭此指导，完全关闭请按下快捷键\t"""
        self.translator.set_text(guide)

    def screenshot_translate(self):
        """执行截图翻译"""
        logger.info("用户触发截图翻译")

        def callback(start_coords, result, is_error=False):
            if is_error:
                self.translator.show_temp_message(result, is_error=True)
            elif result:
                # 创建新翻译窗口
                x, y = start_coords
                translator = TransparentTranslator(self.root, x=x, y=y)
                translator.set_text(result)

        # 在新线程中执行翻译
        threading.Thread(
            target=self.game_lens.update_translation,
            args=(callback,),
            daemon=True
        ).start()

    def register_hotkeys(self):
        """注册全局快捷键"""
        keyboard.add_hotkey('ctrl+alt+s', self.screenshot_translate)
        keyboard.add_hotkey('ctrl+alt+d', self.toggle_realtime)
        keyboard.add_hotkey('ctrl+alt+q', self.exit_app)

    def toggle_realtime(self):
        # TODO: 实时翻译待填充
        """切换实时翻译模式"""
        self.realtime_mode = not self.realtime_mode
        if self.realtime_mode:
            self.start_realtime()
        else:
            self.stop_realtime()

    def exit_app(self):
        """安全退出程序"""
        logger.info("用户请求退出程序")
        if messagebox.askokcancel("退出", "确定要退出翻译工具吗？"):
            self.root.quit()
            os._exit(0)

    def run(self):
        """运行主循环"""
        self.root.mainloop()


if __name__ == '__main__':
    app = EnhancedTranslator()
    app.run()
