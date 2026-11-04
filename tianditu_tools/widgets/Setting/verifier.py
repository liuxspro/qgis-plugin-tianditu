import json

from qgis.core import QgsNetworkAccessManager
from qgis.PyQt.QtCore import QObject, QTimer, pyqtSignal

from ...compat import HttpStatusCodeAttribute, NoError
from ...utils import HEADER, make_request, tianditu_map_url

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
TIMEOUT_MS = 12000


class KeyVerifier(QObject):
    """通过请求一张瓦片来校验天地图 key 是否可用"""

    started = pyqtSignal()
    verified = pyqtSignal(str)
    failed = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._reply = None
        self._key = ""
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._on_timeout)

    @property
    def is_busy(self) -> bool:
        return self._reply is not None

    def verify(self, key: str) -> bool:
        """发起校验，已有请求在进行时返回 False"""
        if self.is_busy:
            return False
        url = tianditu_map_url("vec", key, "t0").format(x=0, y=0, z=0)
        request = make_request(url, HEADER.get("Referer"))
        reply = QgsNetworkAccessManager.instance().get(request)
        self._reply = reply
        self._key = key
        reply.finished.connect(lambda: self._on_finished(reply))
        self._timer.start(TIMEOUT_MS)
        self.started.emit()
        return True

    def abort(self):
        """取消正在进行的校验"""
        reply = self._detach()
        if reply is None:
            return
        reply.abort()
        reply.deleteLater()

    def _detach(self):
        """断开当前请求的回调并清空状态，返回被断开的 reply"""
        reply = self._reply
        self._release()
        if reply is None:
            return None
        try:
            reply.finished.disconnect()
        except (TypeError, RuntimeError):
            pass
        return reply

    def _release(self):
        self._timer.stop()
        self._reply = None
        self._key = ""

    def _on_timeout(self):
        reply = self._detach()
        if reply is None:
            return
        reply.abort()
        reply.deleteLater()
        self.failed.emit("验证超时，请检查网络后重试")
        self.finished.emit()

    def _on_finished(self, reply):
        # 超时或取消后 self._reply 已被清空，回调直接忽略
        if reply is not self._reply:
            reply.deleteLater()
            return

        key = self._key
        self._release()
        status_code = reply.attribute(HttpStatusCodeAttribute)
        if reply.error() == NoError:
            if bytes(reply.readAll()).startswith(PNG_SIGNATURE):
                self.verified.emit(key)
            else:
                self.failed.emit("验证失败：服务器返回了异常内容，请稍后重试")
        elif status_code == 403:
            self.failed.emit(self._parse_error(reply))
        elif status_code == 418:
            self.failed.emit("验证失败：疑似攻击，请稍后重试")
        else:
            self.failed.emit(f"验证失败：{reply.errorString() or '未知错误'}")
        reply.deleteLater()
        self.finished.emit()

    @staticmethod
    def _parse_error(reply) -> str:
        """解析天地图返回的错误信息，例如非法 Key、域名不匹配等"""
        raw = bytes(reply.readAll())
        try:
            data = json.loads(raw.decode("utf-8", "ignore"))
        except json.JSONDecodeError:
            return "验证失败：非法 Key 或域名不匹配"
        message = data.get("msg") or "未知错误"
        resolve = data.get("resolve") or ""
        if resolve:
            return f"验证失败：{message}（{resolve}）"
        return f"验证失败：{message}"
