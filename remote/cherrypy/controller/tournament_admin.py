import cherrypy
import json
import datetime
from ..lib.access_conditions import *
from . import CherrypyWebInterface

from keys import *


T_FORMAT = '%H:%M'
D_FORMAT = '%d.%m.%Y'
DT_FORMAT = '%Y-%m-%dT%H:%M'


def dtstr2dstr_and_tstr(dt_str):
    dt = datetime.datetime.strptime(dt_str, DT_FORMAT)
    return (dt.strftime(D_FORMAT), dt.strftime(T_FORMAT))

def dstr_and_tstr2dtstr(d_str, t_str):
    d = datetime.datetime.strptime(d_str, D_FORMAT)
    t = datetime.datetime.strptime(t_str, T_FORMAT)
    dt = datetime.datetime.combine(d, t.time())
    return dt.strftime(DT_FORMAT)

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
    def do_edit_tournament(self, json_data=None, tournament_id=None, tournament_name=None, start_date=None, end_date=None, additional_info=None):

        # data is a json with the fields?
        if json_data is not None:
            data = json.loads(json_data)
        else:
            data = {}
            data['id'] = int(tournament_id) if len(tournament_id)>0 else None
            data['name'] = tournament_name.encode()
            data['start_date'] = start_date.encode()
            data['end_date'] = end_date.encode()
            data['additional_info'] = additional_info.encode()

        data['start_datetime'] = dstr_and_tstr2dtstr(data['start_date'], '00:00')
        data['end_datetime'] = dstr_and_tstr2dtstr(data['end_date'], '00:00')


        res = cherrypy.engine.publish(KEY_ENGINE_DB_INSERT_TOURNAMENT, data).pop(0)
        return res

    @cherrypy.expose
    def do_delete_tournament(self, tournament_id=None):
        if tournament_id is None:
            return
        tournament = {'id': tournament_id}
        cherrypy.engine.publish(KEY_ENGINE_DB_DELETE_TOURNAMENT, tournament).pop(0)
        return


    @cherrypy.expose
    def get_tournaments(self, **kwargs):
        query_info = {}
        res = cherrypy.engine.publish(KEY_ENGINE_DB_RETRIEVE_TOURNAMENTS, query_info).pop()
        for tournament in res:
            tournament['start_date'], _ = dtstr2dstr_and_tstr(tournament['start_datetime'])
            tournament['end_date'], _ = dtstr2dstr_and_tstr(tournament['end_datetime'])

        return json.dumps(res)


    @cherrypy.expose
    @cherrypy.tools.render(template='tournament_admin/edit_heats.html')
    def heats(self):
        query_info = {}
        #res = cherrypy.engine.publish(KEY_ENGINE_DB_RETRIEVE_HEATS, query_info).pop()
        context = self._standard_env()
        #context['RESULTS'] = json.dumps(res)
        return context


    @cherrypy.expose
    def do_delete_heat(self, heat_id=None):
        if heat_id is None:
            return
        heat = {'id': heat_id}
        cherrypy.engine.publish(KEY_ENGINE_DB_DELETE_HEAT, heat).pop(0)
        return


    @cherrypy.expose
    def get_heats(self, format = None, **kwargs):
        query_info = {}
        res = cherrypy.engine.publish(KEY_ENGINE_DB_RETRIEVE_HEATS, query_info).pop()
        for heat in res:
            heat['date'], heat['start_time'] = dtstr2dstr_and_tstr(heat['start_datetime'])
        return json.dumps(res)



    # TODO: as POST action
    @cherrypy.expose
    #@cherrypy.tools.render(template='tournament_admin/edit_modal.html')
    def do_edit_heat(self, json_data=None, heat_id=None, heat_name=None, date=None, start_time=None, additional_info=None):
        # data is a json with the fields?
        if json_data is not None:
            data = json.loads(json_data)
        else:
            data = {}
            data['id'] = int(heat_id) if len(heat_id)>0 else None
            data['name'] = heat_name.encode()
            data['start_time'] = start_time.encode()
            data['date'] = date.encode()
            data['additional_info'] = additional_info.encode()

        data['start_datetime'] = dstr_and_tstr2dtstr(data['date'], data['start_time'])

        res = cherrypy.engine.publish(KEY_ENGINE_DB_INSERT_HEAT, data).pop(0)
        return res
