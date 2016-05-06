import json
import threading

HEAT_ORDERS_FILENAME = 'heat_orders.json'
ADVANCING_SURFERS_FILENAME = 'advancing_surfers.json'
SEEDING_INFO_FILENAME = 'seeding_info.json'
CURRENT_HEAT_ID_FILENAME = 'current_heat_ids.json'

# tournament_data is a dictionary
# tournament_id
#   --> info
#   --> heat_order (list of heat_ids)

import tournament_generators

class TournamentManager(object):
    def __init__(self, surfjudge):

        # TODO: as weakref
        self._surfjudge = surfjudge

        self._lock = threading.RLock()

        self.heat_orders = None
        self.advancing_surfers = None
        self.current_heat_id = None
        self._load_heat_orders()
        self._load_advancing_surfers()
        self._load_seeding_info()
        self._load_current_heat()

        self._clean_data()


        self.tournament_generators = {}
        self.tournament_generators['standard'] = tournament_generators.StandardHeatStructureGenerator()

    def _clean_data(self):
        heats = self._surfjudge.database.get_heats({})
        tournaments = self._surfjudge.database.get_tournaments({})
        heat_ids = set([h['id'] for h in heats])
        tournament_ids = set([t['id'] for t in tournaments])

        self._clean_heat_orders(tournament_ids, heat_ids)
        self._clean_advancing_surfers(tournament_ids, heat_ids)
        self._clean_seeding_info(tournament_ids, heat_ids)
        self._clean_current_heat_id(tournament_ids, heat_ids)


    def _clean_heat_orders(self, tournament_ids, heat_ids):
        import copy
        heat_order_tids = self.heat_orders.keys()
        for tid in heat_order_tids:
            if tid not in tournament_ids:
                print 'tournament_manager: cleaning heat_order -> tournament {}'.format(tid)
                del self.heat_orders[tid]
                continue
            hids = copy.copy(self.heat_orders[tid].get('heat_order', []))
            for hid in hids:
                if hid not in heat_ids:
                    print 'tournament_manager: cleaning heat_order -> heat {} in tournament {}'.format(hid, tid)
                    self.heat_orders[tid]['heat_order'].remove(hid)
        with self._lock:
            self._write_heat_orders()


    def _clean_advancing_surfers(self, tournament_ids, heat_ids):
        advancing_surfer_hids = self.advancing_surfers.keys()
        for hid in advancing_surfer_hids:
            if hid not in heat_ids:
                print 'tournament_manager: cleaning advancing_surfers -> heat {}'.format(hid)
                del self.advancing_surfers[hid]
                continue
            seeds = self.advancing_surfers[hid].keys()
            for seed in seeds:
                if self.advancing_surfers[hid][seed]['from_heat_id'] not in heat_ids:
                    print 'tournament_manager: cleaning advancing_surfers -> seed {} in heat {}'.format(seed, hid)
                    del self.advancing_surfers[hid][seed]
        with self._lock:
            self._write_advancing_surfers()


    def _clean_seeding_info(self, tournament_ids, heat_ids):
        import copy
        seeding_info_tids = self.seeding_info.keys()
        for tid in seeding_info_tids:
            if tid not in tournament_ids:
                print 'tournament_manager: cleaning seeding_info -> tournament {}'.format(tid)
                del self.seeding_info[tid]
                continue
            hids = copy.copy(self.seeding_info[tid])
            for hid in hids:
                if hid not in heat_ids:
                    print 'tournament_manager: cleaning seeding_info -> heat {} in tournament {}'.format(hid, tid)
                    self.seeding_info[tid].remove(hid)
        with self._lock:
            self._write_seeding_info()


    def _clean_current_heat_id(self, tournament_ids, heat_ids):
        current_heat_tids = self.current_heat_id.keys()
        for tid in current_heat_tids:
            if tid not in tournament_ids or self.current_heat_id[tid] not in heat_ids:
                print 'tournament_manager: cleaning current_heat_id -> tournament {}'.format(tid)
                del self.current_heat_id[tid]
        with self._lock:
            self._write_current_heat_id()


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

            self.heat_orders = {}
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

    def _load_seeding_info(self):
        with self._lock:
            tmp = None
            try:
                with open(SEEDING_INFO_FILENAME, 'rb') as fp:
                    tmp = json.load(fp)
            except IOError as e:
                try:
                    print 'TournamentManager: initializing seeding info file'
                    json.dump({}, open(SEEDING_INFO_FILENAME, 'wb'))
                except:
                    print 'TournamentManager: could not read/initialize seeding info file'
            self.seeding_info = {}
            if tmp is not None:
                for tid, heat_ids in tmp.items():
                    self.seeding_info[int(tid)] = heat_ids
        return

    def _load_current_heat(self):
        with self._lock:
            tmp = None
            try:
                with open(CURRENT_HEAT_ID_FILENAME, 'rb') as fp:
                    tmp = json.load(fp)
            except IOError as e:
                try:
                    print 'TournamentManager: initializing current heat ids'
                    json.dump({}, open(CURRENT_HEAT_ID_FILENAME, 'wb'))
                except:
                    print 'TournamentManager: could not read/initialize current heat ids'
            self.current_heat_id = {}
            if tmp is not None:
                # make ids into ints
                for tid, data in tmp.items():
                    self.current_heat_id[int(tid)] = data
        return


    def _write_advancing_surfers(self):
        with self._lock:
            with open(ADVANCING_SURFERS_FILENAME, 'wb') as fp:
                json.dump(self.advancing_surfers, fp, indent=4)
        return


    def _write_seeding_info(self):
        with self._lock:
            with open(SEEDING_INFO_FILENAME, 'wb') as fp:
                json.dump(self.seeding_info, fp, indent=4)
        return


    def _write_current_heat_id(self):
        with self._lock:
            with open(CURRENT_HEAT_ID_FILENAME, 'wb') as fp:
                 json.dump(self.current_heat_id, fp, indent=4)
        return

    def set_current_heat_id(self, tournament_id, heat_id):
        self.current_heat_id[int(tournament_id)] = heat_id
        return

    def get_current_heat_id(self, tournament_id):
        default_heat_id = self.heat_orders.get(int(tournament_id), {}).get('heat_order', [None])[0]
        res = self.current_heat_id.get(int(tournament_id), default_heat_id)
        if res is None:
            print 'TournamentManager: no current heat id for Tournament {} known and no heat order available'.format(tournament_id)
        self._write_current_heat_id()
        return res


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
            order.insert(orig_pos-1, order.pop(orig_pos))
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


        # determine heat order such that they are inserted in correct order
        tmp = {}
        for (r, h) in new_heats:
            tmp.setdefault(r, []).append( (r, h) )
        new_heats_with_idx = []
        idx = 0
        for r in sorted(tmp, reverse=True):
            for rh in sorted(tmp[r]):
                new_heats_with_idx.append( (idx, rh) )


        seeding_round = max(new_heats, key=lambda x: x[0])[0]
        seeding_info = []
        for idx, (r, h) in sorted(new_heats_with_idx, key=lambda x: x[0]):
            name = self.tournament_generators[tournament_generator].get_name(r,h, max(tree.keys()) + 1)

            # call database
            hid = self._surfjudge.database.insert_heat({'name': name, 'tournament_id': tournament_id, 'category_id': category_id})
            treeid2heatid[(r,h)] = hid
            if r == seeding_round:
                seeding_info.append(hid)

        advancing_surfers = {}
        for r, heats in tree.items():
            for h, participants in heats.items():
                for seed, (from_round, from_heat, from_place) in participants.items():
                    advancing_surfers.setdefault(treeid2heatid[(r,h)], {})[seed] = {'from_heat_id': treeid2heatid[(from_round, from_heat)], 'from_place':  from_place}

        with self._lock:
            self.seeding_info[tournament_id] = seeding_info
            self._write_seeding_info()
            self.advancing_surfers.update(advancing_surfers)
            self._write_advancing_surfers()
        return advancing_surfers, seeding_info
