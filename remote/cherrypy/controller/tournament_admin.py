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
    @require(has_all_roles(KEY_ROLE_ADMIN))
    def tournaments(self):
        context = self._standard_env()
        return context


    # TODO: as POST action
    @cherrypy.expose
    @require(has_all_roles(KEY_ROLE_ADMIN))
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
        return str(res)

    @cherrypy.expose
    @require(has_all_roles(KEY_ROLE_ADMIN))
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
    @require(has_all_roles(KEY_ROLE_ADMIN))
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
    @require(has_all_roles(KEY_ROLE_ADMIN))
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
        return str(res)

    @cherrypy.expose
    @require(has_all_roles(KEY_ROLE_ADMIN))
    def do_delete_category(self, id=None):
        if id is None:
            return
        category = {'id': id}
        cherrypy.engine.publish(KEY_ENGINE_DB_DELETE_CATEGORY, category).pop(0)
        return


    @cherrypy.expose
    @require(has_all_roles(KEY_ROLE_ADMIN))
    @cherrypy.tools.render(template='tournament_admin/edit_heats.html')
    def heats(self):
        context = self._standard_env()
        import utils
        context['lycra_colors'] = [c['COLOR'] for c in sorted(utils.read_lycra_colors('lycra_colors.csv').values(), key=lambda c: c['SEEDING'])]
        return context


    @cherrypy.expose
    @require(has_all_roles(KEY_ROLE_ADMIN))
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
    @require(has_all_roles(KEY_ROLE_ADMIN))
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
        return str(res)


    @cherrypy.expose
    @require(has_all_roles(KEY_ROLE_ADMIN))
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
    @require(has_all_roles(KEY_ROLE_ADMIN))
    def do_set_participating_surfers(self, heat_id=None, participants=None):
        participants = json.loads(participants)
        # fill missing fields
        old_participants = {p['surfer_id']: p for p in self.collect_participants(heat_id=heat_id)}
        all_participants = []
        for p in participants:
            # take old info
            participant = old_participants.get(p['surfer_id'], {})
            # and overwrite with new one, as far as available
            participant.update(p)
            all_participants.append(participant)
        all_participants = self._complete_participants(all_participants)

        res = cherrypy.engine.publish(KEY_ENGINE_DB_SET_PARTICIPANTS, {'heat_id': heat_id, 'participants': all_participants})
        return

    @cherrypy.expose
    @require(has_all_roles(KEY_ROLE_ADMIN))
    def do_set_participating_surfers_depr(self, heat_id=None, surfer_ids=None, surfer_colors=None):
        surfer_ids = json.loads(surfer_ids)
        if surfer_colors is not None:
            surfer_colors = json.loads(surfer_colors)

        if surfer_colors is None:
            surfer_colors = [''] * len(surfer_ids)#'red', 'blue', 'green', 'yellow', 'white', 'orange'][:len(surfer_ids)]

        # TODO: get correct seed values
        seeds = range(len(surfer_ids))
        surfers = zip(surfer_ids, surfer_colors, seeds)
        data = {'heat_id': heat_id, 'surfers': surfers}
        res = cherrypy.engine.publish(KEY_ENGINE_DB_SET_PARTICIPANTS, data)
        return


    # TODO: as POST action
    @cherrypy.expose
    @require(has_all_roles(KEY_ROLE_ADMIN))
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
    @require(has_all_roles(KEY_ROLE_ADMIN))
    def do_delete_surfer(self, id=None):
        if id is None:
            return
        cherrypy.engine.publish(KEY_ENGINE_DB_DELETE_SURFER, {'id': id}).pop(0)
        return


    @cherrypy.expose
    @require(has_all_roles(KEY_ROLE_ADMIN))
    def do_surfers_load_csv(self, my_file=None):
        import utils
        if my_file is None:
            print 'No file given to upload surfers'
            return
        else:
            print 'Loading file...'
        surfers = utils.read_surfers(my_file.file)
        for sid, surfer in surfers.items():
            print 'Trying to add surfer {}'.format(surfer)
            res = cherrypy.engine.publish(KEY_ENGINE_DB_INSERT_SURFER, surfer).pop(0)
        return



    @cherrypy.expose
    @require(has_all_roles(KEY_ROLE_ADMIN))
    @cherrypy.tools.render(template='tournament_admin/edit_judges.html')
    def judges(self):
        context = self._standard_env()
        return context

    @cherrypy.expose
    @require(has_all_roles(KEY_ROLE_ADMIN))
    @cherrypy.tools.render(template='tournament_admin/judge_activities.html')
    def judge_activities(self):
        context = self._standard_env()
        return context

    @cherrypy.expose
    def do_get_active_judges(self, heat_id=None, **kwargs):
        if heat_id is None:
            print 'do_get_active_judges: No heat_id specified'
            return '[]'
        heat_id=int(heat_id)
        judges = cherrypy.engine.publish(KEY_ENGINE_DB_RETRIEVE_JUDGES_FOR_HEAT, heat_id).pop()
        return json.dumps(judges)

    @cherrypy.expose
    @require(has_all_roles(KEY_ROLE_ADMIN))
    def do_set_active_judges(self, heat_id=None, judge_ids=None):
        if heat_id is None:
            return
        if judge_ids is None:
            judge_ids = []
        else:
            judge_ids = json.loads(judge_ids)
        data = {'heat_id': int(heat_id), 'judges': judge_ids}
        cherrypy.engine.publish(KEY_ENGINE_DB_SET_JUDGE_ACTIVITIES, data).pop()
        return



    @cherrypy.expose
    def do_get_judges(self, **kwargs):
        judges = cherrypy.engine.publish(KEY_ENGINE_DB_RETRIEVE_JUDGES, {}).pop()
        judges = sorted(judges, key=lambda x: x['id'])
        return json.dumps(judges)

    @cherrypy.expose
    @require(has_all_roles(KEY_ROLE_ADMIN))
    def do_edit_judge(self, json_data=None, id=None, first_name=None, last_name=None, username=None, additional_info=None):
        #TODO: check user roles for ac_judge and add if required
        if username is None:
            return

        cherrypy.engine.publish(KEY_ENGINE_USER_ADD_ROLE, username, KEY_ROLE_JUDGE)
        print 'editing judge'
        # data is a json with the fields?
        if json_data is not None:
            data = json.loads(json_data)
        else:
            data = {}
            data['id'] = int(id) if len(id) > 0 else None
            data['first_name'] = first_name.encode()
            data['last_name'] = last_name.encode()
            data['name'] = '{} {}'.format(first_name, last_name)
            data['username'] = username.encode()
            data['additional_info'] = additional_info.encode()
        res = cherrypy.engine.publish(KEY_ENGINE_DB_INSERT_JUDGE, data)
        return json.dumps(res)

    @cherrypy.expose
    @require(has_all_roles(KEY_ROLE_ADMIN))
    def do_delete_judge(self, id=None, username=None):
        # TODO: check user roles for ac_judge and delete if required
        if username is None:
            return

        cherrypy.engine.publish(KEY_ENGINE_USER_REMOVE_ROLE, username, KEY_ROLE_JUDGE)
        if id is None:
            return
        cherrypy.engine.publish(KEY_ENGINE_DB_DELETE_JUDGE, {'id': id}).pop(0)
        return


    @cherrypy.expose
    @require(has_all_roles(KEY_ROLE_ADMIN))
    @cherrypy.tools.render(template='/tournament_admin/edit_scores_hub.html')
    def edit_scores(self):
        data = self._standard_env()
        return data



    @cherrypy.expose
    @require(has_one_role(KEY_ROLE_JUDGE, KEY_ROLE_ADMIN))
    def do_delete_score(self, score = None, heat_id = None, judge_id = None):
        if score is None:
            print 'do_delete_score: No score data given'
            return

        score = json.loads(score)
        db_data = score

        if judge_id is None:
            judge_id = cherrypy.session.get(KEY_JUDGE_ID)
            if judge_id is None:
                print 'do_modify_score: Not registered as judge and no judge id specified'
                return

        if heat_id is None:
            print 'do_delete_score: No heat_id specified'
            return

        heat_id = int(heat_id)

        db_data['judge_id'] = judge_id

        db_data['heat_id'] = heat_id
        heat_info = self.collect_heat_info(heat_id)
        participants = heat_info.get('participants', [])
        color2id = self._get_color2id(participants)
        db_data['surfer_id'] = int(color2id[score['color']])
        del db_data['color']

        res = cherrypy.engine.publish(KEY_ENGINE_DB_DELETE_SCORE, db_data).pop()
        return res


    @cherrypy.expose
    @require(has_all_roles(KEY_ROLE_ADMIN))
    #@require(is_admin()) # later ask for judge or similar
    @cherrypy.tools.render(template='/tournament_admin/edit_scores_panel.html')
    def do_get_editor_panel(self, heat_id = None): #--------editiert-------------
        if heat_id is None:
            return ''

        heat_id = int(heat_id)
        data = self._standard_env()
        #heat_info = cherrypy.engine.publish(KEY_ENGINE_SM_GET_ACTIVE_HEAT_INFO, heat_id).pop().get(heat_id)
        heat_info = self.collect_heat_info(heat_id)
        participants = heat_info.get('participants', [])
        ids = [p.get('surfer_id') for p in participants]
        colors = [p.get('surfer_color') for p in participants]
        colors_hex = [p.get('surfer_color_hex') for p in participants]
        data['heat_id'] = heat_id
        data['judge_ids'] = sorted(heat_info.get('judges', {}).keys())
        data['judge_names'] = ['{} {}'.format(heat_info['judges'][judge_id]['judge_first_name'], heat_info['judges'][judge_id]['judge_last_name']) for judge_id in data['judge_ids']]
        data['surfers'] = dict(zip(ids, colors))
        data['surfer_color_names'] = colors
        data['surfer_color_colors'] = dict(zip(colors, colors_hex))
        data['number_of_waves'] = int(heat_info['number_of_waves'])
        return data



    @cherrypy.expose
    @require(has_all_roles(KEY_ROLE_ADMIN))
    @cherrypy.tools.render(template='/tournament_admin/edit_logins.html')
    def logins(self, **kwargs):
        data = self._standard_env()
        return data


    @cherrypy.expose
    @require(has_all_roles(KEY_ROLE_ADMIN))
    def do_get_logins(self, **kwargs):
        logins = cherrypy.engine.publish(KEY_ENGINE_USER_GET_USERS).pop()
        res = []
        for login, data in logins.items():
            d = {}
            d.update(data)
            d['login'] = login
            del d['password']
            res.append(d)
        return json.dumps(res)


    @cherrypy.expose
    def do_get_heat_order(self, tournament_id=None, **kwargs):
        if tournament_id is None:
            return
        tournament_id = int(tournament_id)
        res = cherrypy.engine.publish(KEY_ENGINE_TM_GET_HEAT_ORDER, tournament_id).pop(0)
        return json.dumps(res)

    @cherrypy.expose
    def do_set_heat_order(self, tournament_id=None, list_of_heat_ids=None, **kwargs):
        if tournament_id is None or list_of_heat_ids is None:
            return

        tournament_id = int(tournament_id)
        list_of_heat_ids = json.loads(list_of_heat_ids)
        res = cherrypy.engine.publish(KEY_ENGINE_TM_SET_HEAT_ORDER, tournament_id, list_of_heat_ids).pop(0)
        return json.dumps(res)


    @cherrypy.expose
    def do_get_advancing_surfers(self, heat_id=None, **kwargs):
        if heat_id is None:
            return
        heat_id = int(heat_id)
        res = cherrypy.engine.publish(KEY_ENGINE_TM_GET_ADVANCING_SURFERS, heat_id).pop(0)
        return json.dumps(res)
