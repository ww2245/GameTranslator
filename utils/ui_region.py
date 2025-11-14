# ui_region.py
import tkinter as tk
from utils.logger import logger


class RegionSelector:
    """
    区域选择工具
    使用鼠标拖动选择截图区域，返回 bbox 和起始坐标
    """
    def __init__(self):
        self.root = tk.Tk()
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-alpha", 0.3)
        self.root.attributes("-topmost", True)

        self.canvas = tk.Canvas(self.root, cursor="cross")
        self.canvas.pack(fill="both", expand=True)

        self.start_x = None
        self.start_y = None
        self.rect = None
        self.bbox = None
        self.start_coords = None  # 用于返回起始坐标

        self.canvas.bind("<Button-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.root.bind("<Escape>", lambda e: self.root.destroy())

        self.root.mainloop()

    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline="red", width=2
        )

    def on_drag(self, event):
        self.canvas.coords(
            self.rect, self.start_x, self.start_y, event.x, event.y
        )

    def on_release(self, event):
        self.bbox = (
            min(self.start_x, event.x),
            min(self.start_y, event.y),
            max(self.start_x, event.x),
            max(self.start_y, event.y)
        )
        self.start_coords = (self.bbox[0], self.bbox[1])
        self.root.destroy()
        logger.info(f"选定区域: {self.bbox} (起始坐标: {self.start_coords})")

    def get_selection(self):
        """
        返回 (bbox, start_coords)
        """
        return self.bbox, self.start_coords
