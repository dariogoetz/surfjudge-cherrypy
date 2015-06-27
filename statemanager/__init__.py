from keys import *
class Heat(object):
    def __init__(self, heat_id):
        self.active = False
        self.judges = set([])
        self.heat_id = heat_id
        return

    def add_judge(self, judge_id):
        self.judges.append(judge)

class Class(object):
    def __init__(self, class_id):
        self.heats = {}
        self.class_id = class_id

    def add_heat(self, heat):
        self.heats[heat.heat_id] = heat
        return



class Tournament(object):
    def __init__(self, tournament_id):
        self.active = False
        self.tournament_id = tournament_id

    def add_class(self, cl):
        self.classes[cl.class_id] = cl
        return


class StateManager(object):

    def __init__(self):
        self.active_tournaments = {}
        self.active_heats = {}

    def add_tournament(self, tournament):
        self.active_tournaments[tournament.tournament_id] = tournament

    def activate_heat(self, heat_id, heat_info):
        if heat_id is None or heat_info is None:
            return

        # get judges that are supposed to judge this heat from database
        # TODO

        # get tournament and class corresponding to heat from database
        # TODO

        self.active_heats[heat_id] = heat_info
        return

    def deactivate_heat(self, heat_id):
        if heat_id in self.active_heats:
            del self.active_heats[heat_id]
        return

    def get_active_heat_info(self, heat_id=None):
        if heat_id is None:
            return self.active_heats
        else:
            if heat_id in self.active_heats:
                return {heat_id: self.active_heats[heat_id]}
            else:
                return {}
