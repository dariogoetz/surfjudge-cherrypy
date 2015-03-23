import threading
import time

from statemanager import StateManager
from remote.remote_interface import RemoteInterface
from database.database import SQLiteDatabaseHandler

from remote.cherrypy.server import Server as CherryPyServer
import threading

class SurfJudge(object):
    '''Base SurfJudge Object

    Handles the main functionalities.'''

    def __init__(self):

        self.__database = SQLiteDatabaseHandler()
        self.__interface = RemoteInterface()
        self.__statemanager = StateManager()

        return


    @property
    def database(self):
        return self.__database

    @property
    def interface(self):
        return self.__interface

    @property
    def statemanager(self):
        return self.__statemanager

    def shutdown(self):
        self.interface.shutdown()
        self.database.shutdown()

def doit(args):
    surfjudge = SurfJudge()

    if args.webserver:
        cpserver = CherryPyServer(user_manager = surfjudge.interface.user_manager, database = surfjudge.database, port = args.port)
        surfjudge.interface.add_server(cpserver)

    # start console

    # main loop
    # run code until all interfaces are shut down
    while threading.active_count() > 0:
        try:
            time.sleep(0.1)
        except KeyboardInterrupt:
            surfjudge.shutdown()
            break



if __name__ == "__main__":
    import sys, argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--webserver", action='store_true', help='Start webserver. (Default: True)')
    parser.add_argument("--port", type=int, default=80, help="Port to be used by webserver")
    args = parser.parse_args()


    doit(args)
