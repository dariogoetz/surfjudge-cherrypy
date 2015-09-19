import bcrypt
import threading

from keys import *

from config import Config
_CONFIG = Config(__name__)




class UserManager(object):
    '''
    Provides the user management including check for passwords,
    currently logged in users, their roles, etc.
    '''

    def __init__(self):
        self._critical_section = threading.RLock()


        self.__active_users = {}
        self.__registered_users = None
        self._init_users()

        #self.__encoding = 'utf-8'

        return


    #@property
    #def encoding(self):
    #    return self.__encoding

    @property
    def active_users(self):
        return self.__active_users


    @property
    def registered_users(self):
        return self.__registered_users.keys()


    def check_credentials(self, username, password):
        '''
        Check given password using bcrypt method.

        Returns True if password is correct and False otherwise.
        '''

        if not username or not password:
            return False

        #username = username.encode(self.encoding)
        #password = password.encode(self.encoding)

        hashed_pw = self._get_hashed_pw(username)
        if hashed_pw is None:
            return False
        return bcrypt.hashpw(password, hashed_pw) == hashed_pw



    def get_user_info(self, username):
        '''
        Get the currently active roles for a user.
        If the user is not logged in, "None" is returned.
        '''
        if not username:
            return None
        #username = username.encode(self.encoding)
        return self.active_users.get(username)


    def login_user(self, username, password):
        '''
        Login user at UserManager object.

        Checks credentials and if they are correct,
        stores the user's current roles.
        '''

        if not username or not password:
            return False

        # Refresh list of registered users
        self._init_users(refresh = True)

        #username = username.encode(self.encoding)
        #password = password.encode(self.encoding)

        if username in self.__active_users:
            return True

        if self.check_credentials(username, password):
            roles = self._get_roles_from_state_object(username)
            with self._critical_section:
                self.__active_users[username] = {KEY_ROLES : roles}
            return True
        else:
            return False


    def logout_user(self, username):
        '''
        Logout user at UserManager object.
        '''

        if not username:
            return False
        #username = username.encode(self.encoding)

        if username in self.__active_users:
            with self._critical_section:
                del self.__active_users[username]
        return True


    def register_user(self, username, password, roles = None):
        '''
        Generates a hashed password and stores
        the username with the hashed password.
        '''

        if not username or not password:
            return False

        #username = username.encode(self.encoding)
        #password = password.encode(self.encoding)

        if roles is None:
            roles = []

        with self._critical_section:
            if username in self.__registered_users:
                roles = set(self.__registered_users.setdefault(username, {})[KEY_ROLES]) | set(roles)
            self.__registered_users.setdefault(username, {})[KEY_ROLES] = list(roles)

        hashed_pw = bcrypt.hashpw(password, bcrypt.gensalt())
        self._set_hashed_pw(username, hashed_pw)
        return True


    def _init_users(self, refresh = False):
        if self.__registered_users is None or refresh:
            with self._critical_section:
                self.__registered_users = Config(config =  _CONFIG['users']['users_db'], configspec = _CONFIG['users']['users_db_spec'])
        return


    def _get_roles_from_state_object(self, username):
        '''
        Get the roles that are active for
        the given username in the current state.

        Information is gathered from state object in state manager.
        '''

        if not username:
            return []

        #username = username.encode(self.encoding)
        # TODO: get roles from state object
        return self.__registered_users.get(username, {}).get(KEY_ROLES, [])



    def _get_hashed_pw(self, username):
        '''
        Get the hashed password from users file.
        '''

        if not username:
            return None

        #username = username.encode(self.encoding)

        self._init_users()
        return self.__registered_users.get(username, {}).get(KEY_PASSWORD)


    def _set_hashed_pw(self, username, hashed_pw):
        '''
        Store hashed password in users file.
        '''

        self._init_users()

        with self._critical_section:
            if username in self.__registered_users:
                print('Resetting password for "{}".'.format(username))
            self.__registered_users.setdefault(username, {})[KEY_PASSWORD] = hashed_pw
            self._write_to_disk()


        return


    def _write_to_disk(self):
        with self._critical_section:
            with open(self.__registered_users.config_filename, 'w') as f:
                self.__registered_users.write(f)
        return


    def add_role_to_user(self, username, role):
        if not username in self.__registered_users:
            print 'user manager: user "{}" should be registered as judge but there is no such user'.format(username)
            return False

        with self._critical_section:
            roles = self.__registered_users.setdefault(username, {})[KEY_ROLES]
            if role in roles:
                return True
            self.__registered_users.setdefault(username, {})[KEY_ROLES].append(role)
            self._write_to_disk()
        return True


    def remove_role_from_user(self, username, role):
        if not username in self.__registered_users:
            print 'user manager: user "{}" should be unregistered as judge but there is no such user'.format(username)
            return False

        with self._critical_section:
            roles = self.__registered_users.setdefault(username, {})[KEY_ROLES]
            if role not in roles:
                return True
            self.__registered_users.setdefault(username, {})[KEY_ROLES].remove(role)
            self._write_to_disk()
        return True
