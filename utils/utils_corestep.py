from utils.logger import logger
from utils.utils_ocr import setup_tesseract, ocr_image
from utils.utils_translate import translate
from utils.ui_region import RegionSelector


class ScreenshotTranslator:
    def __init__(self):
        self.last_bbox = None

    def update_translation(self, callback=None):

        """安全的截图翻译流程"""
        try:
            # 区域选择
            selector = RegionSelector()
            bbox, start_coords = selector.get_selection()
            if not selector.bbox:
                return None

            self.last_bbox = selector.bbox  # 保存最后一次成功区域

            # 初始化 Tesseract（程序启动时执行一次）
            setup_tesseract()

            # 在截图翻译流程中调用
            text = ocr_image(selector.bbox)

            logger.info(f"开始翻译文本(长度:{len(text)})")
            # 翻译
            translated_text = translate(text)
            if callback:
                # 回调同时传 start_coords 和翻译文本
                callback(start_coords, translated_text)
            logger.info(f"翻译文本({translated_text})")
            return start_coords, translated_text
        except Exception as e:
            logger.error("截图翻译流程异常", exc_info=True)
            if callback:
                callback(f"错误: {str(e)}", is_error=True)
            return None
