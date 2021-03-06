#coding=UTF-8
from nose.tools import *
import datetime

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from timerlist import TimerList

timerlist = TimerList()

# 文字列はエラー
def test_get_timer_string():
    eq_(timerlist.get_timer('a', ''), None)

# nn:nn で時間指定タイマー
def test_get_timer_colon():
    h = timerlist.get_timer('10:00', '')
    endtime = h['endtime']
    eq_(endtime.hour, 10)
    eq_(endtime.minute, 0)

# 数字でタイマー
def test_get_timer_num():
    h = timerlist.get_timer('10', '')
    endtime = h['endtime']
    target = datetime.datetime.now() + datetime.timedelta(minutes=10)
    eq_(endtime.minute, target.minute)

def test_get_timer_second():
    h = timerlist.get_timer('10s', '')
    endtime = h['endtime']
    target = datetime.datetime.now() + datetime.timedelta(seconds=10)
    eq_(endtime.second, target.second)

def test_get_timer_minute():
    h = timerlist.get_timer('10m', '')
    endtime = h['endtime']
    target = datetime.datetime.now() + datetime.timedelta(minutes=10)
    eq_(endtime.minute, target.minute)

def test_get_timer_hour():
    h = timerlist.get_timer('10h', '')
    endtime = h['endtime']
    target = datetime.datetime.now() + datetime.timedelta(hours=10)
    eq_(endtime.hour, target.hour)

def test_get_timer_hourminute():
    h = timerlist.get_timer('10h 10m', '')
    endtime = h['endtime']
    target = datetime.datetime.now() + datetime.timedelta(hours=10) + datetime.timedelta(minutes=10)
    eq_(endtime.hour, target.hour)
    eq_(endtime.minute, target.minute)

def test_get_timer_hourminutesecond():
    h = timerlist.get_timer('10h 10m 10s', '')
    endtime = h['endtime']
    target = datetime.datetime.now() + datetime.timedelta(hours=10) + datetime.timedelta(minutes=10) + datetime.timedelta(seconds=10)
    eq_(endtime.hour, target.hour)
    eq_(endtime.minute, target.minute)
    eq_(endtime.second, target.second)

def test_get_timedelta_dict():
    eq_(timerlist._get_timedelta_dict('10s 20h 30m'), {'h': 20, 'm': 30, 's': 10})
    eq_(timerlist._get_timedelta_dict('10s30m'), {'h': 0, 'm': 30, 's': 10})
    eq_(timerlist._get_timedelta_dict('10s 30s'), {'h': 0, 'm': 0, 's': 40})

def test_get_maxindex():
    eq_(timerlist._get_maxindex({1: 'a', 3: 'c', 2: 'b'}), 3)
    eq_(timerlist._get_maxindex({'': 'a', 2: 'c', 3: 'b'}), 0)
    eq_(timerlist._get_maxindex({'': 'a'}), 0)
    eq_(timerlist._get_maxindex({}.keys()), 0)
    eq_(timerlist._get_maxindex(None), 0)
