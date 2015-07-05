import cherrypy
import json
from ..lib.access_conditions import *

from keys import *

class CherrypyWebInterface(object):
    def __init__(self, mount_location = '/'):
        self.mount_location = mount_location
        return


    def _standard_env(self):
        env = {}
        env['mount_loc'] = self.mount_location
        username = cherrypy.session.get(KEY_USERNAME)
        env['global_username'] = username

        ui = cherrypy.session.get(KEY_USER_INFO)
        if ui is None:
            ui = cherrypy.engine.publish(KEY_ENGINE_USER_INFO, username).pop()
        if ui is None:
            ui = {}

        roles = ui.get(KEY_ROLES, [])
        env['global_is_admin'] = KEY_ROLE_ADMIN in roles
        env['global_is_commentator'] = KEY_ROLE_COMMENTATOR in roles
        env['global_is_judge'] = KEY_ROLE_JUDGE in roles
        env['global_is_headjudge'] = KEY_ROLE_HEADJUDGE in roles
        env['global_logged_in'] = bool(username)
        return env


    def render_html(self, context = None, template = None):
        if context is None:
            context = {}
        env = self._standard_env()
        env.update(context)

        if template:
            tpl = cherrypy.engine.publish(KEY_ENGINE_LOOKUP_TEMPLATE, template).pop()
        else:
            tpl = None

        # Render the template into the response body
        if tpl:
            return tpl.render(**env)
        else:
            return env


