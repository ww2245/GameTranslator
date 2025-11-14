# ui_transparent.py
import tkinter as tk
from tkinter import font as tkfont


class TransparentTranslator:
    """
    悬浮透明翻译窗口
    可以在指定坐标显示翻译文本，支持拖动和双击关闭
    """
    def __init__(self, parent, x=100, y=100, width=400):

        self.root = tk.Toplevel(parent)  # 避免阻塞主循环
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.85)
        self.root.geometry(f"+{x}+{y}")
        self.bg_color = "#333333"
        self.root.configure(bg=self.bg_color)

        self.canvas = tk.Canvas(
            self.root,
            bg=self.bg_color,
            highlightthickness=0,
            bd=0
        )
        self.canvas.pack(fill="both", expand=True)

        self.text_bg = self.canvas.create_rectangle(
            0, 0, 10, 10,
            fill=self.bg_color,
            outline=""
        )

        self.text_obj = self.canvas.create_text(
            15, 10,
            anchor="nw",
            font=("Microsoft YaHei", 11),
            fill="#FFFFFF",
            width=width - 20
        )

        self.drag_data = {"x": 0, "y": 0}
        self._setup_interaction()

    # -------------------- 交互事件 --------------------
    def _setup_interaction(self):
        # 双击关闭
        for item in [self.text_bg, self.text_obj]:
            self.canvas.tag_bind(item, "<Double-Button-1>", lambda e: self.root.destroy())

        # 拖动逻辑
        self.canvas.bind("<ButtonPress-1>", self._start_drag)
        self.canvas.bind("<B1-Motion>", self._on_drag)

        # 鼠标样式
        self.canvas.bind("<Enter>", lambda e: self.root.config(cursor="arrow"))
        self.canvas.bind("<Leave>", lambda e: self.root.config(cursor=""))

    def _start_drag(self, event):
        self.drag_data["x"] = event.x_root - self.root.winfo_x()
        self.drag_data["y"] = event.y_root - self.root.winfo_y()

    def _on_drag(self, event):
        x = event.x_root - self.drag_data["x"]
        y = event.y_root - self.drag_data["y"]
        self.root.geometry(f"+{x}+{y}")

    # -------------------- 文本显示 --------------------
    def set_text(self, text, max_width=400):
        """
        设置翻译文本并自动换行
        """
        temp_font = tkfont.Font(family="Microsoft YaHei", size=11)

        def split_text(text, max_width):
            """智能分割文本为多行"""
            lines, current_line, current_width = [], [], 0
            words = []
            for segment in text.split(' '):
                if any('\u4e00' <= c <= '\u9fff' for c in segment):
                    words.extend(list(segment))  # 中文按字符
                else:
                    words.append(segment)

            for word in words:
                word_width = temp_font.measure(word)
                if word_width > max_width:
                    for char in word:
                        char_width = temp_font.measure(char)
                        if current_width + char_width > max_width:
                            lines.append(''.join(current_line))
                            current_line = [char]
                            current_width = char_width
                        else:
                            current_line.append(char)
                            current_width += char_width
                    continue

                if current_width + word_width <= max_width:
                    current_line.append(word)
                    current_width += word_width + temp_font.measure(' ')
                else:
                    lines.append(' '.join(current_line).strip())
                    current_line = [word]
                    current_width = word_width

            if current_line:
                lines.append(' '.join(current_line).strip())
            return lines

        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        final_lines = []
        for para in paragraphs:
            final_lines.extend(split_text(para, max_width - 20))

        wrapped_text = '\n'.join(final_lines)
        line_height = temp_font.metrics("linespace")
        text_width = max(temp_font.measure(line) for line in final_lines) if final_lines else 0
        total_width = min(text_width + 40, self.root.winfo_screenwidth() - 50)
        total_height = len(final_lines) * line_height + 30

        # 更新 UI
        self.canvas.coords(self.text_bg, 0, 0, total_width, total_height)
        self.canvas.itemconfig(self.text_obj, text=wrapped_text, width=total_width - 20)
        self.canvas.config(width=total_width, height=total_height)
        self.root.geometry(f"{total_width}x{total_height}")

    def show_temp_message(self, msg, is_error=False):
        """显示临时消息"""
        self.set_text(msg)
        if is_error:
            self.canvas.itemconfig(self.text_obj, fill="red")
