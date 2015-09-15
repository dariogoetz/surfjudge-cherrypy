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
    if dt_str is None or len(dt_str) == 0:
        return (None, None)
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
        context = self._standard_env()
        return context


    # TODO: as POST action
    @cherrypy.expose
    #@cherrypy.tools.render(template='tournament_admin/edit_modal.html')
    def do_edit_tournament(self, json_data=None, id=None, name=None, start_date=None, end_date=None, additional_info=None):

        # data is a json with the fields?
        if json_data is not None:
            data = json.loads(json_data)
        else:
            data = {}
            data['id'] = int(id) if len(id) > 0 else None
            data['name'] = name.encode()
            data['start_date'] = start_date.encode()
            data['end_date'] = end_date.encode()
            data['additional_info'] = additional_info.encode()

        data['start_datetime'] = dstr_and_tstr2dtstr(data['start_date'], '00:00')
        data['end_datetime'] = dstr_and_tstr2dtstr(data['end_date'], '00:00')


        res = cherrypy.engine.publish(KEY_ENGINE_DB_INSERT_TOURNAMENT, data).pop(0)
        return res

    @cherrypy.expose
    def do_delete_tournament(self, id=None):
        if id is None:
            return
        tournament = {'id': id}
        cherrypy.engine.publish(KEY_ENGINE_DB_DELETE_TOURNAMENT, tournament).pop(0)
        return


    @cherrypy.expose
    def do_get_tournaments(self, **kwargs):
        query_info = {}

        res = cherrypy.engine.publish(KEY_ENGINE_DB_RETRIEVE_TOURNAMENTS, query_info).pop()
        for tournament in res:
            tournament['start_date'], _ = dtstr2dstr_and_tstr(tournament.get('start_datetime'))
            tournament['end_date'], _ = dtstr2dstr_and_tstr(tournament.get('end_datetime'))

        return json.dumps(res)


    @cherrypy.expose
    @cherrypy.tools.render(template='tournament_admin/edit_categories.html')
    def categories(self):
        context = self._standard_env()
        return context

    @cherrypy.expose
    def do_get_categories(self, tournament_id = None, **kwargs):
        print 'get categories', tournament_id
        if tournament_id is None:
            res = []
        else:
            query_info = {'tournament_id': int(tournament_id)}
            res = cherrypy.engine.publish(KEY_ENGINE_DB_RETRIEVE_CATEGORIES, query_info).pop()
        return json.dumps(res)


    # TODO: as POST action
    @cherrypy.expose
    #@cherrypy.tools.render(template='tournament_admin/edit_modal.html')
    def do_edit_category(self, json_data=None, id=None, name=None, tournament_id=None, additional_info=None):

        # data is a json with the fields?
        if json_data is not None:
            data = json.loads(json_data)
        else:
            data = {}
            data['id'] = int(id) if len(id) > 0 else None
            data['tournament_id'] = tournament_id;
            data['name'] = name.encode()
            data['additional_info'] = additional_info.encode()

        res = cherrypy.engine.publish(KEY_ENGINE_DB_INSERT_CATEGORY, data).pop(0)
        return res



    @cherrypy.expose
    @cherrypy.tools.render(template='tournament_admin/edit_heats.html')
    def heats(self):
        context = self._standard_env()
        import utils
        context['lycra_colors'] = utils.read_lycra_colors('lycra_colors.csv').keys()
        return context


    @cherrypy.expose
    def do_delete_heat(self, id=None):
        if id is None:
            return
        cherrypy.engine.publish(KEY_ENGINE_DB_DELETE_HEAT, {'id': id}).pop(0)
        return


    @cherrypy.expose
    def do_get_heats(self, format=None, category_id=None, **kwargs):
        query_info = {}
        if category_id is not None:
            query_info['category_id'] = int(category_id)
        res = cherrypy.engine.publish(KEY_ENGINE_DB_RETRIEVE_HEATS, query_info).pop()
        for heat in res:
            heat['date'], heat['start_time'] = dtstr2dstr_and_tstr(heat['start_datetime'])
        return json.dumps(res)



    # TODO: as POST action
    @cherrypy.expose
    #@cherrypy.tools.render(template='tournament_admin/edit_modal.html')
    def do_edit_heat(self, json_data=None, heat_id=None, heat_name=None, tournament_id=None, category_id=None, date=None, start_time=None, number_of_waves=None, additional_info=None):
        # data is a json with the fields?
        if json_data is not None:
            data = json.loads(json_data)
        else:
            data = {}
            data['id'] = int(heat_id) if len(heat_id)>0 else None
            data['tournament_id'] = tournament_id
            data['category_id'] = category_id
            data['name'] = heat_name.encode()
            data['start_time'] = start_time.encode()
            data['date'] = date.encode()
            data['number_of_waves'] = number_of_waves.encode()
            data['additional_info'] = additional_info.encode()

        data['start_datetime'] = dstr_and_tstr2dtstr(data['date'], data['start_time'])

        res = cherrypy.engine.publish(KEY_ENGINE_DB_INSERT_HEAT, data).pop(0)
        return res


    @cherrypy.expose
    @cherrypy.tools.render(template='tournament_admin/edit_surfers.html')
    def surfers(self):
        context = self._standard_env()
        return context


    @cherrypy.expose
    def do_get_surfers(self, **kwargs):
        query_info = {}
        res = cherrypy.engine.publish(KEY_ENGINE_DB_RETRIEVE_SURFERS, query_info).pop()
        return json.dumps(res)


    @cherrypy.expose
    def do_set_participating_surfers(self, json_data=None, heat_id=None, surfer_ids=None, surfer_colors=None):
        surfer_ids = json.loads(surfer_ids)
        if surfer_colors is not None:
            surfer_colors = json.loads(surfer_colors)

        if surfer_colors is None:
            surfer_colors = [''] * len(surfer_ids)#'red', 'blue', 'green', 'yellow', 'white', 'orange'][:len(surfer_ids)]
        surfers = zip(surfer_ids, surfer_colors)
        data = {'heat_id': heat_id, 'surfers': surfers}
        res = cherrypy.engine.publish(KEY_ENGINE_DB_SET_PARTICIPANTS, data)
        return


    # TODO: as POST action
    @cherrypy.expose
    def do_edit_surfer(self, json_data=None, id=None, first_name=None, last_name=None, country=None, additional_info=None):

        # data is a json with the fields?
        if json_data is not None:
            data = json.loads(json_data)
        else:
            data = {}
            data['id'] = int(id) if len(id) > 0 else None
            data['first_name'] = first_name.encode()
            data['last_name'] = last_name.encode()
            data['name'] = '{} {}'.format(first_name, last_name)
            data['country'] = country.encode()
            data['additional_info'] = additional_info.encode()

        res = cherrypy.engine.publish(KEY_ENGINE_DB_INSERT_SURFER, data).pop(0)
        return res



    @cherrypy.expose
    def do_delete_surfer(self, id=None):
        if id is None:
            return
        cherrypy.engine.publish(KEY_ENGINE_DB_DELETE_SURFER, {'id': id}).pop(0)
        return


    @cherrypy.expose
    def do_surfers_load_csv(self):
        import utils
        surfers = utils.read_surfers('tmp_surfers.csv')
        for sid, surfer in surfers.items():
            print surfer, type(surfer)
            print 'Inserting surfer {}'.format(surfer['name']),
            res = cherrypy.engine.publish(KEY_ENGINE_DB_INSERT_SURFER, surfer).pop(0)
            print 'done. {}'.format(res)
        return



    @cherrypy.expose
    @cherrypy.tools.render(template='tournament_admin/edit_judges.html')
    def judges(self):
        context = self._standard_env()
        return context


    @cherrypy.expose
    def do_get_active_judges(self, heat_id=None):
        judges = cherrypy.engine.publish(KEY_ENGINE_DB_RETRIEVE_JUDGES_FOR_HEAT, heat_id).pop()
        print '***JUDGES FOR HEAT'
        print judges
        return json.dumps(judges)

    @cherrypy.expose
    def do_get_judges(self):
        judges = [{'first_name': 'Dario', 'last_name': 'Goetz', 'id': 0}]
        return json.dumps(judges)
