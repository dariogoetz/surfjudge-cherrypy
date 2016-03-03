import cherrypy

from cherrypy.process import plugins
from keys import *

class JudgingManagerPlugin(plugins.SimplePlugin):
    '''
    A WSBPlugin that is responsible for communicating with the
    StateManager of SurfJudge object.
    '''

    def __init__(self, bus, judging_manager):
        plugins.SimplePlugin.__init__(self, bus)

        self.judging_manager = judging_manager


    def start(self):
        self.bus.log('Setting up judging_manager access resources')
        self.bus.subscribe(KEY_ENGINE_JM_REGISTER_JUDGING_REQUEST, self.register_judging_request)
        self.bus.subscribe(KEY_ENGINE_JM_UNREGISTER_JUDGING_REQUEST, self.unregister_judging_request)
        self.bus.subscribe(KEY_ENGINE_JM_GET_JUDGING_REQUESTS, self.get_judging_requests)

        return

    def stop(self):
        self.bus.log('Freeing judging_manager access resources')
        self.bus.unsubscribe(KEY_ENGINE_JM_REGISTER_JUDGING_REQUEST, self.register_judging_request)
        self.bus.unsubscribe(KEY_ENGINE_JM_UNREGISTER_JUDGING_REQUEST, self.unregister_judging_request)
        self.bus.unsubscribe(KEY_ENGINE_JM_GET_JUDGING_REQUESTS, self.get_judging_requests)
        return


    def register_judging_request(self, judge_id, heat_id, expire_s):
        return self.judging_manager.register_judging_request(judge_id, heat_id, expire_s=expire_s)

    def unregister_judging_request(self, heat_id, expire_s):
        return self.judging_manager.register_judging_request(judge_id, heat_id)

    def get_judging_requests(self, heat_id):
        return self.judging_manager.get_judging_requests(heat_id)
