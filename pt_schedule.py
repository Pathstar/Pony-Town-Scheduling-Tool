import threading
import time
from datetime import datetime



date_string = "2025-12-16 15:32:18"
game_time_string = "01:10"

def thread_func(func):
    def run_in_thread(pts):
        thread = threading.Thread(target=func, args=(pts,), daemon=True)
        thread.start()
        return thread
    return run_in_thread


def game_time_minutes_to_tuple(minutes) -> tuple[int, int]:
    """
    m: 任意int，返回24进制 h:m
    :param minutes:
    :return:
    """
    h, m = divmod(minutes, 60)
    h %= 24
    return h, m
    # return (m // 60) % 24, m % 60

def game_time_tuple_to_minutes(t:tuple):
    return t[0]*60 + t[1]

def game_time_tuple_to_str(t:tuple):
    return f"{t[0]:02d}:{t[1]:02d}"

def game_time_str_to_tuple(time_str: str):
    try:
        hours, minutes = time_str.split(':')

        # 将分割后的字符串转换为整数
        hours = int(hours)
        minutes = int(minutes)

        return hours, minutes
    except Exception:
        print(f'error time string: {time_str}')
        return -1, -1
    

def is_time_between(check_time, start_time, end_time):
    """
    判断一个时间是否在两个时间范围之间（包括起止）。
    参数:
    time: tuple, 表示时间 (小时, 分钟)
    start_time: tuple, 起始时间 (小时, 分钟)
    end_time: tuple, 结束时间 (小时, 分钟)
    返回值:
    True/False
    """
    # 转换为分钟
    time_min = game_time_tuple_to_minutes(check_time)
    start_min = game_time_tuple_to_minutes(start_time)
    end_min = game_time_tuple_to_minutes(end_time)

    if start_min <= end_min:
        return start_min <= time_min <= end_min
    else:
        # 跨夜情况处理, 例如22:00~06:00
        return time_min >= start_min or time_min <= end_min





