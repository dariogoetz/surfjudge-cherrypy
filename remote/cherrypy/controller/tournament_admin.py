import cherrypy
import json
import datetime
from ..lib.access_conditions import *
from . import CherrypyWebInterface

from keys import *


def dtstr2dstr_and_tstr(dt_str):
    if dt_str is None or len(dt_str) == 0:
        return (None, None)
    dt = datetime.datetime.strptime(dt_str, CherrypyWebInterface.DT_FORMAT)
    return (dt.strftime(CherrypyWebInterface.D_FORMAT), dt.strftime(CherrypyWebInterface.T_FORMAT))

def dstr_and_tstr2dtstr(d_str, t_str):
    d = datetime.datetime.strptime(d_str, CherrypyWebInterface.D_FORMAT)
    t = datetime.datetime.strptime(t_str, CherrypyWebInterface.T_FORMAT)
    dt = datetime.datetime.combine(d, t.time())
    return dt.strftime(CherrypyWebInterface.DT_FORMAT)

class TournamentAdminWebInterface(CherrypyWebInterface):

    @cherrypy.expose
    @cherrypy.tools.render(template='tournament_admin/edit_tournaments.html')
    @cherrypy.tools.relocate()
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
            data['name'] = name
            data['start_date'] = start_date
            data['end_date'] = end_date
            data['additional_info'] = additional_info

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
    @cherrypy.tools.relocate()
    def categories(self):
        context = self._standard_env()
        return context

    @cherrypy.expose
    def do_get_categories(self, tournament_id = None, **kwargs):
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
            data['name'] = name#.encode()
            data['additional_info'] = additional_info#.encode()

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
    @cherrypy.tools.relocate()
    def heats(self):
        context = self._standard_env()
        #import utils
        #context['lycra_colors'] = [c['COLOR'] for c in sorted(utils.read_lycra_colors('lycra_colors.csv').values(), key=lambda c: c['SEEDING'])]
        return context


    @cherrypy.expose
    @require(has_all_roles(KEY_ROLE_ADMIN))
    def do_delete_heat(self, id=None):
        if id is None:
            return
        cherrypy.engine.publish(KEY_ENGINE_DB_DELETE_HEAT, {'id': id}).pop(0)
        return


    @cherrypy.expose
    def do_get_heats(self, category_id=None, **kwargs):
        query_info = {}
        if category_id is not None:
            query_info['category_id'] = int(category_id)
        res = cherrypy.engine.publish(KEY_ENGINE_DB_RETRIEVE_HEATS, query_info).pop()
        for heat in res:
            heat['date'], heat['start_time'] = dtstr2dstr_and_tstr(heat['start_datetime'])
        return json.dumps(res)


    @cherrypy.expose
    def do_get_heat_info(self, heat_id=None, **kwargs):
        if heat_id is None:
            return '{}'

        query_info = {}
        query_info['id'] = int(heat_id)
        heat = cherrypy.engine.publish(KEY_ENGINE_DB_RETRIEVE_HEATS, query_info).pop()
        if len(heat)>0:
            heat = heat[0]
        else:
            return '{}'

        heat['date'], heat['start_time'] = dtstr2dstr_and_tstr(heat['start_datetime'])
        return json.dumps(heat)


    # TODO: as POST action
    @cherrypy.expose
    @require(has_all_roles(KEY_ROLE_ADMIN))
    def do_edit_heat(self, json_data=None, heat_id=None, heat_name=None, category_id=None, date=None, start_time=None, number_of_waves=None, duration=None, additional_info=None, **kwargs):
        # data is a json with the fields?
        if json_data is not None:
            data = json.loads(json_data)
        else:
            data = {}
            data['id'] = int(heat_id) if len(heat_id)>0 else None
            data['category_id'] = category_id
            data['name'] = heat_name#.encode()
            data['start_time'] = start_time#.encode()
            data['date'] = date#.encode()
            data['number_of_waves'] = number_of_waves if number_of_waves else CherrypyWebInterface.DEFAULT_NUMBER_OF_WAVES
            data['duration'] = duration if duration else CherrypyWebInterface.DEFAULT_DURATION
            data['additional_info'] = additional_info

        data['start_datetime'] = dstr_and_tstr2dtstr(data['date'], data['start_time'])

        res = cherrypy.engine.publish(KEY_ENGINE_DB_INSERT_HEAT, data).pop(0)
        return str(res)


    @cherrypy.expose
    @require(has_all_roles(KEY_ROLE_ADMIN))
    @cherrypy.tools.render(template='tournament_admin/edit_surfers.html')
    @cherrypy.tools.relocate()
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
            data['first_name'] = first_name
            data['last_name'] = last_name
            data['name'] = u'{} {}'.format(first_name, last_name)
            data['country'] = country
            data['additional_info'] = additional_info

        res = cherrypy.engine.publish(KEY_ENGINE_DB_INSERT_SURFER, data).pop(0)
        return json.dumps(res)



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
        surfers = utils.read_surfers(my_file.file, decode='utf-8')
        for sid, surfer in surfers.items():
            print u'Trying to add surfer {}'.format(surfer)
            res = cherrypy.engine.publish(KEY_ENGINE_DB_INSERT_SURFER, surfer).pop(0)
        return




    @cherrypy.expose
    def do_generate_heats(self, tournament_id=None, category_id=None, csv_document=None):
        if tournament_id is None or category_id is None:
            return
        tournament_id = int(tournament_id)
        category_id = int(category_id)

        import utils
        surfers = utils.read_surfers(csv_document.file, decode='utf-8')
        surfers = sorted(surfers.values(), key=lambda x: int(x['seeding']))

        res = cherrypy.engine.publish(KEY_ENGINE_TM_GENERATE_HEATS, len(surfers), tournament_id, category_id, 'standard').pop()

        if len(res) == 2:
            advancing_surfers, seeding_info = res
        else:
            print 'generate_heats: Did not get advancing surfers AND seeding info'
            return

        def rueck(i, n):
            return (i/n) % 2
        def hin(i, n):
            return ( (i/n) +1 ) %2
        def idx2heat(i, n):
            return i%n * hin(i,n) + (n - i%n - 1) * rueck(i,n)
        def idx2seed(i, n):
            return i/n

        participants = {}
        n_heats = len(seeding_info)
        for idx, surfer in enumerate(surfers):
            heat_id = seeding_info[idx2heat(idx, n_heats)]
            seed = idx2seed(idx, n_heats)
            surfer_id = cherrypy.engine.publish(KEY_ENGINE_DB_INSERT_SURFER, surfer).pop()
            p = {}
            p['surfer_id'] = surfer_id
            p['seed'] = seed
            p['was_seeded_at'] = idx
            participants.setdefault(heat_id, []).append(p)

        for heat_id, ps in participants.items():
            self.do_set_participating_surfers(heat_id=heat_id, participants=json.dumps(ps))




    @cherrypy.expose
    @require(has_all_roles(KEY_ROLE_ADMIN))
    @cherrypy.tools.render(template='tournament_admin/edit_judges.html')
    @cherrypy.tools.relocate()
    def judges(self):
        context = self._standard_env()
        return context

    @cherrypy.expose
    @require(has_all_roles(KEY_ROLE_ADMIN))
    @cherrypy.tools.render(template='tournament_admin/edit_judge_activities.html')
    @cherrypy.tools.relocate()
    def edit_judge_activities(self):
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
    def do_set_active_judges(self, heat_id=None, judge_ids=None, append=False):
        if heat_id is None:
            return
        if judge_ids is None:
            judge_ids = []
        else:
            judge_ids = json.loads(judge_ids)

        data = {'heat_id': int(heat_id), 'judges': judge_ids}
        if append:
            data['append'] = True

        cherrypy.engine.publish(KEY_ENGINE_DB_SET_JUDGE_ACTIVITIES, data).pop()
        return

    @cherrypy.expose
    @require(has_all_roles(KEY_ROLE_ADMIN))
    def do_delete_active_judge(self, heat_id=None, judge_id=None):
        if heat_id is None:
            return
        if judge_id is None:
            return
        data = {'heat_id': int(heat_id), 'judge_id': int(judge_id)}
        cherrypy.engine.publish(KEY_ENGINE_DB_DELETE_JUDGE_ACTIVITY, data).pop()
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
            data['first_name'] = first_name
            data['last_name'] = last_name
            data['name'] = u'{} {}'.format(first_name, last_name)
            data['username'] = username
            data['additional_info'] = additional_info
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
    @cherrypy.tools.relocate()
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
    @cherrypy.tools.relocate()
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
        data['judge_names'] = [u'{} {}'.format(heat_info['judges'][judge_id]['judge_first_name'], heat_info['judges'][judge_id]['judge_last_name']) for judge_id in data['judge_ids']]
        data['surfers'] = dict(zip(ids, colors))
        data['surfer_color_names'] = colors
        data['surfer_color_colors'] = dict(zip(colors, colors_hex))
        data['number_of_waves'] = int(heat_info['number_of_waves'])
        return data


    def _get_heat_ids_for_tournament(self, tournament_id):
        heats = cherrypy.engine.publish(KEY_ENGINE_DB_RETRIEVE_HEAT_INFO, {'tournament_id': tournament_id}).pop()
        if heats is None or len(heats) == 0:
            return []
        hids = sorted([h['heat_id'] for h in heats])
        return hids


    @cherrypy.expose
    def do_get_heat_order(self, tournament_id=None, **kwargs):
        if tournament_id is None:
            return
        tournament_id = int(tournament_id)

        hids = cherrypy.engine.publish(KEY_ENGINE_TM_GET_HEAT_ORDER, tournament_id).pop(0)
        if hids is None or len(hids) == 0:
            hids = self._get_heat_ids_for_tournament(tournament_id)
        if len(hids) == 0:
            return '[]'

        res = cherrypy.engine.publish(KEY_ENGINE_DB_RETRIEVE_HEATS, {'id': hids}).pop(0)
        return json.dumps(res)


    @cherrypy.expose
    def do_set_heat_order(self, tournament_id=None, list_of_heat_ids=None, **kwargs):
        if tournament_id is None or list_of_heat_ids is None:
            return

        tournament_id = int(tournament_id)
        list_of_heat_ids = json.loads(list_of_heat_ids)
        res = cherrypy.engine.publish(KEY_ENGINE_TM_SET_HEAT_ORDER, tournament_id, list_of_heat_ids).pop()
        return json.dumps(res)

    @cherrypy.expose
    def do_get_current_heat_id(self, tournament_id=None, **kwargs):
        if tournament_id is None:
            return

        tournament_id = int(tournament_id)
        res = cherrypy.engine.publish(KEY_ENGINE_TM_GET_CURRENT_HEAT_ID, tournament_id).pop()
        if res is None:
            hids = self._get_heat_ids_for_tournament(tournament_id)
            if len(hids) == 0:
                return None
            res = hids[0]

        return str(res)

    @cherrypy.expose
    def do_set_current_heat_id(self, tournament_id=None, heat_id=None, **kwargs):
        if tournament_id is None or heat_id is None:
            return

        tournament_id = int(tournament_id)
        heat_id = int(heat_id)

        res = cherrypy.engine.publish(KEY_ENGINE_TM_SET_CURRENT_HEAT_ID, tournament_id, heat_id)
        return


    @cherrypy.expose
    def do_get_advancement_rules(self, heat_id=None, **kwargs):
        if heat_id is None:
            return
        heat_id = int(heat_id)
        rules = cherrypy.engine.publish(KEY_ENGINE_TM_GET_ADVANCING_SURFERS, heat_id).pop()

        hids = [r['from_heat_id'] for r in rules.values()]
        heat_infos = cherrypy.engine.publish(KEY_ENGINE_DB_RETRIEVE_HEATS, {'id': hids}).pop(0)
        heat_infos = {h['id']: h for h in heat_infos}
        res = []
        for seed, p in rules.items():
            p['seed'] = seed
            heat_name = heat_infos.get(p['from_heat_id'], {}).get('name', p['from_heat_id'])
            p['name'] = 'To advance from place {} of "{}"'.format(p['from_place'], heat_name)
            res.append(p)
        return json.dumps(res)

    @cherrypy.expose
    def do_get_advancing_surfers(self, heat_id=None, **kwargs):
        if heat_id is None:
            return
        heat_id = int(heat_id)
        #res = cherrypy.engine.publish(KEY_ENGINE_TM_GET_ADVANCING_SURFERS, heat_id).pop()
        res = self.collect_participants(heat_id, fill_proposal=True, confirmed_participants=[])
        return json.dumps(res)

    @cherrypy.expose
    def do_get_lycra_colors(self):
        import utils
        return json.dumps([c['COLOR'] for c in sorted(utils.read_lycra_colors('lycra_colors.csv').values(), key=lambda c: c['SEEDING'])])
