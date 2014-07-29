import cherrypy

from cherrypy.process import plugins

KEY_ENGINE_ROLE_LOOKUP = 'lookup-user-info'
KEY_ENGINE_USER_LOGIN  = 'login-user'
KEY_ENGINE_USER_LOGOUT = 'logout-user'
KEY_ENGINE_USER_REGISTER = 'register-user'

class UserAuthenticationPlugin(plugins.SimplePlugin):
    '''
    A WSBPlugin that is responsible for retrieving currently active
    roles of the users. Communicates with a UserManager object.
    '''

    def __init__(self, bus, user_manager):
        plugins.SimplePlugin.__init__(self, bus)

        self.user_manager = user_manager


    def start(self):
        self.bus.log('Setting up user management resources')
        self.bus.subscribe(KEY_ENGINE_ROLE_LOOKUP, self.get_user_info)
        self.bus.subscribe(KEY_ENGINE_USER_LOGIN,  self.login_user)
        self.bus.subscribe(KEY_ENGINE_USER_LOGOUT, self.logout_user)
        self.bus.subscribe(KEY_ENGINE_USER_REGISTER, self.register_user)
        return

    def stop(self):
        self.bus.log('Freeing user management resources')
        self.bus.unsubscribe(KEY_ENGINE_ROLE_LOOKUP, self.get_user_info)
        self.bus.unsubscribe(KEY_ENGINE_USER_LOGIN,  self.login_user)
        self.bus.unsubscribe(KEY_ENGINE_USER_LOGOUT, self.logout_user)
        self.bus.unsubscribe(KEY_ENGINE_USER_REGISTER, self.register_user)
        return


    def get_user_info(self, username):
        info = self.user_manager.get_user_info(username)
        return info

    def login_user(self, username, password):
        return self.user_manager.login_user(username, password)

    def logout_user(self, username):
        return self.user_manager.logout_user(username)

    def register_user(self, username, password):
        return self.user_manager.register_user(username, password)
