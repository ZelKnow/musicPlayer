import time
import sys


def time_int_to_str(time):
    '''把int类型的时间转化为 mm:ss 的形式'''
    hour = time // 3600
    if hour > 0:
        time %= hour
    minute = time // 60
    if minute > 0:
        time %= 60
    second = time
    return '{:0>2}:{:0>2}'.format(minute, second)


def time_str_to_int(time):
    '''把mm:ss.sss形式的时间转化为int类型'''
    time = time.split(':')
    minute = int(time[0])
    second = float(time[1])
    return int(minute * 60000 + second * 1000)


def convert_lyric(lyric):
    '''
    参数为字符串 '[mm:ss.ss(s)]str[mm:ss.ss(s)]str...'
    返回列表 [(millionsecond, str), (millionsecond, str), ...]
    '''
    res = []
    strings = lyric.split('[')
    for string in strings:
        time, word = string.split(']')
        millionsecond = time_str_to_int(time)
        res.append(tuple(millionsecond, word))

    return res