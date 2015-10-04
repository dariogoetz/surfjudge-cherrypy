import cherrypy
import json
from ..lib.access_conditions import *
from . import CherrypyWebInterface

from keys import *

class HeadJudgeWebInterface(CherrypyWebInterface):


    @cherrypy.expose
    @cherrypy.tools.render(template = 'headjudge/start_stop_heats.html')
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
            print heats.values()
            context['heats'][cid] = sorted(heats.values(), key=lambda x:x['name'])
        return context

    @cherrypy.expose
    @cherrypy.tools.render(template='headjudge/judge_activities_panel.html')
    def do_get_judge_activities_panel(self, heat_id=None):
        if heat_id is None:
            return ''
        heat_id = int(heat_id)

        data = self._standard_env()

        heat_info = cherrypy.engine.publish(KEY_ENGINE_SM_GET_ACTIVE_HEAT_INFO, heat_id).pop().get(heat_id)
        surfer_data = heat_info['participants']
        ids = map(str, surfer_data.get('surfer_id', []))
        colors = map(str, surfer_data.get('surfer_color', []))
        colors_hex = map(str, surfer_data.get('surfer_color_hex', []))
        judge_ids = sorted(heat_info['judges'].keys())
        data['heat_id'] = heat_id
        data['surfers'] = dict(zip(ids, colors))
        data['surfer_color_names'] = colors
        data['number_of_waves'] = int(heat_info['number_of_waves'])
        data['judge_ids']= judge_ids 
        data['surfer_color_colors'] = dict(zip(colors, colors_hex))
        return data
        
        
        

    @cherrypy.expose
    def do_get_participating_surfers(self, heat_id=None):
        if heat_id == '' or heat_id is None:
            return json.dumps({'surfer_id': [],
                    'surfer_color': []})
        heat_id = int(heat_id)
        data = self.collect_participants(heat_id)
        return json.dumps(data)
