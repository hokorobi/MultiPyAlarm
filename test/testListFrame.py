#coding=UTF-8
from nose.tools import *
import datetime

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import listframe

def test__get_listbox_left():
    h1 = datetime.timedelta(hours=1)
    eq_(listframe._get_listbox_left(h1), '01:00:00')
    h2 = datetime.timedelta(hours=1, minutes=1)
    eq_(listframe._get_listbox_left(h2), '01:01:00')
    h3 = datetime.timedelta(hours=1, minutes=1, seconds=1)
    eq_(listframe._get_listbox_left(h3), '01:01:01')
    h4 = datetime.timedelta(days=1)
    eq_(listframe._get_listbox_left(h4), '1d 00:00')
    h5 = datetime.timedelta(minutes=1)
    eq_(listframe._get_listbox_left(h5), '01:00')
    h6 = datetime.timedelta(seconds=1)
    eq_(listframe._get_listbox_left(h6), '00:01')
    h7 = datetime.timedelta(days=1, hours=1)
    eq_(listframe._get_listbox_left(h7), '1d 01:00:00')
