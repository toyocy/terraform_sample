#!/usr/bin/python3
# -*- coding: utf-8 -*-

import unittest
import sys
from scripts.create_doc import fetch_tfstate
import io


class TestCreateDoc(unittest.TestCase):
    maxDiff = None

    def setup(self):
      sys.stdout = io.StringIO()

    def tearDown(self):
      sys.stdout = sys.__stdout__
      
    def test_should_exist_tfstate(self):
        fetch_tfstate('')
        actual = "tfstate ファイルが存在しません。terraform apply を実行してください。\n"
        self.assertEqual(sys.stdout.getvalue(), actual)
