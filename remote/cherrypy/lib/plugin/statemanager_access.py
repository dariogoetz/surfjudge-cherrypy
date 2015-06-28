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


    def start(self):
        self.bus.log('Setting up statemanager access resources')
        self.bus.subscribe(KEY_ENGINE_SM_ACTIVATE_HEAT, self.activate_heat)
        self.bus.subscribe(KEY_ENGINE_SM_DEACTIVATE_HEAT, self.deactivate_heat)
        self.bus.subscribe(KEY_ENGINE_SM_GET_ACTIVE_HEAT_INFO, self.get_active_heat_info)
        self.bus.subscribe(KEY_ENGINE_SM_GET_HEATS_FOR_JUDGE, self.get_heats_for_judge)

        return

    def stop(self):
        self.bus.log('Freeing statemanager access resources')
        self.bus.unsubscribe(KEY_ENGINE_SM_ACTIVATE_HEAT, self.activate_heat)
        self.bus.unsubscribe(KEY_ENGINE_SM_DEACTIVATE_HEAT, self.deactivate_heat)
        self.bus.unsubscribe(KEY_ENGINE_SM_GET_ACTIVE_HEAT_INFO, self.get_active_heat_info)
        self.bus.unsubscribe(KEY_ENGINE_SM_GET_HEATS_FOR_JUDGE, self.get_heats_for_judge)

        return


    def activate_heat(self, heat_id, heat_info):
        res = self.statemanager.activate_heat(heat_id, heat_info)
        return res

    def deactivate_heat(self, heat_id):
        res = self.statemanager.deactivate_heat(heat_id)
        return res

    def get_active_heat_info(self, heat_id):
        res = self.statemanager.get_active_heat_info(heat_id)
        return res

    def get_heats_for_judge(self, judge_id):
        res = self.statemanager.get_heats_for_judge(judge_id)
        return res
