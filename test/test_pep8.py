# -*- coding: utf-8 -*-
from nose.tools import *
import pep8
import glob

def test_pep8():
    pep8style = pep8.StyleGuide()
    result = pep8style.check_files(glob.glob('../*.py'))
    eq_(result.total_errors, 0)
