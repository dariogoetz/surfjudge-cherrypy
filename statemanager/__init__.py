
class Heat(object):
    def __init__(self, heat_id):
        self.active = False
        self.judges = []
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
        self.tournaments = {}
        
    def add_tournament(self, tournament):
        self.tournaments[tournament.tournament_id] = tournament