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
    def do_query_scores_for_heat(self):
        # get heat_id for current judge from state object
        # query scores for heat_id in db
        query_info = {}
        scores = cherrypy.engine.publish(KEY_ENGINE_DB_RETRIEVE_SCORES, query_info).pop()
        return json.dumps(scores)

    @cherrypy.expose
    @require(has_roles(KEY_ROLE_JUDGE))
    def do_query_scores(self):
        query_info = {}
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
    #@require(has_roles(KEY_ROLE_JUDGE))
    def do_insert_score(self, score = None):
        if score is None:
            return
        #score = score.encode('utf-8')
        db_data = json.loads(score)

        judge_id = cherrypy.session.get(KEY_JUDGE_ID)
        if judge_id is None:
            return 'Error: Not registered as judge'
        db_data['judge_id'] = judge_id

        # TODO: get heat_id for judge_id from state-manager
        heat_id = 0
        db_data['heat_id'] = heat_id

        res = cherrypy.engine.publish(KEY_ENGINE_DB_INSERT_SCORE, db_data).pop()
        return res

    @cherrypy.expose
    #@require(is_admin())
    def javascript_request(self, parameter = None):
        #database request
        #store in some variable
        #return the variable
        result = 'hallo'
        return result


    @cherrypy.expose
    @cherrypy.tools.render(template = 'simple_message.html')
    def simple_message(self, msg = None):
        env = {}
        env['message'] = msg
        return env
