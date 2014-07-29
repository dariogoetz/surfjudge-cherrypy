import cherrypy
from remote.cherrypy.lib.access_conditions import *

class SurfJudgeWebInterface(object):
    def __init__(self):
        pass

    @cherrypy.expose
    @require(is_admin())
    @cherrypy.tools.render(template = 'test.html')
    def index(self, test=None, buh=None):
        context = {}
        context['title'] = 'Cool Jinja2-rendered file'
        context['description'] = 'Some description of this awesome file'
        context['message'] =  cherrypy.request.query_string #'Why, you again...?'
        return context


