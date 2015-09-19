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

        self.bus.subscribe(KEY_ENGINE_DB_RETRIEVE_CATEGORIES, self.get_categories)
        self.bus.subscribe(KEY_ENGINE_DB_INSERT_CATEGORY, self.insert_category)
        self.bus.subscribe(KEY_ENGINE_DB_DELETE_CATEGORY, self.delete_category)

        self.bus.subscribe(KEY_ENGINE_DB_RETRIEVE_HEATS, self.get_heats)
        self.bus.subscribe(KEY_ENGINE_DB_INSERT_HEAT, self.insert_heat)
        self.bus.subscribe(KEY_ENGINE_DB_DELETE_HEAT, self.delete_heat)

        self.bus.subscribe(KEY_ENGINE_DB_RETRIEVE_JUDGE_ID_FOR_USERNAME, self.get_judge_id_for_username)

        self.bus.subscribe(KEY_ENGINE_DB_RETRIEVE_SURFERS, self.get_surfers)
        self.bus.subscribe(KEY_ENGINE_DB_INSERT_SURFER, self.insert_surfer)
        self.bus.subscribe(KEY_ENGINE_DB_DELETE_SURFER, self.delete_surfer)

        self.bus.subscribe(KEY_ENGINE_DB_RETRIEVE_PARTICIPANTS, self.get_participants)
        self.bus.subscribe(KEY_ENGINE_DB_SET_PARTICIPANTS, self.set_participants)

        self.bus.subscribe(KEY_ENGINE_DB_RETRIEVE_JUDGES, self.get_judges)
        self.bus.subscribe(KEY_ENGINE_DB_INSERT_JUDGE, self.insert_judge)
        self.bus.subscribe(KEY_ENGINE_DB_DELETE_JUDGE, self.delete_judge)

        self.bus.subscribe(KEY_ENGINE_DB_RETRIEVE_JUDGE_ACTIVITIES, self.get_judge_activities)
        self.bus.subscribe(KEY_ENGINE_DB_SET_JUDGE_ACTIVITIES, self.set_judge_activities)

        self.bus.subscribe(KEY_ENGINE_DB_RETRIEVE_JUDGES_FOR_HEAT, self.get_judges_for_heat)
        self.bus.subscribe(KEY_ENGINE_DB_RETRIEVE_HEAT_INFO, self.get_heat_info)
        return

    def stop(self):
        self.bus.log('Freeing database access resources')
        self.bus.unsubscribe(KEY_ENGINE_DB_RETRIEVE_SCORES, self.get_scores)
        self.bus.unsubscribe(KEY_ENGINE_DB_INSERT_SCORE, self.insert_score)

        self.bus.unsubscribe(KEY_ENGINE_DB_RETRIEVE_TOURNAMENTS, self.get_tournaments)
        self.bus.unsubscribe(KEY_ENGINE_DB_INSERT_TOURNAMENT, self.insert_tournament)
        self.bus.unsubscribe(KEY_ENGINE_DB_DELETE_TOURNAMENT, self.delete_tournament)

        self.bus.unsubscribe(KEY_ENGINE_DB_RETRIEVE_CATEGORIES, self.get_categories)
        self.bus.unsubscribe(KEY_ENGINE_DB_INSERT_CATEGORY, self.insert_category)
        self.bus.unsubscribe(KEY_ENGINE_DB_DELETE_CATEGORY, self.delete_category)

        self.bus.unsubscribe(KEY_ENGINE_DB_RETRIEVE_HEATS, self.get_heats)
        self.bus.unsubscribe(KEY_ENGINE_DB_INSERT_HEAT, self.insert_heat)
        self.bus.unsubscribe(KEY_ENGINE_DB_DELETE_HEAT, self.delete_heat)

        self.bus.unsubscribe(KEY_ENGINE_DB_RETRIEVE_JUDGE_ID_FOR_USERNAME, self.get_judge_id_for_username)

        self.bus.unsubscribe(KEY_ENGINE_DB_RETRIEVE_SURFERS, self.get_surfers)
        self.bus.unsubscribe(KEY_ENGINE_DB_INSERT_SURFER, self.insert_surfer)
        self.bus.unsubscribe(KEY_ENGINE_DB_DELETE_SURFER, self.delete_surfer)

        self.bus.unsubscribe(KEY_ENGINE_DB_RETRIEVE_PARTICIPANTS, self.get_participants)
        self.bus.unsubscribe(KEY_ENGINE_DB_SET_PARTICIPANTS, self.set_participants)

        self.bus.unsubscribe(KEY_ENGINE_DB_RETRIEVE_JUDGES, self.get_judges)
        self.bus.unsubscribe(KEY_ENGINE_DB_INSERT_JUDGE, self.insert_judge)
        self.bus.unsubscribe(KEY_ENGINE_DB_DELETE_JUDGE, self.delete_judge)

        self.bus.unsubscribe(KEY_ENGINE_DB_RETRIEVE_JUDGE_ACTIVITIES, self.get_judge_activities)
        self.bus.unsubscribe(KEY_ENGINE_DB_SET_JUDGE_ACTIVITIES, self.set_judge_activities)

        self.bus.unsubscribe(KEY_ENGINE_DB_RETRIEVE_JUDGES_FOR_HEAT, self.get_judges_for_heat)
        self.bus.unsubscribe(KEY_ENGINE_DB_RETRIEVE_HEAT_INFO, self.get_heat_info)
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
        return res

    def get_categories(self, query_info):
        categories = self.database.get_categories(query_info)
        return categories

    def insert_category(self, category):
        res = self.database.insert_category(category)
        return res

    def delete_category(self, category):
        res = self.database.delete_category(category)
        return res


    def get_heats(self, query_info):
        heats = self.database.get_heats(query_info)
        return heats

    def insert_heat(self, heat):
        res = self.database.insert_heat(heat)
        return res

    def delete_heat(self, heat):
        res = self.database.delete_heat(heat)
        return res

    def get_judge_id_for_username(self, username):
        res = self.database.get_judge_id_for_username(username)
        return res


    def get_surfers(self, query_info):
        res = self.database.get_surfers(query_info)
        return res

    def insert_surfer(self, surfer):
        res = self.database.insert_surfer(surfer)
        return res

    def delete_surfer(self, surfer):
        res = self.database.delete_surfer(surfer)
        return res


    def get_participants(self, heat_id):
        res = self.database.get_participants(heat_id)
        return res

    def set_participants(self, data):
        res = self.database.set_participants(data)
        return res


    def get_judges(self, query_info):
        res = self.database.get_judges(query_info)
        return res

    def insert_judge(self, judge):
        res = self.database.insert_judge(judge)
        return res

    def delete_judge(self, judge):
        res = self.database.delete_judge(judge)
        return res


    def get_judge_activities(self, query_info):
        res = self.database.get_judge_activities(query_info)
        return res

    def set_judge_activities(self, data):
        res = self.database.set_judge_activities(data)
        return res


    def get_judges_for_heat(self, heat_id):
        res = self.database.get_judges_for_heat(heat_id)
        return res

    def get_heat_info(self, query_info):
        res = self.database.get_heat_info(query_info)
        return res
