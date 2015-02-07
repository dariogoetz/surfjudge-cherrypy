import cherrypy
from ..lib.access_conditions import *

class SurfJudgeWebInterface(object):
    def __init__(self):
        pass

    @cherrypy.expose
    #@require(is_admin())
    @cherrypy.tools.render(template = 'test_bootstrap_advanced.html')
    def index(self, test=None, buh=None):
        context = {}
        context['title'] = 'Cool Jinja2-rendered file'
        context['description'] = 'Some description of this awesome file'
        context['message'] = 'Why, you again...?'
        return context


    @cherrypy.expose
    @require(is_admin()) # at the moment, everyone is admin
    @cherrypy.tools.render(template='judge_panel.html')
    def judge_panel(self):
        data = {}
        data['judge_name'] = 'Christian'
        data['judge_number'] = '1234'
        data['surfer_colors'] = ['red', 'blue']
        data['n_surfers'] = len(data['surfer_colors'])
        return data


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
