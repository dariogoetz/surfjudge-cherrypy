import cherrypy
from ..lib.access_conditions import *

KEY_ENGINE_USER_LOGIN = 'login-user'
KEY_ENGINE_USER_LOGOUT = 'logout-user'
KEY_ENGINE_USER_REGISTER = 'register-user'
KEY_ENGINE_USER_INFO = 'lookup-user-info'
KEY_USERNAME = '_cp_username'


class SurfJudgeWebInterface(object):
    def __init__(self):
        pass


    def _populate_standard_env(self):
        env = {}
        username = cherrypy.session.get(KEY_USERNAME)
        env['global_username'] = username

        ui = cherrypy.engine.publish(KEY_ENGINE_USER_INFO, username).pop()
        env['global_is_admin'] = ui and KEY_ROLE_ADMIN in ui.get(KEY_ROLES)

        env['global_logged_in'] = True if username else False
        return env



    @cherrypy.expose
    #@require(is_admin())
    @cherrypy.tools.render(template = 'test_bootstrap_advanced.html')
    def index(self):
        context = self._populate_standard_env()

        if context['global_username']:
            message = 'Why, you again...? Welcome back, {}!'.format(context['global_username'])
        else:
            message = 'Welcome.'

        context['title'] = 'Cool Jinja2-rendered file'
        context['description'] = 'Some description of this awesome file'
        context['message'] = message
        return context


    @cherrypy.expose
    @require(is_admin()) # at the moment, everyone is admin
    @cherrypy.tools.render(template='judge_panel.html')
    def judge_panel(self):
        data = {}
        data['judge_name'] = 'Christian'
        data['judge_number'] = '1234'
        data['surfer_colors'] = ['red', 'blue']
        data['n_surfers'] = len(data['surfer_colors'])
        return data


    @cherrypy.expose
    #@require(is_admin())
    def javascript_request(self, parameter = None):
        #database request
        #store in some variable
        #return the variable
        result = 'hallo'
        return result


    @cherrypy.expose
    @cherrypy.tools.render(template = 'simple_message.html')
    def simple_message(self, msg = None):
        env = {}
        env['message'] = msg
        return env
