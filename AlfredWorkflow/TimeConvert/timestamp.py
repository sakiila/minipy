# -*- coding: utf-8 -*-  
import sys
import time
import re
import calendar
from datetime import datetime
from workflow import Workflow3

def getTime(ts):
    wf = Workflow3()
    s = ts
    ms = str(ts * 1000)

    # 使用 gmtime 替代 localtime 来获取 UTC 时间
    timeArray = time.gmtime(ts)

    wf.add_item(uid="s", title="秒 (UTC): " + str(s), arg=s, valid=True)
    wf.add_item(uid="ms", title="毫秒 (UTC): " + str(ms), arg=ms, valid=True)
    wf.add_item(uid="date", title="日期 (UTC): " + time.strftime("%Y-%m-%d", timeArray),
                arg=time.strftime("%Y-%m-%d", timeArray), valid=True)
    wf.add_item(uid="datetime", title="时间 (UTC): " + time.strftime("%Y-%m-%d %H:%M:%S", timeArray),
                arg=time.strftime("%Y-%m-%d %H:%M:%S", timeArray), valid=True)
    wf.send_feedback()

def parse_datetime_to_timestamp(dt_str, format_str):
    """将日期时间字符串转换为 UTC 时间戳"""
    try:
        # 将输入的时间字符串解析为 datetime 对象，假定输入是 UTC 时间
        dt = datetime.strptime(dt_str, format_str)
        # 转换为时间戳
        return calendar.timegm(dt.timetuple())
    except ValueError as e:
        print(f"Error parsing datetime: {e}")
        return None

if __name__ == '__main__':
    if len(sys.argv) == 1:
        # 获取当前的 UTC 时间戳
        ts = calendar.timegm(time.gmtime())
        getTime(ts)
        exit(0)

    query = sys.argv[1]

    if query == 'now':
        # 获取当前的 UTC 时间戳
        ts = calendar.timegm(time.gmtime())
        getTime(ts)
    elif re.match(r"\d+-\d+-\d+ \d+:\d+:\d+", query):
        # 解析完整的日期时间字符串
        ts = parse_datetime_to_timestamp(query, '%Y-%m-%d %H:%M:%S')
        if ts is not None:
            getTime(int(ts))
    elif re.match(r"\d+-\d+-\d+", query):
        # 解析仅包含日期的字符串
        ts = parse_datetime_to_timestamp(query, '%Y-%m-%d')
        if ts is not None:
            getTime(int(ts))
    elif re.match(r"\d+", query):
        # 处理时间戳输入
        ts = int(query)
        if ts > 253402185600:  # 如果时间戳是毫秒格式
            ts = ts / 1000
        getTime(int(ts))