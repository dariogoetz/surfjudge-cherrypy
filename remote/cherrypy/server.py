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


        # Load cherrypy plugins/tools
        self._load_plugins(params)

        # Tools
        self._load_tools()

        # Mount applications
        self._load_applications()

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
        return


    def _load_applications(self):
        # Main SurfJudge app
        from remote.cherrypy.controller.surfjudge import SurfJudgeWebInterface

        mount_loc = '/'
        sj_web_interface = SurfJudgeWebInterface()
        conf_path = os.path.join(self.conf_path, _CONFIG['config_files']['SurfJudgeWebInterface'])
        app = self.mount_app(sj_web_interface, mount_loc, conf_path)
        self.make_rotate_logger(app)


        # User Authentication app
        from remote.cherrypy.controller.user_auth import AuthenticationController
        mount_loc = '/auth/'
        auth_contoller = AuthenticationController(mount_loc)
        conf_path = os.path.join(self.conf_path, _CONFIG['config_files']['AuthenticationController'])
        app = self.mount_app(auth_contoller, mount_loc, conf_path)
        return



    def get_config(self, filename = None):
        # Later, this can be used to construct
        # more complicated config files/dicts
        return filename

    def mount_app(self, app, mount_point, config_file = None):
        config = self.get_config(config_file)
        app = cherrypy.tree.mount(app, mount_point, config = config)
        return app




    def make_rotate_logger(self, app):
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
