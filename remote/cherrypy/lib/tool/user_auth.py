
import cherrypy

KEY_USERNAME = '_cp_username'
KEY_ENGINE_ROLE_LOOKUP = 'lookup-user-info'

LOGIN_PAGE = '/auth/login'


class UserAuthenticationTool(cherrypy.Tool):
    '''
    Tool to do user authentication.
    '''

    def __init__(self):
        cherrypy.Tool.__init__(self, 'before_handler',
                               self._get_user_info,
                               priority = 10)
        return


    def _get_user_info(self):
        '''
        Check the requested page's conditions against the
        user's information.


        If the user is not logged in or the requested page's
        conditions are not met, the user gets redirected to
        the login page.
        '''

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
        from_page = 'from_page={}'.format(cherrypy.lib.httputil.urllib.quote(cherrypy.request.path_info))

        # Check if the user is logged in on the webserver.
        if username is None:
            raise cherrypy.HTTPRedirect(LOGIN_PAGE + '?' + from_page)

        uname_str = 'username={}'.format(username)
        user_info = cherrypy.engine.publish(KEY_ENGINE_ROLE_LOOKUP, username).pop()

        # Check if the user is logged in at the user manager.
        if user_info is None:
            msg = 'msg={}'.format('User "{}" not logged in.'.format(username))
            del cherrypy.session[KEY_USERNAME]
            raise cherrypy.HTTPRedirect(LOGIN_PAGE + '?' + '&'.join([uname_str, from_page, msg]) )


        # User is still logged in, so credentials were okay.
        # Hence the request body gets the field "login" populated.
        # Moreover, we add some information about the user on
        # which the conditions will work.
        cherrypy.request.login = username
        cherrypy.request.user_info = user_info

        # Check if the requested page's conditions are met.

        for condition in conditions:
            if not condition():
                msg = 'msg={}'.format('Insufficient rights to access page.')
                raise cherrypy.HTTPRedirect(LOGIN_PAGE + '?' + '&'.join( [uname_str, from_page, msg]) )

        # Everything is okay.
        return

