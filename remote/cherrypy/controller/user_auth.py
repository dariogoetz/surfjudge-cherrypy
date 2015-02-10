import os
import cherrypy

from ..lib.access_conditions import *

KEY_ENGINE_USER_LOGIN = 'login-user'
KEY_ENGINE_USER_LOGOUT = 'logout-user'
KEY_ENGINE_USER_REGISTER = 'register-user'
KEY_ENGINE_USER_INFO = 'lookup-user-info'
KEY_USERNAME = '_cp_username'


class AuthenticationController(object):
    '''
    Manages the login of users.
    '''

    def __init__(self, mount_location):
        self.mount_location = mount_location
        pass

    # TODO: HTML error messages
    # TODO: make available only by POST
    # TODO: return HTML messages? or json?

    @cherrypy.expose
    def do_login(self, username = None, password = None):
        if username is None or password is None:
            return False

        check_okay = cherrypy.engine.publish(KEY_ENGINE_USER_LOGIN, username, password).pop(0)
        if check_okay:
            # Regenerate session cookie against session fixation attacks.
            cherrypy.session.regenerate()
            # Since authentication was successful, the request
            # field "login" gets populated. Moreover, the session
            # will be stored by writing some (here "KEY_USERNAME")
            # to it.
            cherrypy.session[KEY_USERNAME] = username
            cherrypy.request.login = username
            return True
        else:
            return False


    @cherrypy.expose
    def do_logout(self):
        username = cherrypy.session.get(KEY_USERNAME)
        if not username:
            return True
        else:
            res = cherrypy.engine.publish(KEY_ENGINE_USER_LOGOUT, username).pop()
            cherrypy.request.login = None
            del cherrypy.session[KEY_USERNAME]
            return True


    @cherrypy.expose
    @require(is_admin())
    def do_logout_user(self, username = None):
        if username is None:
            return True
        else:
            res = cherrypy.engine.publish(KEY_ENGINE_USER_LOGOUT, username).pop()
            # If the user to be logged out is of this session,
            # log out session as well
            session_user = cherrypy.session.get(KEY_USERNAME)
            if username == session_user:
                del cherrypy.session[KEY_USERNAME]
                if session_user:
                    cherrypy.request.login = None
                    cherrypy.request.user_info = None
                return True
            else:
                return True


    @cherrypy.expose
    @require(is_admin())
    def do_register(self, username = None, password = None):
        if username is None or password is None:
            return False
        successful = cherrypy.engine.publish(KEY_ENGINE_USER_REGISTER, username, password).pop()
        return successful




    #######################################################################
    #### HTML resources #########
    #######################################################################

    def _populate_standard_env(self):
        env = {}
        username = cherrypy.session.get(KEY_USERNAME)
        env['global_username'] = username
        ui = None
        if username:
            ui = cherrypy.engine.publish(KEY_ENGINE_USER_INFO, username).pop()
        env['global_is_admin'] = ui and KEY_ROLE_ADMIN in ui.get(KEY_ROLES)
        env['global_logged_in'] = True if username else False
        return env


    @cherrypy.expose
    @cherrypy.tools.render(template = 'authentication/login_form.html')
    def login(self, username = None, password = None, from_page = '/'):
        env = self._populate_standard_env()
        message = ''
        if cherrypy.request.method == 'POST':
            successful = self.do_login(username, password)
            if successful:
                raise cherrypy.HTTPRedirect(from_page)
            else:
                message = 'Login unsuccessful!'

        env['message']     = message
        env['from_page']   = from_page
        env['post_action'] = os.path.join(self.mount_location, 'login')
        return env



    @cherrypy.expose
    @cherrypy.tools.render(template = 'authentication/register.html')
    def register(self, username = None, as_admin = False):
        env = self._populate_standard_env()

        logged_in = env['global_logged_in']
        is_admin = env['global_is_admin']

        message = ''
        if cherrypy.request.method == 'POST':
            if as_admin and not is_admin:
                message = 'Only admins can register admins.'
            else:
                successful = self.do_register(username, as_admin)
                if successful:
                    msg = 'User "{}" registered successfully!'.format(username)
                    raise cherrypy.HTTPRedirect('/simple_message?msg={}'.format(msg) )
                else:
                    message = 'Register unsuccessful!'

        env['message']     = message
        env['post_action'] = os.path.join(self.mount_location, 'register')
        return env


    # TODO: make accessible through POST action?
    @cherrypy.expose
    @cherrypy.tools.render(template = 'authentication/logged_out.html')
    def logout(self):
        message = ''
        if cherrypy.request.method == 'POST':
            successful = self.do_logout()
            if successful:
                message = 'Logout successful!'
            else:
                message = 'Logout unsuccessful!'

        successful = self.do_logout()

        env = self._populate_standard_env()
        env['message'] = message
        return env
