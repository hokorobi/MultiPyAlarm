#coding=UTF-8
from nose.tools import *
import datetime

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from MultiPyAlarm import TimerList

# 文字列はエラー
def test_get_timer_string():
    eq_(TimerList.get_timer('a', ''), None)

# nn:nn で時間指定タイマー
def test_get_timer_colon():
    h = TimerList.get_timer('10:00', '')
    endtime = h['endtime']
    eq_(endtime.hour, 10)
    eq_(endtime.minute, 0)

# 数字でタイマー
def test_get_timer_num():
    h = TimerList.get_timer('10', '')
    endtime = h['endtime']
    target = datetime.datetime.now() + datetime.timedelta(minutes=10)
    eq_(endtime.minute, target.minute)

def test_get_timer_second():
    h = TimerList.get_timer('10s', '')
    endtime = h['endtime']
    target = datetime.datetime.now() + datetime.timedelta(seconds=10)
    eq_(endtime.second, target.second)

def test_get_timer_minute():
    h = TimerList.get_timer('10m', '')
    endtime = h['endtime']
    target = datetime.datetime.now() + datetime.timedelta(minutes=10)
    eq_(endtime.minute, target.minute)

def test_get_timer_hour():
    h = TimerList.get_timer('10h', '')
    endtime = h['endtime']
    target = datetime.datetime.now() + datetime.timedelta(hours=10)
    eq_(endtime.hour, target.hour)

def test_get_timer_hourminute():
    h = TimerList.get_timer('10h 10m', '')
    endtime = h['endtime']
    target = datetime.datetime.now() + datetime.timedelta(hours=10) + datetime.timedelta(minutes=10)
    eq_(endtime.hour, target.hour)
    eq_(endtime.minute, target.minute)

def test_get_timer_hourminutesecond():
    h = TimerList.get_timer('10h 10m 10s', '')
    endtime = h['endtime']
    target = datetime.datetime.now() + datetime.timedelta(hours=10) + datetime.timedelta(minutes=10) + datetime.timedelta(seconds=10)
    eq_(endtime.hour, target.hour)
    eq_(endtime.minute, target.minute)
    eq_(endtime.second, target.second)
