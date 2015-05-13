import os
import cherrypy

from ..lib.access_conditions import *
from . import CherrypyWebInterface

from keys import *

ENCODING = 'utf-8'

class AuthenticationController(CherrypyWebInterface):
    '''
    Manages the login of users.
    '''


    # TODO: HTML error messages
    # TODO: make available only by POST
    # TODO: return HTML messages? or json?

    @cherrypy.expose
    def do_login(self, username = None, password = None):
        if username is None or password is None:
            return False

        username = username.encode(ENCODING)
        password = password.encode(ENCODING)
        check_okay = cherrypy.engine.publish(KEY_ENGINE_USER_LOGIN, username, password).pop(0)
        if check_okay:
            # Regenerate session cookie against session fixation attacks.
            cherrypy.session.regenerate()
            # Since authentication was successful, the session
            # will be stored by writing the username and his information
            # (roles etc.) to it.

            user_info = cherrypy.engine.publish(KEY_ENGINE_USER_INFO, username).pop()
            cherrypy.session[KEY_USERNAME] = username
            cherrypy.session[KEY_USER_INFO] = user_info

            return True
        else:
            return False


    @cherrypy.expose
    def do_logout(self):
        username = cherrypy.session.get(KEY_USERNAME)
        if username is None:
            return True
        else:
            username = username.encode(ENCODING)
            res = cherrypy.engine.publish(KEY_ENGINE_USER_LOGOUT, username).pop()
            del cherrypy.session[KEY_USERNAME]
            del cherrypy.session[KEY_USER_INFO]
            cherrypy.request.login = None
            cherrypy.request.user_info = None
            return res


    @cherrypy.expose
    @require(is_admin())
    def do_register(self, username = None, password = None, roles = None):
        if username is None or password is None:
            return False
        username = username.encode(ENCODING)
        password = password.encode(ENCODING)
        successful = cherrypy.engine.publish(KEY_ENGINE_USER_REGISTER, username, password, roles).pop()
        return successful




    #######################################################################
    #### HTML resources #########
    #######################################################################


    # functions as website as well as POST request leading to website, if unsuccessful
    @cherrypy.expose
    @cherrypy.tools.render(template = 'authentication/login_form.html')
    def login(self, username = None, password = None, from_page = '/'):
        env = self._standard_env()
        message = ''
        if cherrypy.request.method == 'POST':
            successful = self.do_login(username, password)
            if successful:
                raise cherrypy.HTTPRedirect(from_page)
            else:
                message = 'Login unsuccessful!'

        env['message']     = message
        env['from_page']   = from_page
        env['post_action'] = self.mount_location + '/' + 'login'
        return env



    # functions as website as well as POST request leading to website, if unsuccessful
    @cherrypy.expose
    @cherrypy.tools.render(template = 'authentication/register.html')
    def register(self, username = None, password = None, as_admin = False):
        env = self._standard_env()

        logged_in = env['global_logged_in']
        is_admin = env['global_is_admin']

        message = ''
        if cherrypy.request.method == 'POST':
            if as_admin and not is_admin:
                message = 'Only admins can register admins.'
            else:
                roles = []
                if as_admin:
                    roles.append(KEY_ROLE_ADMIN)

                successful = self.do_register(username, password, roles)
                if successful:
                    msg = 'User "{}" registered successfully!'.format(username)
                    raise cherrypy.HTTPRedirect('/simple_message?msg={}'.format(msg) )
                else:
                    message = 'Register unsuccessful!'

        env['message']     = message
        env['post_action'] = self.mount_location + '/' + 'register'
        return env


    # TODO: make accessible through POST action?
    @cherrypy.expose
    @cherrypy.tools.render(template = 'authentication/logged_out.html')
    def logout(self):
        message = ''
        successful = self.do_logout()
        if successful:
            message = 'Logout successful!'
        else:
            message = 'Logout unsuccessful!'

        env = self._standard_env()
        print message
        env['message'] = message
        return env
