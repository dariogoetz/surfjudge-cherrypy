# -*- coding: utf-8 -*-
"""
    Copyright (c) Dario Götz and Jörg Christian Reiher.
    All rights reserved.
"""
import sys
import logging
from logging import handlers

from config import Config
_CONFIG = Config(__name__)

import os

import cherrypy


class Server(object):
    def __init__(self, **params):

        # Where is the program located
        self.base_dir = os.path.normpath(os.path.abspath(params.get('basedir', _CONFIG['directories']['basedir'])))

        # Config directory
        self.conf_path = os.path.join(self.base_dir, _CONFIG['directories']['config'])

        # Generate log directory
        self.log_path = os.path.join(self.base_dir, _CONFIG['directories']['logs'])
        if not os.path.exists(self.log_path):
            os.mkdir(self.log_path)

        # Update global settings for cherrypy server
        conf_path = os.path.join(self.conf_path, _CONFIG['config_files']['server'])
        cherrypy.config.update(conf_path)

        # set port
        cherrypy.config['server.socket_port'] = params['port']

        # Load cherrypy plugins/tools
        self._load_plugins(params)

        # Tools
        self._load_tools()

        # Mount applications (websites)
        self._load_applications()

        self.configure_logger(cherrypy)

        return


    def shutdown(self):
        cherrypy.engine.exit()

    def run(self):
        engine = cherrypy.engine
        if hasattr(engine, 'signal_handler'):
            engine.signal_handler.subscribe()
        if hasattr(engine, 'console_control_handler'):
            engine.console_control_handler.subscribe()

        engine.start()
        engine.block()
        return


    def _load_tools(self):

        from remote.cherrypy.lib.tool.user_auth import Relocate
        cherrypy.tools.relocate = Relocate()

        from remote.cherrypy.lib.tool.user_auth import UserAuthenticationTool
        cherrypy.tools.session_authenticate = UserAuthenticationTool()


        from remote.cherrypy.lib.tool.jinja_render import JinjaRenderTool
        cherrypy.tools.render = JinjaRenderTool()
        return


    def _load_plugins(self, params):
        engine = cherrypy.engine

        # Jinja template lookup
        from remote.cherrypy.lib.plugin.jinja_lookup import JinjaTemplatePlugin
        tmpl_dir = os.path.join(self.base_dir, _CONFIG['directories']['templates'])
        tmpl_cache_dir = _CONFIG['directories']['template_cache']
        if tmpl_cache_dir is not None:
            tmpl_cache_dir = os.path.join(self.base_dir, tmpl_cache_dir)

        engine.jinja_lookup = JinjaTemplatePlugin(engine, tmpl_dir, tmpl_cache_dir)
        engine.jinja_lookup.subscribe()


        # User management role lookup
        user_manager = params.get('user_manager')
        if user_manager is not None:
            from remote.cherrypy.lib.plugin.user_auth import UserAuthenticationPlugin
            engine.user_auth = UserAuthenticationPlugin(engine, user_manager)
            engine.user_auth.subscribe()
        else:
            raise Exception("User manager is not initialized!")

        # database connect plugin
        db = params.get('database')
        if db is not None:
            from remote.cherrypy.lib.plugin.db_access import DBAccessPlugin
            engine.database = DBAccessPlugin(engine, db)
            engine.database.subscribe()

            # the following makes sure the db thread is restarted when cherrypy restarts
            engine.subscribe('exit', db.shutdown)
        else:
            raise Exception("Database plugin is not initialized!")

        # statemanager connect plugin
        sm = params.get('statemanager')
        if sm is not None:
            from remote.cherrypy.lib.plugin.statemanager_access import StateManagerPlugin
            engine.statemanager = StateManagerPlugin(engine, sm)
            engine.statemanager.subscribe()
        else:
            raise Exception("Statemanager plugin is not initialized!")


        # tournament_manager connect plugin
        tm = params.get('tournament_manager')
        if tm is not None:
            from remote.cherrypy.lib.plugin.tournament_manager_access import TournamentManagerPlugin
            engine.tournament_manager = TournamentManagerPlugin(engine, tm)
            engine.tournament_manager.subscribe()
        else:
            raise Exception("TournamentManager plugin is not initialized!")


        # judging_manager connect plugin
        jm = params.get('judging_manager')
        if jm is not None:
            from remote.cherrypy.lib.plugin.judging_manager_access import JudgingManagerPlugin
            engine.judging_manager = JudgingManagerPlugin(engine, jm)
            engine.judging_manager.subscribe()
        else:
            raise Exception("JudgingManager plugin is not initialized!")

        return


    def _load_applications(self):
        # Main SurfJudge app
        from remote.cherrypy.controller.surfjudge import SurfJudgeWebInterface

        mount_loc = '/'
        sj_web_interface = SurfJudgeWebInterface(mount_loc)
        conf_path = os.path.join(self.conf_path, _CONFIG['config_files']['SurfJudgeWebInterface'])
        app = self.mount_app(sj_web_interface, mount_loc, conf_path)


        # User Authentication app
        from remote.cherrypy.controller.user_auth import AuthenticationController
        mount_loc = '/auth'
        auth_contoller = AuthenticationController(mount_loc)
        conf_path = os.path.join(self.conf_path, _CONFIG['config_files']['AuthenticationController'])
        app = self.mount_app(auth_contoller, mount_loc, conf_path)


        # Tournament admin app
        from remote.cherrypy.controller.tournament_admin import TournamentAdminWebInterface

        mount_loc = '/tournament_admin'
        ta_interface = TournamentAdminWebInterface(mount_loc)
        conf_path = os.path.join(self.conf_path, _CONFIG['config_files']['SurfJudgeWebInterface'])
        app = self.mount_app(ta_interface, mount_loc, conf_path)

        # HeadJudge app
        from remote.cherrypy.controller.head_judge_tools import HeadJudgeWebInterface

        mount_loc = '/headjudge'
        hj_interface = HeadJudgeWebInterface(mount_loc)
        conf_path = os.path.join(self.conf_path, _CONFIG['config_files']['SurfJudgeWebInterface'])
        app = self.mount_app(hj_interface, mount_loc, conf_path)

        return



    def get_config(self, filename = None):
        # Later, this can be used to construct
        # more complicated config files/dicts
        return filename

    def mount_app(self, app, mount_point, config_file = None):
        config = self.get_config(config_file)
        app = cherrypy.tree.mount(app, mount_point, config = config)
        return app




    def configure_logger(self, app):
        # see http://www.cherrypy.org/wiki/Logging#CustomHandlers
        log = app.log

        # Remove the default FileHandlers if present.
        log.error_file = ""
        log.access_file = ""

        maxBytes = getattr(log, "rot_maxBytes", _CONFIG['logger']['max_bytes'])
        backupCount = getattr(log, "rot_backupCount", _CONFIG['logger']['backup_count'])

        # Make a new RotatingFileHandler for the error log.
        default_path = os.path.join(self.log_path, _CONFIG['logger']['error_logfile'])
        fname = getattr(log, "rot_error_file", default_path)
        h = handlers.RotatingFileHandler(fname, 'a', maxBytes, backupCount)
        h.setLevel(logging.DEBUG)
        h.setFormatter(cherrypy._cplogging.logfmt)
        log.error_log.addHandler(h)

        # Make a new RotatingFileHandler for the access log.
        default_path = os.path.join(self.log_path, _CONFIG['logger']['access_logfile'])
        fname = getattr(log, "rot_access_file", default_path)
        h = handlers.RotatingFileHandler(fname, 'a', maxBytes, backupCount)
        h.setLevel(logging.DEBUG)
        h.setFormatter(cherrypy._cplogging.logfmt)
        log.access_log.addHandler(h)

        return
