# utils_ocr.py
import os
import cv2
import numpy as np
from PIL import ImageGrab, Image
import pytesseract
import paddle
from paddleocr import PaddleOCR
from utils.logger import logger

# PaddleOCR 初始化
paddle.set_device('cpu')  # CPU，如需 GPU 改为 'gpu:0'

ocr_engine = PaddleOCR(

    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False)  # 文本检测+文本识别


# 图像预处理
def preprocess_image(pil_image: Image.Image, upscale: int = 2) -> np.ndarray:
    """PIL Image → BGR numpy array，自动放大，轻度去噪"""
    img_np = np.array(pil_image)

    # 转换到 BGR
    if img_np.ndim == 2:
        img_np = cv2.cvtColor(img_np, cv2.COLOR_GRAY2BGR)
    elif img_np.shape[2] == 4:
        img_np = cv2.cvtColor(img_np, cv2.COLOR_BGRA2BGR)
    else:
        img_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

    # 放大
    h, w = img_np.shape[:2]
    img_np = cv2.resize(img_np, (w * upscale, h * upscale), interpolation=cv2.INTER_CUBIC)

    # 灰度 + 去噪（不做膨胀或二值化，保留小文字细节）
    gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, None, 20, 7, 21)
    final_img = cv2.cvtColor(denoised, cv2.COLOR_GRAY2BGR)

    return final_img


# OCR 核心函数
def ocr_image(bbox: tuple, use_paddle=True) -> str:
    """
    对指定区域截图并 OCR 识别
    bbox: (x1, y1, x2, y2)
    use_paddle: True 使用 PaddleOCR, False 使用 Tesseract
    返回识别出的文本
    """
    try:
        img = ImageGrab.grab(bbox=bbox)
        if use_paddle:
            img_np = preprocess_image(img, upscale=3)  # 小图像放大 3 倍
            result = ocr_engine.predict(img_np)
            text = ' '.join(text for item in result for text in item['rec_texts'])
        else:
            img_np = preprocess_image(img)
            text = pytesseract.image_to_string(
                img_np,
                lang='chi_sim+eng',
                config='--psm 6 --oem 3'
            )
            text = ' '.join(text.splitlines())
        if not text.strip():
            logger.warning("OCR 未识别到有效文本")
            return "OCR 未识别到有效文本"

        logger.info(f"OCR识别结果: {text}")
        return text

    except Exception:
        logger.error("OCR 识别失败", exc_info=True)
        return "OCR 识别失败"
