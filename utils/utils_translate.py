# utils_translate.py
import json
import random
import hashlib
import time
import hmac
import base64
import urllib.parse
from pathlib import Path

import requests
from utils.logger import logger

config_path = Path.cwd() / "config/api_config.json"


def load_config():
    """每次调用都重新读取 JSON 配置，保证配置实时生效"""
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def baidu_translate(text, from_lang="en", to_lang="zh", appid=None, secret=None):
    """
    调用百度翻译 API 翻译文本
    text: 待翻译文本
    from_lang: 源语言
    to_lang: 目标语言
    """

    salt = random.randint(32768, 65536)
    sign = hashlib.md5(f"{appid}{text}{salt}{secret}".encode()).hexdigest()

    try:
        response = requests.get(
            "https://fanyi-api.baidu.com/api/trans/vip/translate",
            params={
                'q': text,
                'from': from_lang,
                'to': to_lang,
                'appid': appid,
                'salt': salt,
                'sign': sign
            },
            timeout=5,
            proxies={"http": None, "https": None}  # 解决 ProxyError
        )

        response.raise_for_status()
        data = response.json()

        if "trans_result" not in data:
            logger.error(f"翻译 API 返回格式异常: {data}")
            return "[翻译错误] API返回不完整"

        dst = data["trans_result"][0]["dst"]
        logger.info(f"翻译成功: {text} → {dst}")
        return dst

    except requests.exceptions.ProxyError as e:
        logger.error(f"翻译 API 代理错误: {e}", exc_info=True)
        return "[翻译错误] 网络代理异常(ProxyError)"

    except requests.exceptions.Timeout as e:
        logger.error(f"翻译 API 超时: {e}", exc_info=True)
        return "[翻译错误] 请求超时"

    except requests.exceptions.RequestException as e:
        logger.error(f"翻译 API 请求异常: {e}", exc_info=True)
        return f"[翻译错误] 网络请求异常: {e}"

    except Exception as e:
        logger.error(f"未知翻译错误: {e}", exc_info=True)
        return f"[翻译错误] {e}"


def google_translate(text, from_lang="en", to_lang="zh", api_key=None):
    """
        调用 Google 翻译 API 翻译文本
        """
    try:
        response = requests.post(
            "https://translation.googleapis.com/language/translate/v2",
            json={
                "q": text,
                "source": from_lang,
                "target": to_lang,
                "format": "text",
                "key": api_key
            },
            timeout=5,
            proxies={"http": None, "https": None}
        )

        response.raise_for_status()
        data = response.json()

        if "data" not in data or "translations" not in data["data"]:
            logger.error(f"翻译 API 返回格式异常: {data}")
            return "[翻译错误] API返回不完整"

        dst = data["data"]["translations"][0]["translatedText"]
        logger.info(f"谷歌翻译成功: {text} → {dst}")
        return dst

    except requests.exceptions.ProxyError as e:
        logger.error(f"谷歌翻译 API 代理错误: {e}", exc_info=True)
        return "[翻译错误] 网络代理异常(ProxyError)"

    except requests.exceptions.Timeout as e:
        logger.error(f"谷歌翻译 API 超时: {e}", exc_info=True)
        return "[翻译错误] 请求超时"

    except requests.exceptions.RequestException as e:
        logger.error(f"谷歌翻译 API 请求异常: {e}", exc_info=True)
        return f"[翻译错误] 网络请求异常: {e}"

    except Exception as e:
        logger.error(f"未知翻译错误: {e}", exc_info=True)
        return f"[翻译错误] {e}"


def youdao_translate(text, from_lang="en", to_lang="zh", app_key=None, app_secret=None):
    """
        调用有道翻译 API 翻译文本
        """
    salt = str(random.randint(32768, 65536))
    sign_str = app_key + text + salt + app_secret
    sign = hashlib.md5(sign_str.encode()).hexdigest()

    try:
        response = requests.get(
            "https://openapi.youdao.com/api",
            params={
                "q": text,
                "from": from_lang,
                "to": to_lang,
                "appKey": app_key,
                "salt": salt,
                "sign": sign
            },
            timeout=5,
            proxies={"http": None, "https": None}
        )

        response.raise_for_status()
        data = response.json()

        if "translation" not in data:
            logger.error(f"有道翻译 API 返回格式异常: {data}")
            return "[翻译错误] API返回不完整"

        dst = data["translation"][0]
        logger.info(f"有道翻译成功: {text} → {dst}")
        return dst

    except requests.exceptions.ProxyError as e:
        logger.error(f"有道翻译 API 代理错误: {e}", exc_info=True)
        return "[翻译错误] 网络代理异常(ProxyError)"

    except requests.exceptions.Timeout as e:
        logger.error(f"有道翻译 API 超时: {e}", exc_info=True)
        return "[翻译错误] 请求超时"

    except requests.exceptions.RequestException as e:
        logger.error(f"有道翻译 API 请求异常: {e}", exc_info=True)
        return f"[翻译错误] 网络请求异常: {e}"

    except Exception as e:
        logger.error(f"未知翻译错误: {e}", exc_info=True)
        return f"[翻译错误] {e}"


