# -*- coding: utf-8 -*-
"""
    Copyright (c) Dario Götz and Jörg Christian Reiher.
    All rights reserved.
"""
import json


class PythonSQLAdapter(object):
    py2sql = {type(None): 'NULL',
              bool:       'BOOL',
              int:        'INTEGER',
              float:      'REAL',
              long:       'INTEGER',
              str:        'TEXT',
              unicode:    'TEXT',
              dict:       'JSON'}

    @staticmethod
    def _json_adapter(d):
        return json.dumps(d)

    @staticmethod
    def _json_converter(s):
        return json.loads(s)


    @staticmethod
    def _bool_adapter(b):
        return int(b)

    @staticmethod
    def _bool_converter(i):
        return i==1

    def __init__(self):
        self.adapter = {bool: self._bool_adapter,
                        dict: self._json_adapter}

        self.converter = {'BOOL': self._bool_converter,
                          'JSON': self._json_converter}
        return
