import pyautogui
import time
import random
import math


class HumanMouse:
    """
    模拟人类鼠标操作的封装类
    支持：移动、左/右/中键点击、按下/松开、拖拽等

    使用示例：
        mouse = HumanMouse(human_factor=0.92)
        mouse.move_to(1200, 800)
        mouse.click_left(1200, 800)
        mouse.click_right(offset=3)
        mouse.press_middle()
        mouse.release_middle()
    """

    def __init__(self,
                 human_factor: float = 0.93,     # 0.0~1.0，越高越接近真人（但动作稍慢）
                 default_duration: float = 0.45, # 默认移动时间
                 default_offset: int = 3,        # 默认点击偏移像素
                 fail_safe: bool = True):
        pyautogui.FAILSAFE = fail_safe
        pyautogui.PAUSE = 0

        self.human_factor = max(0.1, min(1.0, human_factor))
        self.default_duration = default_duration
        self.default_offset = default_offset

    # ────────────────────────────────────────────────
    #  核心移动函数（三次贝塞尔 + 非线性速度曲线）
    # ────────────────────────────────────────────────

    def _cubic_bezier(self, t: float, p0, p1, p2, p3):
        """三次贝塞尔曲线"""
        u = 1 - t
        tt = t * t
        uu = u * u
        uuu = uu * u
        ttt = tt * t

        x = uuu * p0[0] + 3 * uu * t * p1[0] + 3 * u * tt * p2[0] + ttt * p3[0]
        y = uuu * p0[1] + 3 * uu * t * p1[1] + 3 * u * tt * p2[1] + ttt * p3[1]
        return x, y

    def _velocity_curve(self, t: float) -> float:
        """S型速度曲线 + 轻微噪声"""
        # sigmoid 风格的慢-快-慢
        eased = 1 / (1 + math.exp(-10 * (t - 0.5)))
        # 加一点随机波动
        noise = random.gauss(0, 0.06 * self.human_factor)
        return max(0.0, min(1.0, eased + noise))

    def move_to(self,
                x: int | float,
                y: int | float,
                duration: float | None = None,
                curvature: int = 28,
                human_factor: float | None = None):
        """
        自然曲线移动到目标坐标
        """
        hf = human_factor if human_factor is not None else self.human_factor
        dur = duration if duration is not None else self.default_duration

        sx, sy = pyautogui.position()
        tx, ty = int(x), int(y)

        dist = math.hypot(tx - sx, ty - sy)
        if dist < 3:
            pyautogui.moveTo(tx, ty, duration=0.04)
            return

        # 控制点偏移
        offset = int(curvature * hf * random.uniform(0.7, 1.5))
        angle = math.atan2(ty - sy, tx - sx)

        p0 = (sx, sy)
        p3 = (tx, ty)

        # 控制点1、2
        p1x = sx + (tx - sx) * random.uniform(0.25, 0.45) + math.cos(angle + math.pi/2) * offset * random.uniform(-1, 1)
        p1y = sy + (ty - sy) * random.uniform(0.25, 0.45) + math.sin(angle + math.pi/2) * offset * random.uniform(-1, 1)
        p2x = sx + (tx - sx) * random.uniform(0.55, 0.75) + math.cos(angle - math.pi/2) * offset * random.uniform(-1, 1)
        p2y = sy + (ty - sy) * random.uniform(0.55, 0.75) + math.sin(angle - math.pi/2) * offset * random.uniform(-1, 1)

        p1 = (p1x, p1y)
        p2 = (p2x, p2y)

        steps = max(18, min(68, int(dist / 5 * hf)))

        for i in range(steps + 1):
            raw_t = i / steps
            t = self._velocity_curve(raw_t)

            bx, by = self._cubic_bezier(t, p0, p1, p2, p3)

            jitter = hf * random.gauss(0, 1.4)
            cx = int(bx + jitter)
            cy = int(by + jitter)

            pyautogui.moveTo(cx, cy, _pause=False)

            step_dur = (dur / steps) * random.uniform(0.7, 1.4)
            time.sleep(step_dur)

        # 极小概率轻微过冲 + 修正
        if random.random() < 0.07 * hf:
            ox = tx + random.randint(-14, 14)
            oy = ty + random.randint(-14, 14)
            pyautogui.moveTo(ox, oy, duration=0.06)
            time.sleep(random.uniform(0.03, 0.09))
            pyautogui.moveTo(tx, ty, duration=0.07)

    # ────────────────────────────────────────────────
    #  点击相关函数
    # ────────────────────────────────────────────────

    def _click_internal(self,
                        button: str,          # 'left', 'right', 'middle'
                        x: int | None = None,
                        y: int | None = None,
                        offset: int | None = None,
                        press_duration: float = 0.08,
                        move_duration: float | None = None):
        if x is None or y is None:
            cx, cy = pyautogui.position()
        else:
            cx, cy = int(x), int(y)

        off = offset if offset is not None else self.default_offset
        click_x = cx + random.randint(-off, off)
        click_y = cy + random.randint(-off, off)

        # 先移动
        self.move_to(click_x, click_y, duration=move_duration)

        # 按下前微延迟
        time.sleep(random.uniform(0.035, 0.13))

        pyautogui.mouseDown(x=click_x, y=click_y, button=button)
        time.sleep(random.uniform(press_duration * 0.65, press_duration * 1.45))
        pyautogui.mouseUp(x=click_x, y=click_y, button=button)

        # 点击后自然间隔
        time.sleep(random.uniform(0.12, 0.48))

    def click_left(self, x=None, y=None, offset=None, press_duration=0.08, move_duration=None):
        """左键单击"""
        self._click_internal('left', x, y, offset, press_duration, move_duration)

    def click_right(self, x=None, y=None, offset=None, press_duration=0.08, move_duration=None):
        """右键单击"""
        self._click_internal('right', x, y, offset, press_duration, move_duration)

    def click_middle(self, x=None, y=None, offset=None, press_duration=0.08, move_duration=None):
        """中键单击"""
        self._click_internal('middle', x, y, offset, press_duration, move_duration)

    def press_left(self, x=None, y=None):
        """只按下左键（不松开）"""
        if x is not None and y is not None:
            self.move_to(x, y)
        cx, cy = pyautogui.position()
        pyautogui.mouseDown(cx, cy, button='left')

    def release_left(self):
        """松开左键"""
        cx, cy = pyautogui.position()
        pyautogui.mouseUp(cx, cy, button='left')

    def press_right(self, x=None, y=None):
        if x is not None and y is not None:
            self.move_to(x, y)
        cx, cy = pyautogui.position()
        pyautogui.mouseDown(cx, cy, button='right')

    def release_right(self):
        cx, cy = pyautogui.position()
        pyautogui.mouseUp(cx, cy, button='right')

    def press_middle(self, x=None, y=None):
        if x is not None and y is not None:
            self.move_to(x, y)
        cx, cy = pyautogui.position()
        pyautogui.mouseDown(cx, cy, button='middle')

    def release_middle(self):
        cx, cy = pyautogui.position()
        pyautogui.mouseUp(cx, cy, button='middle')

    # 常用组合动作
    def drag_to(self, x, y, duration=1.2, button='left'):
        """从当前位置拖拽到目标位置"""
        self.move_to(x, y, duration=duration * 0.3)   # 先快速移过去
        if button == 'left':
            self.press_left()
        elif button == 'right':
            self.press_right()
        elif button == 'middle':
            self.press_middle()

        time.sleep(random.uniform(0.08, 0.18))

        self.move_to(x, y, duration=duration * 0.7, curvature=35)  # 慢速拖动

        if button == 'left':
            self.release_left()
        elif button == 'right':
            self.release_right()
        elif button == 'middle':
            self.release_middle()

        time.sleep(random.uniform(0.15, 0.55))


# ────────────────────────────────────────────────
#  使用示例
# ────────────────────────────────────────────────

if __name__ == "__main__":
    mouse = HumanMouse(human_factor=0.93, default_duration=0.48, default_offset=5)

    print("3秒后开始演示...")
    time.sleep(3)

    # 移动 → 左键点击
    mouse.move_to(800, 600)
    mouse.click_left()

    time.sleep(1.2)

    # 右键点击（带更大偏移）
    mouse.click_right(offset=8)

    time.sleep(0.8)

    # 中键按下 → 移动 → 松开（模拟滚轮拖动或某些游戏操作）
    mouse.press_middle()
    mouse.move_to(1200, 900, duration=0.9)
    mouse.release_middle()

    print("演示结束")