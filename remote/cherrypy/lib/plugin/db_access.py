import cherrypy

from cherrypy.process import plugins
from keys import *

class DBAccessPlugin(plugins.SimplePlugin):
    '''
    A WSBPlugin that is responsible for communicating with the
    database for surfjudge data. Communicates with a database of SurfJudge object.
    '''

    def __init__(self, bus, database):
        plugins.SimplePlugin.__init__(self, bus)

        self.database = database


    def start(self):
        self.bus.log('Setting up database access resources')
        self.bus.subscribe(KEY_ENGINE_DB_RETRIEVE_SCORES, self.get_scores)
        self.bus.subscribe(KEY_ENGINE_DB_INSERT_SCORE, self.insert_score)

        self.bus.subscribe(KEY_ENGINE_DB_RETRIEVE_TOURNAMENTS, self.get_tournaments)
        self.bus.subscribe(KEY_ENGINE_DB_INSERT_TOURNAMENT, self.insert_tournament)
        self.bus.subscribe(KEY_ENGINE_DB_DELETE_TOURNAMENT, self.delete_tournament)

        self.bus.subscribe(KEY_ENGINE_DB_RETRIEVE_HEATS, self.get_heats)
        self.bus.subscribe(KEY_ENGINE_DB_INSERT_HEAT, self.insert_heat)
        self.bus.subscribe(KEY_ENGINE_DB_DELETE_HEAT, self.delete_heat)

        self.bus.subscribe(KEY_ENGINE_DB_RETRIEVE_JUDGE_ID, self.get_judge_id)

        return

    def stop(self):
        self.bus.log('Freeing database access resources')
        self.bus.unsubscribe(KEY_ENGINE_DB_RETRIEVE_SCORES, self.get_scores)
        self.bus.unsubscribe(KEY_ENGINE_DB_INSERT_SCORE, self.insert_score)

        self.bus.unsubscribe(KEY_ENGINE_DB_RETRIEVE_TOURNAMENTS, self.get_tournaments)
        self.bus.unsubscribe(KEY_ENGINE_DB_INSERT_TOURNAMENT, self.insert_tournament)
        self.bus.unsubscribe(KEY_ENGINE_DB_DELETE_TOURNAMENT, self.delete_tournament)

        self.bus.unsubscribe(KEY_ENGINE_DB_RETRIEVE_HEATS, self.get_heats)
        self.bus.unsubscribe(KEY_ENGINE_DB_INSERT_HEAT, self.insert_heat)
        self.bus.unsubscribe(KEY_ENGINE_DB_DELETE_HEAT, self.delete_heat)

        self.bus.unsubscribe(KEY_ENGINE_DB_RETRIEVE_JUDGE_ID, self.get_judge_id)

        return


    def get_scores(self, query_info):
        scores = self.database.get_scores(query_info)
        return scores

    def insert_score(self, score):
        res = self.database.insert_score(score)
        return res


    def get_tournaments(self, query_info):
        tournaments = self.database.get_tournaments(query_info)
        return tournaments

    def insert_tournament(self, tournament):
        res = self.database.insert_tournament(tournament)
        return res

    def delete_tournament(self, tournament):
        res = self.database.delete_tournament(tournament)


    def get_heats(self, query_info):
        heats = self.database.get_heats(query_info)
        return heats

    def insert_heat(self, heat):
        res = self.database.insert_heat(heat)
        return res

    def delete_heat(self, heat):
        res = self.database.delete_heat(heat)


    def get_judge_id(self, username):
        res = self.database.get_judge_id(username)
        return res
