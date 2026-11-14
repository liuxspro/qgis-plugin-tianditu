"""Google Earth 风格的历史影像档期时间轴。"""

import datetime

from qgis.PyQt import QtCore, QtGui, QtWidgets
from qgis.PyQt.QtCore import QDate

from ...compat import (
    AlignCenter,
    AlignVCenter,
    Antialiasing,
    KeyEnd,
    KeyHome,
    KeyLeft,
    KeyRight,
    LeftButton,
    NoPen,
    StrongFocus,
)

HIT_RADIUS = 9.0
LABEL_GAP = 26.0
DATE_FORMATS = ("yyyyMMdd", "yyyy-MM-dd", "yyyyMM", "yyyy-MM", "yyyy")


class TimelineBar(QtWidgets.QWidget):
    """按日期线性分布档期圆点，切换档期时发出 dateChanged 信号

    set_dates 接受一组档期，每项可以是 QDate / datetime.date / 字符串日期，
    也可以是带 date(st) 与 reso、name 的 dict；dict 会原样通过信号回传。
    """

    dateChanged = QtCore.pyqtSignal(object)

    HEIGHT = 48
    DOT_Y = 18.0
    LABEL_BASELINE = 38.0
    ACCENT_COLOR = QtGui.QColor("#1a73e8")

    def __init__(self, parent=None):
        super().__init__(parent)
        self._items = []
        self._current = -1
        self._hover = -1
        self.setMouseTracking(True)
        self.setFocusPolicy(StrongFocus)
        self.setFixedHeight(self.HEIGHT)

    # ---------- 数据接口 ----------

    def set_dates(self, items):
        """更新档期，尽量保持当前选中的日期"""
        previous = self.current_date()
        self._items = self._normalize(items)
        self._hover = -1
        self._restore_selection(previous)
        self.update()

    def clear(self):
        self._items = []
        self._current = -1
        self._hover = -1
        self.update()

    def count(self):
        return len(self._items)

    def current_date(self):
        if 0 <= self._current < len(self._items):
            return self._items[self._current]["date"]
        return None

    def current_item(self):
        if 0 <= self._current < len(self._items):
            return self._items[self._current]["raw"]
        return None

    def current_index(self):
        return self._current

    def step(self, delta):
        """切到上一档 / 下一档，返回是否发生了切换"""
        target = self._current + delta
        if not 0 <= target < len(self._items):
            return False
        self.set_current_index(target)
        return True

    def set_current_index(self, index, emit=True):
        if not 0 <= index < len(self._items):
            return
        if index == self._current:
            return
        self._current = index
        self.update()
        if emit:
            self.dateChanged.emit(self._items[index]["raw"])

    # ---------- 数据整理 ----------

    def _normalize(self, items):
        normalized = []
        for item in items or []:
            date = _to_qdate(_item_value(item, "date"))
            if date is None or not date.isValid():
                continue
            normalized.append(
                {
                    "date": date,
                    "date_str": date.toString("yyyy-MM"),
                    "reso": _item_value(item, "reso"),
                    "name": _item_value(item, "name"),
                    "raw": item,
                }
            )
        normalized.sort(key=lambda entry: entry["date"])
        return normalized

    def _restore_selection(self, previous):
        if not self._items:
            self._current = -1
            return
        if previous is None:
            if not 0 <= self._current < len(self._items):
                self._current = len(self._items) - 1
            return
        for index, item in enumerate(self._items):
            if item["date"] == previous:
                self._current = index
                return
        earlier = [i for i, item in enumerate(self._items) if item["date"] < previous]
        self._current = earlier[-1] if earlier else 0

    # ---------- 绘制 ----------

    def paintEvent(self, event):  # pylint: disable=unused-argument
        painter = QtGui.QPainter(self)
        painter.setRenderHint(Antialiasing, True)
        rect = QtCore.QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        radius = rect.height() / 2
        painter.setPen(NoPen)
        painter.setBrush(self._pill_color())
        painter.drawRoundedRect(rect, radius, radius)

        if not self._items:
            painter.setPen(self._muted_text_color())
            painter.drawText(rect, AlignCenter | AlignVCenter, "暂无历史影像档期")
            painter.end()
            return

        points = self._layout_points()
        self._draw_dots(painter, points)
        self._draw_labels(painter, points)
        painter.end()

    def _draw_dots(self, painter, points):
        for index, x in enumerate(points):
            if index == self._current:
                radius, color = 6.0, self.ACCENT_COLOR
            elif index == self._hover:
                radius, color = 4.5, _with_alpha(self.ACCENT_COLOR, 215)
            else:
                radius, color = 3.0, _with_alpha(self.ACCENT_COLOR, 140)
            painter.setPen(NoPen)
            painter.setBrush(color)
            painter.drawEllipse(QtCore.QPointF(x, self.DOT_Y), radius, radius)

    def _draw_labels(self, painter, points):
        font = self.font()
        bold_font = QtGui.QFont(font)
        bold_font.setBold(True)
        metrics = QtGui.QFontMetrics(font)
        label_color = _with_alpha(self.palette().color(self.foregroundRole()), 205)

        # 先算出选中档期标签的位置，为它预留空间，避免年份标签压上去
        current_left = None
        current_width = 0.0
        current_text = ""
        if 0 <= self._current < len(self._items):
            current_text = self._items[self._current]["date_str"]
            current_width = QtGui.QFontMetrics(bold_font).horizontalAdvance(
                current_text
            )
            current_left = points[self._current] - current_width / 2
            current_left = max(
                4.0, min(current_left, self.width() - current_width - 4.0)
            )

        # 每个年份只标注第一档，并按像素间距抽稀，避免标签重叠
        last_year = None
        occupied = -1.0e9
        for index, (item, x) in enumerate(zip(self._items, points)):
            year = item["date"].year()
            first_of_year = year != last_year
            last_year = year
            if index == self._current or not first_of_year:
                continue
            text = str(year)
            width = metrics.horizontalAdvance(text)
            left = max(4.0, min(x - width / 2, self.width() - width - 4.0))
            if left < occupied + LABEL_GAP:
                continue
            if current_left is not None and (
                left < current_left + current_width + LABEL_GAP
                and left + width > current_left - LABEL_GAP
            ):
                continue
            painter.setFont(font)
            painter.setPen(label_color)
            painter.drawText(QtCore.QPointF(left, self.LABEL_BASELINE), text)
            occupied = left + width

        # 选中档期最后绘制并加粗，保证画在最上层
        if current_left is None:
            return
        painter.setFont(bold_font)
        painter.setPen(self.ACCENT_COLOR)
        painter.drawText(
            QtCore.QPointF(current_left, self.LABEL_BASELINE), current_text
        )

    def _layout_points(self):
        if not self._items:
            return []
        left = self.HEIGHT / 2 + 6
        right = self.width() - self.HEIGHT / 2 - 6
        if right - left < 1:
            left, right = 14.0, max(self.width() - 14.0, 15.0)
        first = self._items[0]["date"]
        last = self._items[-1]["date"]
        span = first.daysTo(last)
        if span <= 0 or len(self._items) == 1:
            middle = (left + right) / 2
            return [middle for _ in self._items]
        return [
            left + (right - left) * first.daysTo(item["date"]) / span
            for item in self._items
        ]

    def _pill_color(self):
        base = self.palette().color(self.backgroundRole())
        if base.lightness() < 128:
            return QtGui.QColor(255, 255, 255, 28)
        return QtGui.QColor(0, 0, 0, 16)

    def _muted_text_color(self):
        return _with_alpha(self.palette().color(self.foregroundRole()), 120)

    # ---------- 交互 ----------

    def _hit_index(self, pos):
        points = self._layout_points()
        best, best_gap = -1, HIT_RADIUS
        for index, x in enumerate(points):
            gap = abs(pos.x() - x)
            if gap <= best_gap:
                best, best_gap = index, gap
        return best

    def _tooltip_text(self, index):
        item = self._items[index]
        parts = [item["date_str"]]
        if item.get("name"):
            parts.insert(0, str(item["name"]))
        if item.get("reso"):
            parts.append(f"{item['reso']} m")
        return " · ".join(parts)

    def mouseMoveEvent(self, event):
        index = self._hit_index(event.pos())
        if index != self._hover:
            self._hover = index
            self.update()
            if index >= 0:
                QtWidgets.QToolTip.showText(
                    self.mapToGlobal(event.pos()), self._tooltip_text(index), self
                )
            else:
                QtWidgets.QToolTip.hideText()
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        self._hover = -1
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == LeftButton:
            index = self._hit_index(event.pos())
            if index >= 0:
                self.set_current_index(index)
                event.accept()
                return
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        key = event.key()
        if key in (KeyLeft, KeyRight, KeyHome, KeyEnd) and self._items:
            if key == KeyLeft:
                self.set_current_index(self._current - 1)
            elif key == KeyRight:
                self.set_current_index(self._current + 1)
            elif key == KeyHome:
                self.set_current_index(0)
            else:
                self.set_current_index(len(self._items) - 1)
            event.accept()
            return
        super().keyPressEvent(event)


def _item_value(item, key):
    if not isinstance(item, dict):
        return item if key == "date" else None
    if key == "date":
        return item.get("date") or item.get("st")
    return item.get(key)


def _to_qdate(value):
    if isinstance(value, bool):
        return None
    # imgmeta 的 st 可能是整数（201304）而不是字符串
    if isinstance(value, (int, float)):
        value = str(int(value))
    if isinstance(value, QDate):
        return value
    if isinstance(value, datetime.datetime):
        return QDate(value.year, value.month, value.day)
    if isinstance(value, datetime.date):
        return QDate(value.year, value.month, value.day)
    if isinstance(value, str):
        text = value.strip()
        for date_format in DATE_FORMATS:
            date = QDate.fromString(text, date_format)
            if date.isValid():
                return date
    return None


def _with_alpha(color, alpha):
    faded = QtGui.QColor(color)
    faded.setAlpha(alpha)
    return faded
