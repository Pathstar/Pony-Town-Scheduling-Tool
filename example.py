import random
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pt_schedule import GameTimeManager, date_string, game_time_string, GameTimeScheduler, thread_func, is_time_between

# winter
# 晚上 16:45 开灯
# 早上 09:00 关灯

# ------- 定义按钮位置 --------------
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
# -----------------------

sn = -1
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



def extinguish_torch(gts: GameTimeScheduler):
    get_flag = gts.get_flag
    if get_flag("extinguish_torch"):
        return
    gts.set_flag("extinguish_torch", True)
    touch_right_button(magic_y)
    random_action = [
        lambda : touch_right_button(sneeze_y),
        lambda : touch_right_button(2050)
    ]
    while get_flag("extinguish_torch"):
        num = round(random.uniform(0.8, 2), 8)
        wait_time = num * time_multi
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
    random_action = [
        lambda : touch_right_button(y_3),
        lambda : touch_right_button(y_4),
        lambda : touch_right_button(y_5)
    ]
    while get_flag("eat_sometimes"):
        action = random.choice(random_action)
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





# 创建调度工具
pt_m = GameTimeManager(date_string, game_time_string)
pt_s = GameTimeScheduler(pt_m)

# 在每个pony town小时都进行报时
# def create_task_func(hour):
#     return lambda gts: say(f"Game_Time:_{hour:02d}:00!")
# for i in range(24):
#     pt_s.add_task((i, 0), create_task_func(i))

# 添加在pony town时间刻时运行的函数
# 在17点钟启动循环熄灭火把
pt_s.add_task((17, 0), thread_func(extinguish_torch))
# 在上午九点停止循环熄灭火把
pt_s.add_task((9, 0), lambda gts: gts.set_flag("extinguish_torch", False) )

pt_s.add_task((9, 0), thread_func(eat_sometimes))
pt_s.add_task((17, 0), lambda gts: gts.set_flag("eat_sometimes", False) )

# 线程启动主循环
pts_thread = pt_s.run_thread_mainloop()

# 用线程启动的时间，判断需要运行什么任务，在17:01-第二天08:50时，也要运行17:00的任务
if is_time_between(pt_s.game_time_begin, (17,1), (8,50)):
    print(f"start 17, 0 at {pt_s.game_time_begin}")
    pt_s.run_task((17, 0))

if is_time_between(pt_s.game_time_begin, (9,1), (16,50)):
    print(f"start 9, 0 at {pt_s.game_time_begin}")
    pt_s.run_task((9, 0))

# 堵塞主线程
pts_thread.join()
