import cherrypy
import json
from ..lib.access_conditions import *
from . import CherrypyWebInterface

import score_processing

from keys import *

class HeadJudgeWebInterface(CherrypyWebInterface):


    @cherrypy.expose
    @cherrypy.tools.render(template = 'headjudge/start_stop_heats.html')
    @cherrypy.tools.relocate()
    @require(has_one_role(KEY_ROLE_HEADJUDGE))
    def start_stop_heats(self):
        context = self._standard_env()
        heat_info = cherrypy.engine.publish(KEY_ENGINE_SM_GET_ACTIVE_HEAT_INFO, None).pop()
        tournaments = set()
        for heat in heat_info.values():
            tournaments.add(heat['tournament_id'])
        for tournament_id in tournaments:
            panel_html = self.render_html(context = self.get_heat_activation_panel(tournament_id), template = 'headjudge/heat_activation_panel.html')
            context.setdefault('panels', []).append(panel_html)
        return context

    @cherrypy.expose
    @require(has_one_role(KEY_ROLE_HEADJUDGE))
    @cherrypy.tools.render(template = 'headjudge/judge_activities_hub.html')
    @cherrypy.tools.relocate()
    def judge_activities(self):

        data = self._standard_env()
        return data



    ##############
    # REST stuff #
    ##############

    @cherrypy.expose
    @require(has_one_role(KEY_ROLE_HEADJUDGE))
    def do_activate_heat(self, heat_id = None, **kwargs):
        if heat_id is None:
            return
        heat_id = int(heat_id)
        heat_info = self.collect_heat_info(heat_id)

        res = cherrypy.engine.publish(KEY_ENGINE_SM_ACTIVATE_HEAT, heat_id, heat_info).pop()
        return res

    @cherrypy.expose
    @require(has_one_role(KEY_ROLE_HEADJUDGE))
    def do_deactivate_heat(self, heat_id = None, **kwargs):
        if heat_id is None:
            return
        heat_id = int(heat_id)

        res = cherrypy.engine.publish(KEY_ENGINE_SM_DEACTIVATE_HEAT, heat_id).pop()
        return res


    @cherrypy.expose
    @cherrypy.tools.render(template='headjudge/heat_activation_panel.html')
    @require(has_one_role(KEY_ROLE_HEADJUDGE))
    def get_heat_activation_panel(self, tournament_id=None):
        context = self._standard_env()

        if tournament_id is None:
            return ''
        heat_info = cherrypy.engine.publish(KEY_ENGINE_DB_RETRIEVE_HEAT_INFO, {'tournament_id': tournament_id}).pop()
        if len(heat_info) == 0:
            return ''

        context['tournament_name'] = heat_info[0]['tournament_name']
        context['tournament_id'] = heat_info[0]['tournament_id']
        categories = {}
        cid2heats = {}
        for heat in heat_info:
            cid = heat['category_id']
            categories[cid] = {'id': cid, 'name': heat['category_name']}
            cid2heats.setdefault(cid, {})[heat['heat_id']] = {'id': heat['heat_id'], 'name': heat['heat_name']}

        context['categories'] = sorted(categories.values(), key=lambda x:x['name'])
        context['heats'] = {}
        for cid, heats in cid2heats.items():
            context['heats'][cid] = sorted(heats.values(), key=lambda x:x['name'])
        return context

    @cherrypy.expose
    @cherrypy.tools.render(template='headjudge/judge_activities_panel.html')
    def do_get_judge_activities_panel(self, heat_id=None):
        if heat_id is None:
            return ''
        heat_id = int(heat_id)

        data = self._standard_env()

        heat_info = cherrypy.engine.publish(KEY_ENGINE_SM_GET_ACTIVE_HEAT_INFO, heat_id).pop()
        participants = heat_info['participants']
        ids = [str(p.get('surfer_id')) for p in participants]
        colors = [str(p.get('surfer_color')) for p in participants]
        colors_hex = [str(p.get('surfer_color_hex')) for p in participants]
        judge_ids = sorted(heat_info['judges'].keys())
        data['heat_id'] = heat_id
        data['surfers'] = dict(zip(ids, colors))
        data['surfer_color_names'] = colors
        data['number_of_waves'] = int(heat_info['number_of_waves'])
        data['judge_ids']= judge_ids
        data['judge_names'] = ['{}'.format(heat_info['judges'][judge_id]['judge_first_name']) for judge_id in data['judge_ids']]
        data['surfer_color_colors'] = dict(zip(colors, colors_hex))
        return data




    @cherrypy.expose
    def do_get_participating_surfers(self, heat_id=None, fill_advance=False):
        if heat_id == '' or heat_id is None:
            return json.dumps([])
        heat_id = int(heat_id)
        data = self.collect_participants(heat_id, fill_advance=fill_advance)
        return json.dumps(data)


    @cherrypy.expose
    @require(has_one_role(KEY_ROLE_ADMIN, KEY_ROLE_HEADJUDGE))
    def do_delete_published_results(self, heat_id=None):
        if heat_id is None:
            return
        heat_id = int(heat_id)
        print 'deleting'
        res = cherrypy.engine.publish(KEY_ENGINE_DB_DELETE_RESULTS, {'heat_id': heat_id})
        return

    @cherrypy.expose
    @require(has_one_role(KEY_ROLE_ADMIN, KEY_ROLE_HEADJUDGE))
    def do_publish_results(self, heat_id=None, n_best_waves=CherrypyWebInterface.N_BEST_WAVES):
        if heat_id is None:
            return
        heat_id = int(heat_id)
        heat_info = self.collect_heat_info(heat_id)
        judges = set(heat_info.get('judges', []))
        scores= self._get_scores(heat_id, judges)
        average_scores = score_processing.compute_average_scores(scores, judges)
        places_total_scores = score_processing.compute_places_total_scores(average_scores, n_best_waves)
        # write to results db
        # sorted_total_scores: surfer_id -> (place (start at 0), total_score)
        # average_scores: surfer_id -> wave_nr -> average_score
        for surfer_id, data in average_scores.items():
            score_list = sorted(average_scores.get(surfer_id, {}).items(), key=lambda x: x[0])
            json_scores = json.dumps([score for (wave, score) in score_list])
            place, total_score = places_total_scores[surfer_id]

            res = cherrypy.engine.publish(KEY_ENGINE_DB_INSERT_RESULT, {'surfer_id': surfer_id, 'heat_id': heat_id, 'wave_scores': json_scores, 'place': place, 'total_score': total_score})
        return


    @cherrypy.expose
    def do_get_judging_requests(self, heat_id=None, **kwargs):
        requests = {}
        if heat_id is not None:
            heat_id = int(heat_id)
            specific_requests = cherrypy.engine.publish(KEY_ENGINE_JM_GET_JUDGING_REQUESTS, heat_id).pop()
            requests.update(specific_requests)

        general_requests = cherrypy.engine.publish(KEY_ENGINE_JM_GET_JUDGING_REQUESTS, None).pop()
        requests.update(general_requests)

        # get registered judges for the current heat
        confirmed_judge_ids = set()
        if heat_id is not None:
            heat_info = self.collect_heat_info(int(heat_id))
            judges = heat_info.get('judges', {})
            confirmed_judge_ids = set(judges)

        # get judge info for judging_requests
        res = []
        for judge_id, expires in requests.items():
            judge_info = cherrypy.engine.publish(KEY_ENGINE_DB_RETRIEVE_JUDGES, {'id': judge_id}).pop()
            if len(judge_info)>0:
                judge_info = judge_info[0]
            else:
                # request by unknown judge
                continue
            if judge_id in confirmed_judge_ids:
                judge_info['status'] = 'confirmed'
            else:
                judge_info['status'] = 'pending'
            judge_info['judge_id'] = judge_info['id']
            if heat_id not in judge_info:
                # fill in heat_id
                judge_info['heat_id'] = heat_id
            judge_info['expires'] = str(expires)
            judge_info['name'] = '{} {}'.format(judge_info['first_name'], judge_info['last_name'])
            res.append(judge_info)
            #res.append({'judge_id': judge_id, 'expires': str(expires)})

        # add missing judges
        for judge_id in confirmed_judge_ids - set(requests):
            judge_info = judges[judge_id]
            judge_info['judge_id'] = judge_id
            judge_info['status'] = 'missing'
            judge_info['name'] = '{} {}'.format(judge_info['judge_first_name'], judge_info['judge_last_name'])
            res.append(judge_info)

        return json.dumps(res)

    @cherrypy.expose
    @cherrypy.tools.render(template='tournament_admin/heat_overview_hub.html')
    @cherrypy.tools.relocate()
    def heat_overview(self):
        context = self._standard_env()
        return context


    @cherrypy.expose
    @cherrypy.tools.render(template='tournament_admin/heat_overview_panel.html')
    @require(has_one_role(KEY_ROLE_HEADJUDGE, KEY_ROLE_ADMIN))
    def do_get_heat_overview_panel(self, heat_id, **kwargs):
        if heat_id is None:
            return
        heat_id = int(heat_id)
        heat_info = self.collect_heat_info(heat_id)

        context = self._standard_env()
        context['heat_id'] = heat_id
        context['heat_name'] = heat_info['heat_name']
        context['category_id'] = heat_info['category_id']
        context['category_name'] = heat_info['category_name']
        return context