class GameTimeManager:
    def __init__(self, date_string, game_time_string):
        # 默认映射为当前现实时间与游戏00:00
        try:
            self.base_real_time = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S").timestamp()
            game_time_tuple = game_time_str_to_tuple(game_time_string)
            self.base_game_minute = game_time_tuple[0] * 60 + game_time_tuple[1]
        except Exception as e:
            raise e

        # 一个游戏分钟 = 2秒现实时间
        self.seconds_per_game_minute: float = 2
        self.game_minutes_per_day = 24 * 60
        self.game_day_seconds = self.game_minutes_per_day * self.seconds_per_game_minute



    def get_game_time_minutes(self, timestamp=None) -> float:
        """
        int game_minutes
        :param timestamp: (time.time)
        :return:
        """
        if timestamp is None:
            timestamp = time.time()
        # 计算过去了多少现实秒
        passed_real_seconds = timestamp - self.base_real_time
        return self.base_game_minute + passed_real_seconds/self.seconds_per_game_minute

    def get_game_time(self, timestamp=None) -> tuple[int, int]:
        """
        tuple h,m
        :param timestamp: (time.time)
        :return:
        """
        return game_time_minutes_to_tuple(int(self.get_game_time_minutes(timestamp)))

    def get_game_time_by_datetime(self, date_time: datetime):
        return self.get_game_time(date_time.timestamp())

    def is_future(self, now):
        return True if self.base_real_time > now else False

    def calibrate_game_time(self, real_time_str, game_time_str):
        """
        real_time_str: 现实时间（'HH:MM'）
        game_time_str: 游戏时间（'HH:MM'）
        """
        real_time_tuple = time.strptime(real_time_str, '%H:%M')
        today_tuple = time.localtime()
        base_real_time = time.mktime(today_tuple[:3] + real_time_tuple[3:6] + (0, 0, 0))
        game_time_tuple = time.strptime(game_time_str, '%H:%M')
        base_game_minute = game_time_tuple.tm_hour * 60 + game_time_tuple.tm_min
        self.base_real_time = base_real_time
        self.base_game_minute = base_game_minute



    def get_game_time_tuple(self):
        now_real_time = time.time()
        passed_real_seconds = now_real_time - self.base_real_time
        passed_game_minutes = int(passed_real_seconds // self.seconds_per_game_minute)
        total_game_minutes = (self.base_game_minute + passed_game_minutes) % self.game_minutes_per_day
        game_hour = total_game_minutes // 60
        game_min = total_game_minutes % 60
        return game_hour, game_min



    def get_real_timestamp_by_game_time(self, h: int, m: int, game_round: int = 0):
        """
        给定目标游戏时间(h:m)以及轮数(可为负)，查询对应的现实时间戳
        :param h: 游戏小时（0-23）
        :param m: 游戏分钟（0-59）
        :param round: 轮数/次数(0为本次，正数为未来，负数为过去)
        :return: 现实时间戳
        """
        # 目标游戏时间对应的游戏分钟数
        target_game_minute = h * 60 + m + game_round * self.game_minutes_per_day
        # 和初始映射的游戏分钟比对，得出差值
        delta_game_minute = target_game_minute - self.base_game_minute
        # 游戏分钟差转为现实秒
        delta_real_seconds = delta_game_minute * self.seconds_per_game_minute
        # 映射回现实时间
        target_real_timestamp = self.base_real_time + delta_real_seconds
        return target_real_timestamp

    def get_real_datetime_by_game_time(self, h: int, m: int, game_round: int = 0):
        timestamp = self.get_real_timestamp_by_game_time(h, m, game_round)
        return datetime.fromtimestamp(timestamp)

    def get_seconds_to_next_game_minute(self, timestamp=None):
        """
        返回距离下一次游戏分钟变化还差多少现实秒
        :param timestamp: 默认为当前时间
        :return: 秒数（float）
        """
        if timestamp is None:
            timestamp = time.time()
        passed_seconds = timestamp - self.base_real_time
        left = self.seconds_per_game_minute - (passed_seconds % self.seconds_per_game_minute)
        # # 避免因为极小数误差导致出现1.9999变成2秒，实际是刚好在0点上( ±0.000001 1e-6) 1ms
        # # 修改为 10ms 0.00001
        # if abs(left - self.seconds_per_game_minute) < 1e-5:
        #     left = 0
        return left

class GameTimeScheduler:
    def __init__(self, gtm: GameTimeManager, params=None):
        super().__init__()
        self.gtm = gtm
        self.interval: float = gtm.seconds_per_game_minute
        self.tasks = {}  # key: (HH, MM): [func, ...]
        self.thread: threading.Thread | None = None
        self.thread_stop = threading.Event()
        self.has_run_init = False
        self.game_minutes = -1
        self.game_time_begin = (-1, -1)
        self.game_days_since_run = 0
        self.game_time_change_timestamp: float = -1
        self.flags = {}
        self.params = params if params else {}

    def set_flag(self, flag_name: str, value: bool):
        self.flags[flag_name] = value

    def get_flag(self, flag_name: str, default=False):
        return self.flags.get(flag_name, default)

    def stop_run(self, join: bool = False, timeout: float | None = None):
        """请求停止主循环；可选等待线程退出。"""
        self.thread_stop.set()
        if join and self.thread and self.thread.is_alive():
            self.thread.join(timeout=timeout)

    def add_task(self, time_key: tuple[int, int], func):
        self.tasks.setdefault(time_key, []).append(func)

    # def todo 校准时间

    # def todo 加offset

    def run_task(self, time_key: tuple[int, int]):
        tasks = self.tasks.get(time_key)
        if tasks:
            for func in tasks:
                try:
                    func(self)
                except Exception as e:
                    print(f"任务执行错误: {e}")


    def run_init(self, is_round=True, loop_offset: float=0):
        # ------- init -------

        timestamp_begin = time.time()
        self.game_minutes = int(self.gtm.get_game_time_minutes(timestamp_begin))
        self.game_time_begin: tuple[int, int] = game_time_minutes_to_tuple(self.game_minutes)
        time_left = self.gtm.get_seconds_to_next_game_minute(timestamp_begin)
        # --------------------
        # 下个游戏时间变化的现实时间刻
        self.game_time_change_timestamp = timestamp_begin + time_left
        if is_round:
            self.game_time_change_timestamp = round(self.game_time_change_timestamp)
        if loop_offset:
            self.game_time_change_timestamp += loop_offset

        self.has_run_init = True

    def run_mainloop(self, is_round=True, loop_offset: float=0):
        """
        :param is_round:
        :param loop_offset:
        :return:
        """
        if not self.has_run_init:
            self.run_init(is_round, loop_offset)
        self.run_task(self.game_time_begin)
        # 运行经过时进行天数增加
        self.add_task(self.game_time_begin, self.increase_game_day_since_run)
        get_timestamp = time.time
        wait = time.sleep
        while True:
            print()
            now = get_timestamp()
            if self.game_time_change_timestamp > now:
                wait(self.game_time_change_timestamp - now)
            if self.thread_stop.is_set():
                break
            self.game_minutes += 1

            game_time: tuple[int, int] = game_time_minutes_to_tuple(self.game_minutes)
            print(f"game_time: {game_time_tuple_to_str(game_time)}")
            self.run_task(game_time)


            self.game_time_change_timestamp += self.interval
            print(f"next: {self.game_time_change_timestamp}")

    def run_thread_mainloop(self, is_round=True, loop_offset: float = 0,
                            daemon: bool = True) -> threading.Thread:
        """用线程启动主循环。重复调用时，若线程仍在跑则直接返回该线程。"""

        if not self.has_run_init:
            self.run_init(is_round, loop_offset)

        if self.thread and self.thread.is_alive():
            return self.thread
        self.thread_stop.clear()
        self.thread = threading.Thread(
            target=self.run_mainloop,
            args=(is_round, loop_offset),
            # kwargs={"is_round": is_round, "loop_offset": loop_offset},
            daemon=daemon
        )
        self.thread.start()
        return self.thread




    def increase_game_day_since_run(self, gts):
        """
        Default: callback at run time
        :param func:
        :return:
        """
        self.game_days_since_run += 1
        print(f"{time.strftime("%H:%M:%S")} game_days_since_run: {self.game_days_since_run}")

