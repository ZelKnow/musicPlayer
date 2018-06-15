import time
import sys



def convert_time(time_stamp):
    '''把int类型的时间转化为 mm:ss 的形式'''
    hour = time_stamp // 3600
    if hour > 0:
        time_stamp %= hour
    minute = time_stamp // 60
    if minute > 0:
        time_stamp %= 60
    second = time_stamp
    return '{:0>2}:{:0>2}'.format(minute, second)