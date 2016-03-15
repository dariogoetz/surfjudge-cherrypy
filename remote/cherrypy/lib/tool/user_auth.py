import cherrypy

from keys import *

LOGIN_PAGE = '/auth/login'

class Relocate(cherrypy.Tool):
    '''
    Sets relocation request if authentication fails.
    '''

    def __init__(self):
        cherrypy.Tool.__init__(self, 'before_handler',
                               self._set_relocation,
                               priority = 10)
        return

    def _set_relocation(self):
        print 'requesting relocation'
        cherrypy.request.config['auth.relocate'] = True


class UserAuthenticationTool(cherrypy.Tool):
    '''
    Tool to do user authentication.
    '''

    def __init__(self):
        cherrypy.Tool.__init__(self, 'before_handler',
                               self._get_user_info,
                               priority = 20)
        return


    def _get_user_info(self):
        '''
        Check the requested page's conditions against the
        user's information.


        If the user is not logged in or the requested page's
        conditions are not met, the user gets redirected to
        the login page.
        '''

        relocate = cherrypy.request.config.get('auth.relocate', False)

        # Check if there are conditions and get them
        # The field "auth.require" in the request config
        # gets written by the "require" function.
        conditions = cherrypy.request.config.get('auth.require', [])
        if len(conditions) == 0:
            return


        # Check if user already logged in
        # alternatively, if sessions should not be used,
        # one could check for cherrypy.request.login or the like
        username = cherrypy.session.get(KEY_USERNAME)
        user_info = cherrypy.session.get(KEY_USER_INFO)


        ## The following could maybe be used if the standard
        ## authentication method would be used. Then the field
        ## cherrypy.request.login is populated with the username.
        #if username is None:
        #    username = cherrypy.request.login

        # KNOWN_ISSUE:
        # the from_page looses all its parameters
        # adding it with cherrypy.request.query_string
        # interprets the old parameters as new ones
        # in the page handler where it is redirected to.
        #from_page = 'from_page={}'.format(cherrypy.lib.httputil.urllib.quote(cherrypy.request.path_info))
        #print from_page
        # try alternatively
        from_page = 'from_page={}'.format(cherrypy.lib.httputil.urllib.quote(cherrypy.request.request_line.split()[1]))

        # Check if the user is logged in on the webserver.
        if username is None:
            if relocate:
                raise cherrypy.HTTPRedirect(LOGIN_PAGE + '?' + from_page)
            else:
                raise cherrypy.HTTPError(status=403, message='auth: No username given')

        uname_str = 'username={}'.format(username)
        if user_info is None: # for whatever reason, the session has no user_info
            user_info = cherrypy.engine.publish(KEY_ENGINE_USER_INFO, username).pop()

        # Check if the user is logged in at the user manager.
        if user_info is None:
            msg = 'msg={}'.format('User "{}" not logged in.'.format(username))
            del cherrypy.session[KEY_USERNAME]
            if relocate:
                raise cherrypy.HTTPRedirect(LOGIN_PAGE + '?' + '&'.join([uname_str, from_page, msg]) )
            else:
                raise cherrypy.HTTPError(status=403, message='auth: User not logged in')


        # User is still logged in, so credentials were okay.
        # Hence the request body gets the field "login" populated.
        # -> will be read by access_conditions
        # Moreover, we add some information about the user on
        # which the conditions will work.
        cherrypy.request.login = username
        cherrypy.request.user_info = user_info

        # Check if the requested page's conditions are met.

        for condition in conditions:
            if not condition():
                if relocate:
                    msg = 'msg={}'.format('Insufficient rights to access page.')
                    raise cherrypy.HTTPRedirect(LOGIN_PAGE + '?' + '&'.join( [uname_str, from_page, msg]) )
                else:
                    raise cherrypy.HTTPError(status=403, message='auth: Insufficient rights')

        # Everything is okay.
        return
