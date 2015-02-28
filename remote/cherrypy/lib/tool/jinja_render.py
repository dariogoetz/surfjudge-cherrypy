import cherrypy

from keys import *

class JinjaRenderTool(cherrypy.Tool):
    '''
    Renders a given response body context using a Jinja2 template.

    The template is retrieved using the cherrypy engine by calling 'lookup-template' (e.g. using plugin JinjaTemplatePlugin).
    '''

    def __init__(self):
        cherrypy.Tool.__init__(self, 'before_finalize',
                               self._render_template,
                               priority = 50)
        return


    def _render_template(self, template = None):

        # Only render if no error occured
        if cherrypy.response.status > 399:
            return


        # Get context from response body
        context = cherrypy.response.body
        if context is None:
            context = {}

        # Retrieve template from lookup plugin
        template = cherrypy.engine.publish(KEY_ENGINE_LOOKUP_TEMPLATE, template).pop()

        # Render the template into the response body
        if template and isinstance(context, dict):
            cherrypy.response.body = template.render(**context)
        return
