import os
import cherrypy
import json

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
            if KEY_ROLE_JUDGE in user_info.get(KEY_ROLES):
                judge_ids = cherrypy.engine.publish(KEY_ENGINE_DB_RETRIEVE_JUDGE_ID_FOR_USERNAME, username).pop()
                if len(judge_ids) > 0:
                    cherrypy.session[KEY_JUDGE_ID] = judge_ids[0]['id']

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



    @cherrypy.expose
    @require(has_all_roles(KEY_ROLE_ADMIN))
    def do_get_logins(self, **kwargs):
        logins = cherrypy.engine.publish(KEY_ENGINE_USER_GET_USERS).pop()
        res = []
        for login, data in logins.items():
            d = {}
            d.update(data)
            d['username'] = login
            del d['password']
            res.append(d)
        return json.dumps(res)


    @cherrypy.expose
    @require(is_admin())
    def do_modify_login(self, old_username=None, new_username=None, username=None, roles=None, **kwargs):
        if username is not None and roles is not None:
            roles = json.loads(roles)
            res = cherrypy.engine.publish(KEY_ENGINE_USER_SET_ROLES, username, roles).pop()
        if old_username is not None and new_username is not None:
            res = cherrypy.engine.publish(KEY_ENGINE_USER_RENAME, old_username, new_username).pop()
        return

    @cherrypy.expose
    @require(is_admin())
    def do_delete_login(self, username=None, **kwargs):
        if username is None:
            return
        res = cherrypy.engine.publish(KEY_ENGINE_USER_DELETE, username).pop()
        return

    #######################################################################
    #### HTML resources #########
    #######################################################################



    @cherrypy.expose
    @require(has_all_roles(KEY_ROLE_ADMIN))
    @cherrypy.tools.render(template='/tournament_admin/edit_logins.html')
    @cherrypy.tools.relocate()
    def logins(self, **kwargs):
        data = self._standard_env()
        return data


    # functions as website as well as POST request leading to website, if unsuccessful
    @cherrypy.expose
    @cherrypy.tools.render(template = 'authentication/login_form.html')
    def login(self, username = None, password = None, from_page = '/judge_hub'):
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
    def register(self, username = None, password = None):
        env = self._standard_env()

        logged_in = env['global_logged_in']

        message = u''
        if cherrypy.request.method == 'POST':
            roles = []
            successful = self.do_register(username, password, roles)
            if successful:
                msg = u'User "{}" registered successfully!'.format(username)
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
        message = u''
        successful = self.do_logout()
        if successful:
            message = 'Logout successful!'
        else:
            message = 'Logout unsuccessful!'

        env = self._standard_env()
        raise cherrypy.HTTPRedirect('/auth/login')
