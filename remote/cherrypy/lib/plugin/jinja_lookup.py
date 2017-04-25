# -*- coding: utf-8 -*-
"""
    Copyright (c) Dario Götz and Jörg Christian Reiher.
    All rights reserved.
"""
import tempfile

import cherrypy
from cherrypy.process import plugins
from keys import *

import jinja2


class JinjaTemplatePlugin(plugins.SimplePlugin):
    '''
    A WSPBus plugin that manages the Jinja2 template lookup.
    '''

    def __init__(self, bus, base_dir = None, base_cache_dir = None,
                 collection_size = 50, encoding = 'utf-8'):
        plugins.SimplePlugin.__init__(self, bus)

        self.base_dir = base_dir

        if base_cache_dir is None:
            base_cache_dir = tempfile.gettempdir()
        self.base_cache_dir = base_cache_dir
        self.encoding = encoding
        self.collection_size = collection_size
        self.lookup = None
        return


    def start(self):
        # Gets called when the cherrypy engine starts and the plugin is loaded
        self.bus.log('Setting up Jinja2 template lookup resources')
        self.loader = jinja2.FileSystemLoader(self.base_dir)
        self.lookup = jinja2.Environment(loader=self.loader)

        self.bus.subscribe(KEY_ENGINE_LOOKUP_TEMPLATE, self.get_template)
        return


    def stop(self):
        self.bus.log('Freeing up Jinja2 template lookup resources.')
        self.bus.unsubscribe(KEY_ENGINE_LOOKUP_TEMPLATE, self.get_template)
        self.lookup = None
        return


    def get_template(self, name):
        '''
        Returns a Jinja2 template by name.
        '''

        return self.lookup.get_template(name)
