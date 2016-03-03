import json
import threading

HEAT_ORDERS_FILENAME = 'heat_orders.json'
ADVANCING_SURFERS_FILENAME = 'advancing_surfers.json'

# tournament_data is a dictionary
# tournament_id
#   --> info
#   --> heat_order (list of heat_ids)

import tournament_generators

class TournamentManager(object):
    def __init__(self, surfjudge):
        self._lock = threading.RLock()

        self.heat_orders = None
        self.advancing_surfers = None
        self._load_heat_orders()
        self._load_advancing_surfers()


        self.tournament_generators = {}
        self.tournament_generators['standard'] = tournament_generators.StandardHeatStructureGenerator()

        # TODO: as weakref
        self._surfjudge = surfjudge


    def _load_heat_orders(self):
        with self._lock:
            tmp = None
            try:
                with open(HEAT_ORDERS_FILENAME, 'rb') as fp:
                    tmp = json.load(fp)
            except IOError as e:
                try:
                    print 'TournamentManager: initializing heat order file'
                    json.dump({}, open(HEAT_ORDERS_FILENAME, 'wb'))
                except:
                    print 'TournamentManager: could not read/initialize heat order file'
            if tmp is not None:
                self.heat_orders = {int(key): val for key, val in tmp.items()}
        return

    def _write_heat_orders(self):
        with self._lock:
            with open(HEAT_ORDERS_FILENAME, 'wb') as fp:
                json.dump(self.heat_orders, fp)
        return

    def _load_advancing_surfers(self):
        with self._lock:
            tmp = None
            try:
                with open(ADVANCING_SURFERS_FILENAME, 'rb') as fp:
                    tmp = json.load(fp)
            except IOError as e:
                try:
                    print 'TournamentManager: initializing advancing surfers file'
                    json.dump({}, open(ADVANCING_SURFERS_FILENAME, 'wb'))
                except:
                    print 'TournamentManager: could not read/initialize advancing surfers file'
            self.advancing_surfers = {}
            if tmp is not None:
                for hid, data in tmp.items():
                    for place, from_data in data.items():
                        self.advancing_surfers.setdefault(int(hid), {})[int(place)] = from_data
        return

    def _write_advancing_surfers(self):
        with self._lock:
            with open(ADVANCING_SURFERS_FILENAME, 'wb') as fp:
                json.dump(self.advancing_surfers, fp, indent=4)
        return


    def get_heat_order(self, tournament_id):
        return self.heat_orders.get(tournament_id, {}).get('heat_order', [])

    def set_heat_order(self, tournament_id, list_of_heat_ids):
        with self._lock:
            self.heat_orders[tournament_id] = {'heat_order': list_of_heat_ids}
        return

    def raise_heat(self, tournament_id, heat_id):
        if tournament_id not in self.heat_orders:
            print 'insert_heat_at: tournament_id not in data'
            return
        if orig_pos == 0:
            return

        order = self.heat_orders[tournament_id]['heat_order']

        try:
            orig_pos = order.index(heat_id)
        except:
            # heat is not in data
            print 'raise_heat: Heat is not in heat_orders. Cannot raise'
            return

        with self._lock:
            val = order.pop(orig_pos)
            order.insert(orig_pos-1, order.opo(orig_pos))
        return

    def lower_heat(self, tournament_id, heat_id):
        if tournament_id not in self.heat_orders:
            print 'insert_heat_at: tournament_id not in data'
            return

        order = self.heat_orders[tournament_id]['heat_order']

        try:
            orig_pos = order.index(heat_id)
        except:
            # heat is not in data
            print 'raise_heat: Heat is not in heat_orders. Cannot lower'
            return

        with self._lock:
            order.insert(orig_pos+1, order.pop(orig_pos))
        return

    def place_heat_at(self, tournament_id, heat_id, position):
        if tournament_id not in self.heat_orders:
            print 'insert_heat_at: tournament_id not in data'
            return

        order = self.heat_orders[tournament_id]['heat_order']

        if position > len(order):
            print 'insert_heat_at: position is off limits'
            return

        orig_pos = None
        try:
            orig_pos = order.index(heat_id)
        except:
            # heat was not yet in tournament
            pass

        with self._lock:
            if orig_pos is not None:
                order.pop(orig_pos)

            order.insert(position, heat_id)
        return


    def append_heat(self, tournament_id, heat_id):
        with self._lock:
            order = self.heat_orders.setdefault(tournament_id, {}).setdefault('heat_order', [])
            if heat_id in order:
                order.remove(heat_id)
            order.append(heat_id)
        return


    def set_advancing_surfer(self, heat_id, seed, from_heat_id, from_place):
        with self._lock:
            self.advancing_surfers.setdefault(heat_id, {})[seed] = {'surfer_id': surfer_id, 'from_heat_id': from_heat_id, 'from_place': from_place}
        return

    def get_advancing_surfers(self, heat_id, seed=None):
        res = self.advancing_surfers.get(heat_id, {})
        if seed is not None:
            return res.get(seed)
        else:
            return res


    def generate_heats(self, nparticipants, tournament_id=None, category_id=None, tournament_generator='standard'):
        treeid2heatid = {}
        tree = self.tournament_generators[tournament_generator].generate_heat_structure(nparticipants)

        # determine all heats that will be generated
        new_heats = set()
        for r, heats in tree.items():
            for h, participants in heats.items():
                new_heats.add( (r, h) )
                for p, (from_round, from_heat, from_place) in participants.items():
                    new_heats.add( (from_round, from_heat) )

        for (r, h) in new_heats:
            name = self.tournament_generators[tournament_generator].get_name(r,h, max(tree.keys()) + 1)

            # call database
            hid = self._surfjudge.database.insert_heat({'name': name, 'tournament_id': tournament_id, 'category_id': category_id})
            treeid2heatid[(r,h)] = hid

        advancing_surfers = {}
        for r, heats in tree.items():
            for h, participants in heats.items():
                for seed, (from_round, from_heat, from_place) in participants.items():
                    advancing_surfers.setdefault(treeid2heatid[(r,h)], {})[seed] = {'from_heat_id': treeid2heatid[(from_round, from_heat)], 'from_place':  from_place}

        with self._lock:
            self.advancing_surfers.update(advancing_surfers)
        self._write_advancing_surfers()
        return advancing_surfers

