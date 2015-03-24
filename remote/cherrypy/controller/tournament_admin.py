import cherrypy
import json
from ..lib.access_conditions import *
from . import CherrypyWebInterface

from keys import *

class TournamentAdminWebInterface(CherrypyWebInterface):

    @cherrypy.expose
    @cherrypy.tools.render(template='tournament_admin/edit_tournaments.html')
    def edit_tournaments(self):
        return {}