def tencent_translate(text, from_lang="en", to_lang="zh", secret_id=None, secret_key=None):
    endpoint = "tmt.tencentcloudapi.com"
    service = "tmt"
    region = "ap-guangzhou"
    action = "TextTranslate"
    version = "2018-03-21"

    timestamp = int(time.time())
    nonce = random.randint(100000, 999999)

    params = {
        "Action": action,
        "Region": region,
        "SecretId": secret_id,
        "Timestamp": timestamp,
        "Nonce": nonce,
        "Version": version,
        "SourceText": text,
        "Source": from_lang,
        "Target": to_lang
    }

    # 简单签名示例（生产环境请用官方 SDK）
    sorted_params = "&".join(f"{k}={urllib.parse.quote(str(v), safe='')}" for k, v in sorted(params.items()))
    sign_str = f"GET{endpoint}/?{sorted_params}"
    signature = base64.b64encode(
        hmac.new(secret_key.encode(), sign_str.encode(), hashlib.sha1).digest()).decode()
    params["Signature"] = signature

    try:
        r = requests.get(f"https://{endpoint}/", params=params, timeout=5)
        r.raise_for_status()
        data = r.json()
        return data.get("Response", {}).get("TargetText", "[翻译错误] API返回不完整")
    except Exception as e:
        logger.error(f"腾讯翻译错误: {e}", exc_info=True)
        return f"[翻译错误] {e}"


def deepl_translate(text, from_lang="EN", to_lang="ZH", api_key=None):
    try:
        r = requests.post(
            "https://api-free.deepl.com/v2/translate",
            data={"text": text, "source_lang": from_lang, "target_lang": to_lang},
            headers={"Authorization": f"DeepL-Auth-Key {api_key}"},
            timeout=5
        )
        r.raise_for_status()
        data = r.json()
        return data["translations"][0]["text"]
    except Exception as e:
        logger.error(f"DeepL翻译错误: {e}", exc_info=True)
        return f"[翻译错误] {e}"


def papago_translate(text, from_lang="en", to_lang="ko", client_id=None, client_secret=None):
    try:
        headers = {
            "X-Naver-Client-Id": client_id,
            "X-Naver-Client-Secret": client_secret
        }
        r = requests.post(
            "https://openapi.naver.com/v1/papago/n2mt",
            data={"source": from_lang, "target": to_lang, "text": text},
            headers=headers,
            timeout=5
        )
        r.raise_for_status()
        return r.json()["message"]["result"]["translatedText"]
    except Exception as e:
        logger.error(f"Papago翻译错误: {e}", exc_info=True)
        return f"[翻译错误] {e}"


def translate(text, from_lang="en", to_lang="zh"):
    """
    统一翻译接口
    engine: "baidu", "google", "youdao", "tencent", "deepl", "papago"
    """
    config = load_config()
    engine = config.get("engine").lower()
    if engine == "baidu":
        baidu_cfg = config["baidu_translate"]
        return baidu_translate(text, from_lang, to_lang, baidu_cfg["appid"], baidu_cfg["secret"])
    elif engine == "google":
        google_cfg = config["google_translate"]
        return google_translate(text, from_lang, to_lang, google_cfg["api_key"])
    elif engine == "youdao":
        youdao_cfg = config["youdao_translate"]
        return youdao_translate(text, from_lang, to_lang, youdao_cfg["app_key"], youdao_cfg["app_secret"])
    elif engine == "tencent":
        tencent_cfg = config["tencent_translate"]
        return tencent_translate(text, from_lang, to_lang, tencent_cfg["secret_id"], tencent_cfg["secret_key"])
    elif engine == "deepl":
        deepl_cfg = config["deepl_translate"]
        return deepl_translate(text, from_lang, to_lang, deepl_cfg["api_key"])
    elif engine == "papago":
        papago_cfg = config["papago_translate"]
        return papago_translate(text, from_lang, to_lang, papago_cfg["client_id"], papago_cfg["client_secret"])
    else:
        logger.error(f"未支持的翻译引擎: {engine}")
        return f"[翻译错误] 未支持的翻译引擎: {engine}"
