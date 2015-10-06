import cherrypy
import json
from ..lib.access_conditions import *

from keys import *

class CherrypyWebInterface(object):
    def __init__(self, mount_location = '/'):
        self.mount_location = mount_location
        return


    def _standard_env(self):
        env = {}
        env['mount_loc'] = self.mount_location
        username = cherrypy.session.get(KEY_USERNAME)
        env['global_username'] = username

        ui = cherrypy.session.get(KEY_USER_INFO)
        if ui is None:
            ui = cherrypy.engine.publish(KEY_ENGINE_USER_INFO, username).pop()
        if ui is None:
            ui = {}

        roles = ui.get(KEY_ROLES, [])
        env['global_is_admin'] = KEY_ROLE_ADMIN in roles
        env['global_is_commentator'] = KEY_ROLE_COMMENTATOR in roles
        env['global_is_judge'] = KEY_ROLE_JUDGE in roles
        env['global_is_headjudge'] = KEY_ROLE_HEADJUDGE in roles
        env['global_logged_in'] = bool(username)
        return env


    def render_html(self, context = None, template = None):
        if context is None:
            context = {}
        env = self._standard_env()
        env.update(context)

        if template:
            tpl = cherrypy.engine.publish(KEY_ENGINE_LOOKUP_TEMPLATE, template).pop()
        else:
            tpl = None

        # Render the template into the response body
        if tpl:
            return tpl.render(**env)
        else:
            return env


    def collect_heat_info(self, heat_id):
        query_info = {'heat_id': heat_id}

        # get heat_info from database
        heat_info = cherrypy.engine.publish(KEY_ENGINE_DB_RETRIEVE_HEAT_INFO, query_info).pop()
        if len(heat_info) > 0:
            heat_info = heat_info[0]
        else:
            print 'do_activate_heat: Error: heat_id not in DB'
            return None

        heat_info[KEY_HEAT_ID] = heat_id
        judges = cherrypy.engine.publish(KEY_ENGINE_DB_RETRIEVE_JUDGES_FOR_HEAT, heat_id).pop()
        for judge in judges:
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
        surfer_data = self.collect_participants(heat_id)
        heat_info['participants'] = surfer_data
        return heat_info


    def collect_participants(self, heat_id):
        res = cherrypy.engine.publish(KEY_ENGINE_DB_RETRIEVE_PARTICIPANTS, heat_id).pop()
        import utils
        colors = utils.read_lycra_colors('lycra_colors.csv')
        seeds = []
        for idx, participant in enumerate(res):
            color = participant.get('surfer_color')
            seeds.append( (idx, int(colors.get(color, {}).get('SEEDING', len(colors) + idx))) )
        data = {}
        for p, seed in sorted(seeds, key=lambda x: x[1]):
            participant = res[p]
            for key, val in participant.items():
                data.setdefault(key, []).append(val)
            #id = participant.get('surfer_id')
            color = participant.get('surfer_color')
            color_hex = colors.get(color, {}).get('HEX')
            #data.setdefault('surfer_ids', []).append(id)
            ## TODO: insert 'surfer_names'
            #data.setdefault('surfer_colors', []).append(color)
            data.setdefault('surfer_color_hex', []).append(color_hex)
        return data
