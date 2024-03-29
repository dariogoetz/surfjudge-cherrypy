# -*- coding: utf-8 -*-
"""
    Copyright (c) Dario Götz and Jörg Christian Reiher.
    All rights reserved.
"""
from configobj import ConfigObj
from validate import Validator, ValidateError

class Config(ConfigObj):
    '''
    Wrapper around ConfigObj
    '''


    @staticmethod
    def _eval_check(to_eval):
        try:
            res = eval(to_eval)
        except:
            raise ValidateError('Config parser: Could not evaluate "{}"'.format(to_eval))
        return res

    @staticmethod
    def _int_check(to_check):
        try:
            res = int(float(to_check))
        except:
            raise ValidateError('Config parser: Could not parse int "{}"'.format(to_check))
        return res

    @staticmethod
    def _path_check(to_check):
        import os
        try:
            res = os.path.normpath(to_check)
        except:
            raise ValidateError('Config parser: Could not parse path "{}"'.format(to_check))
        return res

    MODULE_SEPARATOR = '.'
    def __init__(self, module = None, config = None, configspec = None, **kwargs):
        if configspec is not None:
            configspec = configspec
        else:
            configspec = self._module_to_path(module)

        super(Config, self).__init__(infile = config, configspec = configspec,  **kwargs)

        self.config_filename = config

        additional_checks = {'eval': self._eval_check,
                             'int':  self._int_check,
                             'path': self._path_check}

        validator = Validator(additional_checks)
        self.validate(validator)

        return


    def _module_to_path(self, module):
        import os
        return module.replace(self.MODULE_SEPARATOR, os.path.sep) + '.ini'

