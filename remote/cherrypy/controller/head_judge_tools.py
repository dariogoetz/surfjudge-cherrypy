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
        res = cherrypy.engine.publish(KEY_ENGINE_DB_RETRIEVE_JUDGE_ACTIVITIES, {}).pop()
        print '********', res
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
        res = cherrypy.engine.publish(KEY_ENGINE_DB_RETRIEVE_JUDGE_ACTIVITIES, {'heat_id':heat_id}).pop()
        heat_info = {}
        for heat_judge in res:
            if heat_judge[KEY_HEAT_ID] != heat_id:
                continue
            judge_id = heat_judge[KEY_JUDGE_ID]
            first_name = heat_judge['judge_first_name']
            last_name = heat_judge['judge_last_name']
            username = heat_judge['judge_username']
            heat_name = heat_judge['heat_name']
            heat_info[judge_id] = {KEY_HEAT_ID: heat_id,
                                   KEY_JUDGE_ID: judge_id,
                                   'judge_first_name': first_name,
                                   'judge_last_name': last_name,
                                   'judge_username': username,
                                   'heat_name': heat_name}

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
    def do_get_active_heat_info(self, heat_id = None, **kwargs):
        if heat_id is not None:
            heat_id = int(heat_id)

        heat_info = cherrypy.engine.publish(KEY_ENGINE_SM_GET_ACTIVE_HEAT_INFO, heat_id).pop()
        res = []
        for heat_judges in heat_info.values():
            res.extend(heat_judges.values())
        return json.dumps(res)
