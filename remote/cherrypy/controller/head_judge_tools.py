import cherrypy
import json
from ..lib.access_conditions import *
from . import CherrypyWebInterface

from keys import *

class HeadJudgeWebInterface(CherrypyWebInterface):


    @cherrypy.expose
    @cherrypy.tools.render(template = 'headjudge/start_stop_heats.html')
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
    @cherrypy.tools.render(template = 'headjudge/judge_activities.html')
    def judge_activities(self):
        judge_id = cherrypy.session.get(KEY_JUDGE_ID)
        heats = cherrypy.engine.publish(KEY_ENGINE_SM_GET_HEATS_FOR_JUDGE, judge_id).pop()
        data = self._standard_env()
        if len(heats) > 0:
            heat_id = int(heats.keys()[0])
        else:
            return ''

        heat_info = cherrypy.engine.publish(KEY_ENGINE_SM_GET_ACTIVE_HEAT_INFO, heat_id).pop().get(heat_id)
        surfer_data = heat_info['participants']
        ids = map(str, surfer_data.get('surfer_id', []))
        colors = map(str, surfer_data.get('surfer_color', []))
        colors_hex = map(str, surfer_data.get('surfer_color_hex', []))
        data['judge_name'] = '{} {}'.format(heat_info['judges'][judge_id]['judge_first_name'], heat_info['judges'][judge_id]['judge_last_name'])
        data['surfers'] = dict(zip(ids, colors))
        data['surfer_color_names'] = colors
        data['surfer_color_colors'] = dict(zip(colors, colors_hex))
        data['number_of_waves'] = int(heat_info['number_of_waves'])

        #heat_info = cherrypy.engine.publish(KEY_ENGINE_SM_GET_ACTIVE_HEAT_INFO, None).pop()
        #tournaments = set()
        #for heat in heat_info.values():
        #    tournaments.add(heat['tournament_id'])
        #for tournament_id in tournaments:
        #    panel_html = self.render_html(context = self.get_heat_activation_panel(tournament_id), template = 'headjudge/activity_panel.html')
        #    context.setdefault('panels', []).append(panel_html)
        return data





    ##############
    # REST stuff #
    ##############

    @cherrypy.expose
    def do_activate_heat(self, heat_id = None, **kwargs):
        if heat_id is None:
            return
        heat_id = int(heat_id)
        heat_info = self.collect_heat_info(heat_id)

        res = cherrypy.engine.publish(KEY_ENGINE_SM_ACTIVATE_HEAT, heat_id, heat_info).pop()
        return res

    @cherrypy.expose
    def do_deactivate_heat(self, heat_id = None, **kwargs):
        if heat_id is None:
            return
        heat_id = int(heat_id)

        res = cherrypy.engine.publish(KEY_ENGINE_SM_DEACTIVATE_HEAT, heat_id).pop()
        return res


    @cherrypy.expose
    @cherrypy.tools.render(template='headjudge/heat_activation_panel.html')
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
            print heats.values()
            context['heats'][cid] = sorted(heats.values(), key=lambda x:x['name'])
        return context



    @cherrypy.expose
    def do_get_participating_surfers(self, heat_id=None):
        if heat_id == '' or heat_id is None:
            return json.dumps({'surfer_id': [],
                    'surfer_color': []})
        heat_id = int(heat_id)
        data = self.collect_participants(heat_id)
        return json.dumps(data)
