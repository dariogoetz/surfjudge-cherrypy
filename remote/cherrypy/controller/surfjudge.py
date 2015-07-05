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
    @cherrypy.tools.render(template = 'base_template.html')
    def index(self):
        context = self._standard_env()

        if context['global_username']:
            message = 'Why, you again...? Welcome back, {}!'.format(context['global_username'])
        else:
            message = 'Welcome.'

        context['title'] = 'Cool Jinja2-rendered file'
        context['description'] = 'Some description of this awesome file'
        context['message'] = message
        return context


    @cherrypy.expose
    #@require(is_admin()) # later ask for judge or similar
    @cherrypy.tools.render(template='judge_panel.html')
    def judge_panel(self):
        #judge_id = cherrypy.session.get(KEY_JUDGE_ID)
        #heats = cherrypy.engine.publish(KEY_ENGINE_SM_GET_HEATS_FOR_JUDGE, judge_id).pop()

        data = self._standard_env()
        data['judge_name'] = 'Christian'
        data['judge_number'] = '1234'
        data['surfer_color_names'] = ['red', 'blue', 'green']
        data['surfer_color_colors'] = {'red': '#FF8888', 'blue': '#8888FF', 'green': '#88FF88'}
        data['n_surfers'] = len(data['surfer_color_names'])
        data['number_of_waves'] = 10
        return data

    @cherrypy.expose
    #@require(is_admin()) # later ask for judge or similar
    @cherrypy.tools.render(template='commentator_panel.html')
    def commentator_panel(self):
        data = self._standard_env()
        data['judge_name'] = 'Christian'
        data['judge_number'] = '1234'
        data['surfer_color_names'] = ['red', 'blue', 'green']
        data['surfer_color_colors'] = {'red': '#FF8888', 'blue': '#8888FF', 'green': '#88FF88'}
        data['n_surfers'] = len(data['surfer_color_names'])
        data['number_of_waves'] = 10
        return data

    @cherrypy.expose
    @require(has_roles(KEY_ROLE_JUDGE))
    def do_query_scores(self, heat_id = None):
        if heat_id is None:
            judge_id = cherrypy.session.get(KEY_JUDGE_ID)
            if judge_id is None:
                print 'Error: Not registered as judge'
                return '[]'
            heats = cherrypy.engine.publish(KEY_ENGINE_SM_GET_HEATS_FOR_JUDGE, judge_id).pop()
            if len(heats) == 0:
                print 'Error: No heat specified and no active heat available'
                return '[]'
            heat_id = heats.values()[0][KEY_HEAT_ID]

        query_info = {KEY_HEAT_ID: int(heat_id)}

        scores = cherrypy.engine.publish(KEY_ENGINE_DB_RETRIEVE_SCORES, query_info).pop()
        out_scores = {}
        for score in scores:
            out_scores.setdefault(score['color'], []).append( (score['wave'], score['score']) )

        print out_scores
        for color in out_scores:
            print out_scores[color]
            sorted_pairs = sorted(out_scores[color], key=lambda x: x[0])
            out_scores[color] = [score for (wave, score) in sorted_pairs]

        return json.dumps(out_scores)

    @cherrypy.expose
    @require(has_roles(KEY_ROLE_JUDGE))
    def do_insert_score(self, score = None, heat_id = None):
        if score is None:
            return
        #score = score.encode('utf-8')
        db_data = json.loads(score)

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
    def do_get_active_heats(self, **kwargs):
        heat_info = cherrypy.engine.publish(KEY_ENGINE_SM_GET_ACTIVE_HEAT_INFO, None).pop()
        return json.dumps(heat_info.values())


    @cherrypy.expose
    @cherrypy.tools.render(template = 'simple_message.html')
    def simple_message(self, msg = None):
        env = {}
        env['message'] = msg
        return env
