import cherrypy
import json
from ..lib.access_conditions import *
from . import CherrypyWebInterface

from keys import *

class HeadJudgeWebInterface(CherrypyWebInterface):


    @cherrypy.expose
    @cherrypy.tools.render(template = 'headjudge/headjudge_panel.html')
    def index(self):
        context = self._standard_env()
        #res = cherrypy.engine.publish(KEY_ENGINE_DB_RETRIEVE_JUDGE_ACTIVITIES, {}).pop()
        return context


    ##############
    # REST stuff #
    ##############

    @cherrypy.expose
    def do_activate_heat(self, heat_id = None, **kwargs):
        if heat_id is None:
            return
        heat_id = int(heat_id)

        # get heat_info from database
        heat_info = {}
        res = cherrypy.engine.publish(KEY_ENGINE_DB_RETRIEVE_HEAT_INFO, heat_id).pop()
        if len(res) > 0:
            res = res[0]

        heat_info[KEY_HEAT_ID] = heat_id
        heat_info[KEY_HEAT_NAME] = res['heat_name']
        heat_info[KEY_TOURNAMENT_NAME] = res['tournament_name']
        heat_info[KEY_EVENT_NAME] = res['event_name']
        res = cherrypy.engine.publish(KEY_ENGINE_DB_RETRIEVE_JUDGES_FOR_HEAT, heat_id).pop()
        for judge in res:
            if judge[KEY_HEAT_ID] != heat_id:
                continue
            judge_id = judge[KEY_JUDGE_ID]
            first_name = judge['first_name']
            last_name = judge['last_name']
            username = judge['username']
            heat_info.setdefault('judges', {})[judge_id] = {KEY_HEAT_ID: heat_id,
                                                            KEY_JUDGE_ID: judge_id,
                                                            'judge_first_name': first_name,
                                                            'judge_last_name': last_name,
                                                            'judge_username': username}
        res = cherrypy.engine.publish(KEY_ENGINE_SM_ACTIVATE_HEAT, heat_id, heat_info).pop()
        return res

    @cherrypy.expose
    def do_deactivate_heat(self, heat_id = None, **kwargs):
        if heat_id is None:
            return
        heat_id = int(heat_id)

        res = cherrypy.engine.publish(KEY_ENGINE_SM_DEACTIVATE_HEAT, heat_id).pop()
        return res

