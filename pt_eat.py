import random
import subprocess
import sys
import time
from datetime import datetime, timedelta

# from unidecode import unidecode

from pt_schedule import GameTimeManager, date_string, game_time_string, GameTimeScheduler, thread_func, is_time_between

# 函数的默认参数只会在函数“定义”时被计算一次 (self, timestamp=time.time()) ×


# winter
# 晚上 16:45 开灯
# 早上 09:00 关灯


x_position = 1200
# eat_y = 1500
magic_y = 1200
eat_y = 1350
kiss_y = 1700
sneeze_y = 1850

y_1 = 650
y_2 = 800
y_3 = 1000

y_4 = 1150
y_5 = 1300
y_6 = 1500

y_7 = 1650
y_8 = 1850
y_9 = 2000

sn = "4VL0125520000243"
# use = f"{x_position} 1900"

# x_position
def get_first_parameter():
    if len(sys.argv) == 1:
        return eat_y
    try:
        return int(sys.argv[1])
    except Exception:
        return eat_y

use_y = get_first_parameter()

shell_base = f"hdc -t {sn} shell"
time_multi = 5

cmd_queue = []
is_running = False

def add_cmd_queue(cmd):
    print(cmd)
    cmd_queue.append(cmd)
    run_cmd_queue()

def run_cmd_queue():
    global is_running
    if is_running:
        return
    is_running = True
    try:
        while cmd_queue:
            cmd = cmd_queue.pop(0)
            # print("RUN:", cmd)
            subprocess.run(cmd, shell=True)
    finally:
        is_running = False



def device_wait(t):
    cmd_sleep = f'{shell_base} sleep {t}'
    add_cmd_queue(cmd_sleep)
    # subprocess.run(cmd_sleep, shell=True)

def touch(x, y):
    cmd = f'{shell_base} "uinput -M -m {x} {y} -d 0 -u 0"'
    add_cmd_queue(cmd)
    # print(cmd)
    # subprocess.run(cmd, shell=True)


def device_input(s):
    # cmd = f"hdc shell uinput -K -t \"`printf {s}`\""
    cmd = f"hdc shell uinput -K -t {s}"
    add_cmd_queue(cmd)
    # print(cmd)
    # subprocess.run(cmd, shell=True)

def say(s):
    # 输入框
    touch(100, 2300)

    device_input(s)
    # device_wait(2)
    # 发送
    touch_right_button(1600)

def touch_right_button(y):
    touch(x_position, y)
    # cmd = f'{shell_base} "uinput -M -m {x_position} {y} -d 0 -u 0"'
    # print(cmd)
    # subprocess.run(cmd, shell=True)


# emoji_list = [
#     "(≧▽≦)/", "(=^･ω･^=)", "(｡>ω<｡)", "(｡>﹏<｡)",
#     "～(つˆДˆ)つ", "(｀・ω・´)", "(ﾉ≧∀≦)ﾉ",
#     "_(:з」∠)_", "(=・ω・=)", "_(≧v≦」∠)_", "(〜￣△￣)〜", "╮(￣▽￣)╭", "(・ω< )☆", "(^・ω・^)", "(｡･ω･｡)"
# ]
# emoji_list = [unidecode(emoji) for emoji in emoji_list]

def next_half_or_full_hour_final():
    now = datetime.now()
    # now = datetime(2024, 6, 30, 23, 40, 0)
    h, m = now.hour, now.minute
    if m < 30:
        next_time = now.replace(minute=30, second=0, microsecond=0)
        time_str = next_time.strftime("%H:%M:%S")
    else:
        next_time = (now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1))
        time_str = next_time.strftime("%H:%M:%S")
    seconds_to_next = int((next_time - now).total_seconds())

    # 随机颜色
    # 判断是否为凌晨0点~6点
    # if 0 <= next_time.hour < 6 and random.random() < 0.99:
    #     text_emoji = "(。-ω-)zzz"
    # else:
    #     text_emoji = random.choice(emoji_list)
    # 拼接输出

    time_str = f"Beijing_Time:_{time_str}!"

    return time_str, seconds_to_next

def say_every_half_hour(_):
    print("started say every half hour")
    while True:
        time_str, seconds_to_next = next_half_or_full_hour_final()

        # 等待到下一个半小时
        if seconds_to_next > 0:
            time.sleep(seconds_to_next)
            # say(time_str)
            say(f"Beijing_Time:_{time_str}!")
        else:
            time.sleep(1)




