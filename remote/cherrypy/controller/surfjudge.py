import cherrypy
import json
from ..lib.access_conditions import *
from . import CherrypyWebInterface

from keys import *

class SurfJudgeWebInterface(CherrypyWebInterface):
    #def __init__(self, *args, **kwargs):
    #    CherrypyWebInterface.__init__(self, *args, **kwargs)
    #    return


    @cherrypy.expose
    #@require(is_admin())
    @cherrypy.tools.render(template = 'index.html')
    def index(self):
        context = self._standard_env()
        heats_info = cherrypy.engine.publish(KEY_ENGINE_SM_GET_ACTIVE_HEAT_INFO, None).pop()
        for heat_id, heat in heats_info.items():
            query_info = {KEY_HEAT_ID: int(heat_id)}
            # TODO: maybe store current scores in state object for faster access
            scores = cherrypy.engine.publish(KEY_ENGINE_DB_RETRIEVE_SCORES, query_info).pop()
            heat['scores'] = json.loads(self.do_query_scores(heat_id=heat_id, get_for_all_judges=1))
        context['active_heats'] = heats_info
        return context


    @cherrypy.expose
    @cherrypy.tools.render(template='judge_hub.html')
    def judge_hub(self):
        data = self._standard_env()
        return data


    @cherrypy.expose
    #@require(is_admin()) # later ask for judge or similar
    @cherrypy.tools.render(template='judge_panel.html')
    def do_get_judge_panel(self, heat_id = None):
        if heat_id is None:
            return ''

        heat_id = int(heat_id)
        judge_id = cherrypy.session.get(KEY_JUDGE_ID)
        heats = cherrypy.engine.publish(KEY_ENGINE_SM_GET_HEATS_FOR_JUDGE, judge_id).pop()
        data = self._standard_env()
        if len(heats) == 0:
            return ''

        if heat_id not in [h['heat_id'] for h in heats.values()]:
            print 'do_get_judge_panel: Is not judge for requested heat_id'
            return 'res'

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
        return data

    @cherrypy.expose
    #@require(is_admin()) # later ask for judge or similar
    @cherrypy.tools.render(template='commentator_hub.html')
    def commentator_hub(self):
        data = self._standard_env()
        return data

    @cherrypy.expose
    #@require(is_admin()) # later ask for judge or similar
    @cherrypy.tools.render(template='commentator_panel.html')
    def do_get_commentator_panel(self, heat_id=None):
        if heat_id is None:
            return ''
        heat_id = int(heat_id)

        data = self._standard_env()

        heat_info = cherrypy.engine.publish(KEY_ENGINE_SM_GET_ACTIVE_HEAT_INFO, heat_id).pop().get(heat_id)
        surfer_data = heat_info['participants']
        ids = map(str, surfer_data.get('surfer_id', []))
        colors = map(str, surfer_data.get('surfer_color', []))
        colors_hex = map(str, surfer_data.get('surfer_color_hex', []))
        data['heat_id'] = heat_id
        data['surfers'] = dict(zip(ids, colors))
        data['surfer_color_names'] = colors
        data['surfer_color_colors'] = dict(zip(colors, colors_hex))
        data['number_of_waves'] = int(heat_info['number_of_waves'])
        return data


    @cherrypy.expose
    @require(has_one_role(KEY_ROLE_JUDGE, KEY_ROLE_COMMENTATOR))
    def do_query_scores(self, heat_id = None, judge_id = None, get_for_all_judges = None):
        roles = cherrypy.session.get(KEY_USER_INFO, {}).get(KEY_ROLES, [])

        if get_for_all_judges and KEY_ROLE_COMMENTATOR in roles:
            judge_id = None
        elif judge_id is None:
            judge_id = cherrypy.session.get(KEY_JUDGE_ID)
            if judge_id is None:
                print 'Error in "do_query_scores": No judge_id specified and is no judge'
                return '[]'
        else:
            if not KEY_ROLE_COMMENTATOR in roles:
                print 'Error in "do_query_scores": judge_id specified but is no commentator'
                return '[]'

        if heat_id is None:
            if judge_id is None:
                print 'Error in "do_query_scores": No heat_id provided and no judge_id either (is probably commentator and requested for all judges)'
                return '[]'
            heats = cherrypy.engine.publish(KEY_ENGINE_SM_GET_HEATS_FOR_JUDGE, judge_id).pop()
            if len(heats) == 0:
                print 'Error in "do_query_scores": No heat specified and no active heat available'
                return '[]'
            heat_id = heats.values()[0][KEY_HEAT_ID]

        heat_id = int(heat_id)
        query_info = {KEY_HEAT_ID: heat_id}

        if judge_id is not None:
            query_info[KEY_JUDGE_ID] = int(judge_id)

        scores = cherrypy.engine.publish(KEY_ENGINE_DB_RETRIEVE_SCORES, query_info).pop()
        heat_info = cherrypy.engine.publish(KEY_ENGINE_SM_GET_ACTIVE_HEAT_INFO, heat_id).pop().get(heat_id)
        if heat_info is None:
            return '[]'

        participants = heat_info['participants']
        if 'surfer_id' not in participants or 'surfer_color' not in participants:
            print 'do_query_scores: no participants'
            return '[]'
        id2color = dict(zip(participants.get('surfer_id', []), participants.get('surfer_color', [])))

        out_scores = {}
        for score in scores:
            out_scores.setdefault(score['judge_id'], {}).setdefault(id2color[int(score['surfer_id'])], []).append( (score['wave'], score['score']) )

        for jid, s in out_scores.items():
            for color, vals in s.items():
                sorted_pairs = sorted(vals, key=lambda x: x[0])
                out_scores[jid][color] = [score for (wave, score) in sorted_pairs]

        if judge_id is not None:
            # not all judges scores were requested
            out_scores = out_scores.get(judge_id, {})
        else:
            # filter out only judges that are active for that heat
            judges = heat_info.get('judges', [])
            judges_with_scores = out_scores.keys()
            for jid in judges_with_scores:
                if jid not in judges:
                    del out_scores[jid]
                    print 'do_query_scores: filtered out scores for inactive judge {}'.format(jid)
        return json.dumps(out_scores)

    @cherrypy.expose
    @require(has_all_roles(KEY_ROLE_JUDGE))
    def do_insert_score(self, score = None, heat_id = None):
        if score is None:
            return
        #score = score.encode('utf-8')
        score = json.loads(score)
        db_data = score
        print score

        judge_id = cherrypy.session.get(KEY_JUDGE_ID)
        if judge_id is None:
            print 'Error: Not registered as judge'
            return
        db_data['judge_id'] = judge_id

        # TODO: get heat_id for judge_id from state-manager
        heats = cherrypy.engine.publish(KEY_ENGINE_SM_GET_HEATS_FOR_JUDGE, judge_id).pop()
        active_heat_id = None
        if len(heats) > 0:
            active_heat_id = heats.values()[0][KEY_HEAT_ID]

        if heat_id is None:
            heat_id = active_heat_id

        if heat_id is None:
            print 'Error: No heat_id specified and judge has no active heat'
            return

        if int(heat_id) != int(active_heat_id): # and not is_admin... later: ask for admin roles
            print 'Error: Specified heat_id does not coincide with active heat of judge'
            return

        db_data['heat_id'] = int(heat_id)
        heat_info = cherrypy.engine.publish(KEY_ENGINE_SM_GET_ACTIVE_HEAT_INFO, heat_id).pop().get(heat_id)
        participants = heat_info['participants']
        color2id = dict(zip(participants['surfer_color'], participants['surfer_id']))
        db_data['surfer_id'] = int(color2id[score['color']])
        del db_data['color']

        res = cherrypy.engine.publish(KEY_ENGINE_DB_INSERT_SCORE, db_data).pop()
        return res


    @cherrypy.expose
    def do_get_active_heat_info(self, heat_id = None, **kwargs):
        if heat_id is not None:
            heat_id = int(heat_id)
        else:
            judge_id = cherrypy.session.get(KEY_JUDGE_ID)
            if judge_id is None:
                print 'Error: Not registered as judge and no heat_id specified'
                return '{}'
            heats = cherrypy.engine.publish(KEY_ENGINE_SM_GET_HEATS_FOR_JUDGE, judge_id).pop()
            if len(heats) == 0:
                print 'Error: No heat specified and judge has no active heats'
                return '{}'
            heat_id = heats.keys()[0]
        heat_info = cherrypy.engine.publish(KEY_ENGINE_SM_GET_ACTIVE_HEAT_INFO, heat_id).pop().get(heat_id)
        return json.dumps(heat_info)


    @cherrypy.expose
    def do_get_all_active_heats(self, **kwargs):
        heat_info = cherrypy.engine.publish(KEY_ENGINE_SM_GET_ACTIVE_HEAT_INFO, None).pop()
        return json.dumps(heat_info.values())


    @cherrypy.expose
    @cherrypy.tools.render(template = 'simple_message.html')
    def simple_message(self, msg = None):
        env = {}
        env['message'] = msg
        return env
