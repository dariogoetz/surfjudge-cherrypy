import cherrypy

from cherrypy.process import plugins
from keys import *

class TournamentManagerPlugin(plugins.SimplePlugin):
    '''
    A WSBPlugin that is responsible for communicating with the
    TournamentManager of SurfJudge object.
    '''

    def __init__(self, bus, tournament_manager):
        plugins.SimplePlugin.__init__(self, bus)

        self.tournament_manager = tournament_manager


    def start(self):
        self.bus.log('Setting up tournament_manager access resources')
        self.bus.subscribe(KEY_ENGINE_TM_GET_HEAT_ORDER, self.get_heat_order)
        self.bus.subscribe(KEY_ENGINE_TM_SET_HEAT_ORDER, self.set_heat_order)
        self.bus.subscribe(KEY_ENGINE_TM_GET_ADVANCING_SURFERS, self.get_advancing_surfers)
        self.bus.subscribe(KEY_ENGINE_TM_SET_ADVANCING_SURFER, self.set_advancing_surfer)
        self.bus.subscribe(KEY_ENGINE_TM_GENERATE_HEATS, self.generate_heats)

        return

    def stop(self):
        self.bus.log('Freeing tournament_manager access resources')
        self.bus.unsubscribe(KEY_ENGINE_TM_GET_HEAT_ORDER, self.get_heat_order)
        self.bus.unsubscribe(KEY_ENGINE_TM_SET_HEAT_ORDER, self.set_heat_order)
        self.bus.unsubscribe(KEY_ENGINE_TM_GET_ADVANCING_SURFERS, self.get_advancing_surfers)
        self.bus.unsubscribe(KEY_ENGINE_TM_SET_ADVANCING_SURFER, self.set_advancing_surfer)
        self.bus.unsubscribe(KEY_ENGINE_TM_GENERATE_HEATS, self.generate_heats)
        return


    def get_heat_order(self, tournament_id):
        res = self.tournament_manager.get_heat_order(tournament_id)
        return res


    def set_heat_order(self, tournament_id, list_of_heat_ids):
        res = self.tournament_manager.set_heat_order(tournament_id, list_of_heat_ids)
        return res


    def get_advancing_surfers(self, heat_id):
        res = self.tournament_manager.get_advancing_surfers(heat_id)
        return res


    def set_advancing_surfer(self, heat_id, surfer_id, seed, advancing_from_heat_id, place):
        res = self.tournament_manager.set_advancing_surfers(heat_id, surfer_id, seed, advancing_from_heat_id, place)
        return res

    def generate_heats(self, nparticipants, tournament_id, category_id, tournament_generator):
        res = self.tournament_manager.generate_heats(nparticipants, tournament_id=tournament_id, category_id=category_id, tournament_generator=tournament_generator)
        return res
