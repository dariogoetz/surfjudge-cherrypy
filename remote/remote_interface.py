import threading

#from remote.cherrypy.server import Server


from .user_manager import UserManager
from .judging_manager import JudgingManager

class RemoteInterface(object):
    '''
    Provides the remote interface to the users.

    May be XML-RPC or webserver.
    '''

    def __init__(self):
        self.__servers = []
        self.__user_manager = UserManager()
        self.__judging_manager = JudgingManager()
        self.__threads = []
        return


    @property
    def user_manager(self):
        return self.__user_manager

    @property
    def judging_manager(self):
        return self.__judging_manager

    @property
    def threads(self):
        return self.__threads

    def add_server(self, server):
        self.__servers.append(server)
        t = threading.Thread(target = server.run)
        self.__threads.append(t)
        t.start()
        return


    def shutdown(self):
        for s in self.__servers:
            s.shutdown()

