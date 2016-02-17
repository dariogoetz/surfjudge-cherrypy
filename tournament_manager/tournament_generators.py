class HeatStructureGenerator(object):
    def __init__(self):
        pass

    def generate_heat_structure(self):
        pass

    def get_name(self, round, heat, nrounds):
        pass


class StandardHeatStructureGenerator(HeatStructureGenerator):
    # tool to generate a 4-heat 2-advance tree

    def advances_from(self, r, h, place):
        def get_other_branch(r,h):
            if r == 0:
                return h
            else:
                return h - h%2 + (h+1)%2

        #assert h < n_heats(r, mode)
        from_round = r+1
        from_place = place/2

        from_heat = None
        if place < 2:
            from_heat = 2*h + place%2
        elif place < 4:
            from_heat = 2 * get_other_branch(r, h) + place%2
        else:
            print 'error'
        return from_round, from_heat, from_place


    def get_round_name(self, r):
        round_names = ['Final', 'Semi-Final', 'Quarter-Final']
        if r < len(round_names):
            return round_names[r]
        else:
            return 'Round {}'.format(nrounds - r + 1)

    def get_name(self, r, h, nrounds):
        round_names = ['Final', 'Semi-Final', 'Quarter-Final']
        if r == 0:
            return round_names[r]
        elif r < len(round_names):
            prefix = round_names[r]
        else:
            prefix = 'Round {} Heat'.format(nrounds - r + 1)
        return '{} {}'.format(prefix, h+1)


    def generate_heat_structure(self, nparticipants):
        import math
        #nrounds = int(math.ceil(math.log(math.ceil(nparticipants/4.0), 2)))
        res = {}
        round = 0
        nheats = 1
        while nparticipants > nheats*4:
            for heat in range(nheats):
                advancing_from = {}
                for place in range(4):
                    advancing_from[place] = self.advances_from(round, heat, place)
                res.setdefault(round, {})[heat] = advancing_from
            round += 1
            nheats = 2**round
        return res




#def make_mode(*args):
#    args = list(args)
#    res = []
#    maxpart = args.pop(0)
#    res.append({'maxpart' : maxpart})
#    while len(args) > 0:
#        nadvance = args.pop(0)
#        maxpart = args.pop(0)
#        res.append({'maxpart': maxpart, 'nadvance': nadvance})
#    return res


# mode = [{nadvance:0, maxpart:x}, nadvance(1), maxpart(1)
#def n_heats(r, mode):
#    if r == 0:
#        return 1
#    return mode[r-1]['maxpart'] / mode[r]['nadvance'] * n_heats(r-1, mode)
