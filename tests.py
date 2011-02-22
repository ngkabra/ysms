"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""
import unittest
from django.test import TestCase

class TestBasic(TestCase):
    fixtures = ['ysms.json',]
    def test_basic(self):
        a = 1
        self.assertEqual(1, a)
        
'''class TestBasic(unittest.TestCase):
    "Basic tests"
    fixtures = ['/ysms/fixtures/sam.json']
    def test_basic(self):
        a = 1
        self.assertEqual(1, a)

    def test_basic_2(self):
        a = 1
        assert a == 1'''

