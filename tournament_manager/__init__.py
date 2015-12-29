import json

HEAT_ORDERS_FILENAME = 'heat_orders.json'
ADVANCING_SURFERS_FILENAME = 'advancing_surfers.json'

# tournament_data is a dictionary
# tournament_id
#   --> info
#   --> heat_order (list of heat_ids)

class TournamentManager(object):
    def __init__(self):
        self.heat_orders = None
        self.advancing_surfers = None
        self._load_heat_orders()
        self._load_advancing_surfers()


    def _load_heat_orders(self):
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
        with open(HEAT_ORDERS_FILENAME, 'wb') as fp:
            json.dump(self.heat_orders, fp)
        return

    def _load_advancing_surfers(self):
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
        if tmp is not None:
            self.advancing_surfers = {int(key): val for key, val in tmp.items()}
        return

    def _write_advancing_surfers(self):
        with open(ADVANCING_SURFERS_FILENAME, 'wb') as fp:
            json.dump(self.advancing_surfers, fp)
        return


    def get_heat_order(self, tournament_id):
        return self.heat_orders.get(tournament_id, {}).get('heat_order', [])

    def set_heat_order(self, tournament_id, list_of_heat_ids):
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

        if orig_pos is not None:
            order.pop(orig_pos)

        order.insert(position, heat_id)
        return


    def append_heat(self, tournament_id, heat_id):
        order = self.heat_orders.setdefault(tournament_id, {}).setdefault('heat_order', [])
        if heat_id in order:
            order.remove(heat_id)
        order.append(heat_id)
        return


    def set_advancing_surfer(self, heat_id, surfer_id, color, advancing_from_heat_id, place):
        self.advancing_surfers.setdefault(heat_id, {}).setdefault('advancing_surfers', {})[color] = {'surfer_id': surfer_id, 'from_heat_id': advancing_from_heat_id, 'place': place, 'color': color}
        return

    def get_advancing_surfers(self, heat_id):
        return self.advancing_surfers.get(heat_id, {}).get('advancing_surfers', {})
