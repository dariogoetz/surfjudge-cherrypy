import cherrypy
import json
from ..lib.access_conditions import *
from . import CherrypyWebInterface

from keys import *

class TournamentAdminWebInterface(CherrypyWebInterface):

    @cherrypy.expose
    @cherrypy.tools.render(template='tournament_admin/edit_tournaments.html')
    def tournaments(self):
        query_info = {}
        res = cherrypy.engine.publish(KEY_ENGINE_DB_RETRIEVE_TOURNAMENTS, query_info).pop()

        context = self._standard_env()
        context['RESULTS'] = json.dumps(res)
        return context


    # TODO: as POST action
    @cherrypy.expose
    #@cherrypy.tools.render(template='tournament_admin/edit_modal.html')
    def do_edit_tournament(self, json_data=None, tournament_id=None, tournament_name=None, start_date=None, end_date=None, additional_info = None):
        # data is a json with the fields?
        if json_data is not None:
            data = json.loads(json_data)
        else:
            data = {}
            data['id'] = tournament_id
            data['name'] = name
            data['start_date'] = start_date
            data['end_date'] = end_date
            data['additional_info'] = additional_info

        res = cherrypy.engine.publish(KEY_ENGINE_DB_INSERT_TOURNAMENT, data).pop(0)
        return res


    @cherrypy.expose
    def get_tournaments(self, **kwargs):
        query_info = {}
        res = cherrypy.engine.publish(KEY_ENGINE_DB_RETRIEVE_TOURNAMENTS, query_info).pop()
        return json.dumps(res)


    @cherrypy.expose
    @cherrypy.tools.render(template='base_dashboard.html')
    def submit(self, **kwargs):
        res = self._standard_env()
        return res