def extinguish_torch(gts: GameTimeScheduler):
    get_flag = gts.get_flag
    if get_flag("extinguish_torch"):
        return
    gts.set_flag("extinguish_torch", True)
    touch_right_button(magic_y)
    # run_time = 16 * 2 * 60
    # time_begin = time.time()
    # finish_time = time_begin + run_time
    random_action = [
        lambda : touch_right_button(sneeze_y),
        lambda : touch_right_button(2050)
    ]
    while get_flag("extinguish_torch"):
        # if time.time() > finish_time:
        #     return
        num = round(random.uniform(0.8, 2), 8)
        wait_time = num * time_multi
        # double_num = round(num * 2, 3)
        # double_num_str = '{:.3f}'.format(num)
        # 执行你的 shell 命令
        # touch(eat_y)

        # time.sleep(0.1)

        # device_wait(0.05)

        random.choice(random_action)()
        touch_right_button(kiss_y)
        print(f'wait {wait_time}')
        print()
        time.sleep(wait_time)


def eat_sometimes(gts: GameTimeScheduler):
    get_flag = gts.get_flag
    if get_flag("eat_sometimes"):
        return
    gts.set_flag("eat_sometimes", True)
    touch_right_button(magic_y)
    # run_time = 9 * 2 * 60
    # time_begin = time.time()
    # finish_time = time_begin + run_time
    random_action = [
        lambda : touch_right_button(y_3),
        lambda : touch_right_button(y_4),
        lambda : touch_right_button(y_5)
    ]
    while get_flag("eat_sometimes"):
        action = random.choice(random_action)
        # if time.time() > finish_time:
        #     return

        # double_num = round(num * 2, 3)
        # double_num_str = '{:.3f}'.format(num)
        # 执行你的 shell 命令
        # touch(eat_y)

        # time.sleep(0.1)
        action()
        wait_time = round(random.uniform(0.1, 2), 8) * time_multi
        print(f'wait {wait_time}')
        print()
        time.sleep(wait_time)
        action()
        wait_time = round(random.uniform(0.1, 2), 8) * time_multi
        print(f'wait {wait_time}')
        print()
        time.sleep(wait_time)






pt_m = GameTimeManager(date_string, game_time_string)
pt_s = GameTimeScheduler(pt_m)


thread_func(say_every_half_hour)(None)
# thread_func(extinguish_torch)(pt_s)


# game_time_begin = ptm.get_game_time()
# game_time_begin = (game_time_begin[0], game_time_begin[1] + 1)

# for i in range(24):
#     pt_s.add_task((i, 0), lambda gts: say(f"Game_Time:_{i:02d}:00!") )
# 这是Python中闭包变量捕获的经典问题。所有lambda函数都引用了同一个变量i，当循环结束时，i的值是23，所以所有lambda函数都使用了23。

def create_task_func(hour):
    return lambda gts: say(f"Game_Time:_{hour:02d}:00!")

# for i in range(24):
#     pt_s.add_task((i, 0), create_task_func(i))

pt_s.add_task((17, 0), thread_func(extinguish_torch))
pt_s.add_task((9, 0), lambda gts: gts.set_flag("extinguish_torch", False) )
# pt_s.add_task((9, 0), lambda gts: touch(magic_y))

pt_s.add_task((9, 0), thread_func(eat_sometimes))
pt_s.add_task((17, 0), lambda gts: gts.set_flag("eat_sometimes", False) )





pts_thread = pt_s.run_thread_mainloop()
# or pt_s.thread.join()
if is_time_between(pt_s.game_time_begin, (17,1), (8,50)):
    print(f"start 17, 0 at {pt_s.game_time_begin}")
    pt_s.run_task((17, 0))

    # 正好同时print导致print混乱，一个在线程中，一个在主线程中
    # def set_flag(self, flag_name: str, value: bool):
    #     print(f"{threading.current_thread().name} set_flag: {flag_name} = {value}")
    #     # print(f"set_flag: {flag_name} = {value}")
    #     self.flags[flag_name] = value

if is_time_between(pt_s.game_time_begin, (9,1), (16,50)):
    print(f"start 9, 0 at {pt_s.game_time_begin}")
    pt_s.run_task((9, 0))

pts_thread.join()













# print(-1 %2)1
# print(-1 %3)2
# class GameTime:
#     def __init__(self, hour, minute):
#         self._hour = hour
#         self._minute = minute
#         self._cached_str = None
#
#     @property
#     def strftime(self):
#         if self._cached_str is None:
#             self._cached_str = f"{self._hour:02d}:{self._minute:02d}"
#             time.strftime()
#         return self._cached_str
#
#     @property
#     def hour(self):
#         return self._hour
#
#     @hour.setter
#     def hour(self, value):
#         self._hour = value
#         self._cached_str = None
#
#     @property
#     def minute(self):
#         return self._minute
#
#     @minute.setter
#     def minute(self, value):
#         self._minute = value
#         self._cached_str = None  # 改变时失效缓存
#
#     def tuple(self):
#         return self._hour, self._minute

# wait = time.sleep
# get_timestamp = time.time
# wait(1)
# time1 = get_timestamp()
# print(time1)
# for i in range(10):
#     time.sleep(1)
#     print(time.time())
# wait(1)
# time2 = get_timestamp()
# print(time2)
# print(f"diff: {time2 - time1}")
# 0.001 diff
# exit()
