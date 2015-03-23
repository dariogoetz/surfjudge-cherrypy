import cherrypy

from cherrypy.process import plugins
from keys import *

class StateManagerPlugin(plugins.SimplePlugin):
    '''
    A WSBPlugin that is responsible for communicating with the
    StateManager of SurfJudge object.
    '''

    
    def __init__(self, bus, statemanager):
    plugins.SimplePlugin.__init__(self, bus)

    self.statemanager = statemanager