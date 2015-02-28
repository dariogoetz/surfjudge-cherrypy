import cherrypy

from cherrypy.process import plugins

KEY_ENGINE_DB_RETRIEVE_SCORES = 'db_retrieve_scores'
KEY_ENGINE_DB_INSERT_SCORE = 'db_insert_score'

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

        #self.bus.subscribe(KEY_ENGINE_USER_LOGIN,  self.login_user)
        #self.bus.subscribe(KEY_ENGINE_USER_LOGOUT, self.logout_user)
        #self.bus.subscribe(KEY_ENGINE_USER_REGISTER, self.register_user)
        return

    def stop(self):
        self.bus.log('Freeing database access resources')
        self.bus.unsubscribe(KEY_ENGINE_DB_RETRIEVE_SCORES, self.get_scores)
        self.bus.unsubscribe(KEY_ENGINE_DB_INSERT_SCORE, self.insert_score)
        #self.bus.unsubscribe(KEY_ENGINE_USER_LOGIN,  self.login_user)
        #self.bus.unsubscribe(KEY_ENGINE_USER_LOGOUT, self.logout_user)
        #self.bus.unsubscribe(KEY_ENGINE_USER_REGISTER, self.register_user)
        return


    def get_scores(self, query_info):
        scores = self.database.get_scores(query_info)
        return scores

    def insert_score(self, score):
        res = self.database.insert_score(score)
        return res
