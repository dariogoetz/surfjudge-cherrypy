import cherrypy

from cherrypy.process import plugins
from keys import *

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
        self.bus.subscribe(KEY_ENGINE_USER_INFO, self.get_user_info)
        self.bus.subscribe(KEY_ENGINE_USER_LOGIN,  self.login_user)
        self.bus.subscribe(KEY_ENGINE_USER_LOGOUT, self.logout_user)
        self.bus.subscribe(KEY_ENGINE_USER_REGISTER, self.register_user)
        self.bus.subscribe(KEY_ENGINE_USER_ADD_ROLE, self.add_role_to_user)
        self.bus.subscribe(KEY_ENGINE_USER_REMOVE_ROLE, self.remove_role_from_user)
        self.bus.subscribe(KEY_ENGINE_USER_GET_USERS, self.get_users)
        return

    def stop(self):
        self.bus.log('Freeing user management resources')
        self.bus.unsubscribe(KEY_ENGINE_USER_INFO, self.get_user_info)
        self.bus.unsubscribe(KEY_ENGINE_USER_LOGIN,  self.login_user)
        self.bus.unsubscribe(KEY_ENGINE_USER_LOGOUT, self.logout_user)
        self.bus.unsubscribe(KEY_ENGINE_USER_REGISTER, self.register_user)
        self.bus.unsubscribe(KEY_ENGINE_USER_ADD_ROLE, self.add_role_to_user)
        self.bus.unsubscribe(KEY_ENGINE_USER_REMOVE_ROLE, self.remove_role_from_user)
        self.bus.unsubscribe(KEY_ENGINE_USER_GET_USERS, self.get_users)
        return


    def get_user_info(self, username):
        info = self.user_manager.get_user_info(username)
        return info

    def login_user(self, username, password):
        return self.user_manager.login_user(username, password)

    def logout_user(self, username):
        return self.user_manager.logout_user(username)

    def register_user(self, username, password, roles):
        return self.user_manager.register_user(username, password, roles)

    def add_role_to_user(self, username, role):
        return self.user_manager.add_role_to_user(username, role)

    def remove_role_from_user(self, username, role):
        return self.user_manager.remove_role_from_user(username, role)

    def get_users(self):
        return self.user_manager.get_users()
