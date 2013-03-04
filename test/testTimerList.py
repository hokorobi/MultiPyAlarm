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

def test_split_digit_char():
    eq_(timerlist.split_digit_char('10h 10m 10s'), ['10', 'h', '10', 'm', '10', 's'])
    eq_(timerlist.split_digit_char('10h10m10s'), ['10', 'h', '10', 'm', '10', 's'])
    eq_(timerlist.split_digit_char('10h10h10s'), ['10', 'h', '10', 'h', '10', 's'])
