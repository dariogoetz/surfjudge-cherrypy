import os
import cherrypy

from remote.cherrypy.lib.access_conditions import *

KEY_ENGINE_USER_LOGIN = 'login-user'
KEY_ENGINE_USER_LOGOUT = 'logout-user'
KEY_ENGINE_USER_REGISTER = 'register-user'
KEY_USERNAME = '_cp_username'

class AuthenticationController(object):
    '''
    Manages the login of users.
    '''

    def __init__(self, mount_location):
        self.mount_location = mount_location
        pass


    @cherrypy.expose
    def do_login(self, username = None, password = None, from_page = '/'):
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
            raise cherrypy.HTTPRedirect(from_page)
        else:
            raise cherrypy.HTTPRedirect( os.path.join(self.mount_location, 'login?from_page={}&msg={}'.format(from_page, 'Wrong credentials.')) )

    @cherrypy.expose
    @cherrypy.tools.render(template = 'authentication/logged_out.html')
    def do_logout(self):
        username = cherrypy.session.get(KEY_USERNAME)
        print 'loggin out', username
        if username is not None:
            res = cherrypy.engine.publish(KEY_ENGINE_USER_LOGOUT, username).pop()
            cherrypy.request.login = None

        cherrypy.session[KEY_USERNAME] = None
        return {}


    @cherrypy.expose
    @require(is_admin())
    @cherrypy.tools.render(template = 'authentication/logged_out.html')
    def do_logout_user(self, username = None):
        if username is None:
            return {}

        res = cherrypy.engine.publish(KEY_ENGINE_USER_LOGOUT, username).pop()
        # If the user to be logged out is of this session,
        # log out session as well
        session_user = cherrypy.session.get(KEY_USERNAME, None)
        if username == session_user:
            cherrypy.session[KEY_USERNAME] = None
            if session_user:
                cherrypy.request.login = None
        return {}

    @cherrypy.expose
    @require(is_admin())
    @cherrypy.tools.render(template = 'authentication/registered.html')
    def do_register_user(self, username = None, password = None):
        if username is None or password is None:
            return {'message': 'Insufficient information for registration.'}
        successful = cherrypy.engine.publish(KEY_ENGINE_USER_REGISTER, username, password).pop()

        return {'message': 'User "{}" registered successful!'.format(username)}



    @cherrypy.expose
    @cherrypy.tools.render(template = 'authentication/login_form.html')
    def login(self, username = None, from_page = '/', msg = None):
        message = 'Please login!'
        if msg is not None:
            message += ' ({})'.format(msg)
        env = {}
        env['username']    = username
        env['message']     = message
        env['from_page']   = from_page
        env['post_action'] = os.path.join(self.mount_location, 'do_login')
        return env
