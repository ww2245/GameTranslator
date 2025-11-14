# utils_ocr.py
import os
from PIL import ImageGrab
import pytesseract
from utils.logger import logger


def setup_tesseract(tesseract_dir='tools/Tesseract-OCR'):
    """
    设置 tesseract 路径
    tesseract_dir: 相对项目根目录的 Tesseract-OCR 文件夹路径
    """
    # 获取项目根目录，而不是当前文件目录
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tesseract_path = os.path.join(base_dir, tesseract_dir, 'tesseract.exe')

    if not os.path.exists(tesseract_path):
        raise FileNotFoundError(
            f"Tesseract 未找到，请确保路径存在: {tesseract_path}\n"
            "解决方案：\n"
            "1. 将 Tesseract-OCR 文件夹放在项目 tools 目录下\n"
            "2. 或修改 tesseract_dir 变量指向正确位置"
        )

    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
    logger.info(f"Tesseract 设置成功: {tesseract_path}")


def ocr_image(bbox):
    """
    对指定区域截图并 OCR 识别
    bbox: (x1, y1, x2, y2)
    返回识别出的文本（中英文混合）
    """
    try:
        if not hasattr(pytesseract, 'get_tesseract_version'):
            raise RuntimeError("Tesseract 未正确安装")

        img = ImageGrab.grab(bbox=bbox)
        text = pytesseract.image_to_string(
            img,
            lang='chi_sim+eng',
            config='--psm 6 --oem 3'
        )
        text = ' '.join(text.splitlines())
        if not text.strip():
            logger.warning("OCR 未识别到有效文本")
            return "OCR 未识别到有效文本"

        logger.debug(f"OCR识别结果: {text}")
        return text

    except Exception as e:
        logger.error("OCR 识别失败", exc_info=True)
        return "OCR 识别失败"
