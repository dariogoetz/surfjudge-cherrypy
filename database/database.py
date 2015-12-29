from config import Config #path relative to main path
from .sql_adapter import PythonSQLAdapter

from keys import *

from Queue import Queue
import multiprocessing, uuid, json, os

_CONFIG = Config(__name__)

class _DatabaseHandler(object):
    '''
    Handles the interface to the database (file, SQLite, mongodb, ...)
    '''

    def __init__(self):
        pass


    def insert_score(self, score):
        '''
        Push a score to the database
        '''
        pass

    def get_scores(self, query_info):
        '''
        Retrieve a score from the database
        '''
        pass

    def shutdown(self):
        '''
        Shutdown database
        '''
        pass


class SQLiteDatabaseHandler(_DatabaseHandler):
    '''
    SQLite implementation of the database hander
    '''

    def __init__(self, db_name = _CONFIG['sqlite_db']['default_name']):
        _DatabaseHandler.__init__(self)
        self._pysql_adapt = PythonSQLAdapter()

        self.__access_queue = Queue()
        self._db_name = db_name

        import threading
        self._thread = threading.Thread(target=self._run)
        self._thread.start()

        print 'database: Initializing ID pointers'
        tournaments = self.get_tournaments({})
        n_tournaments = max([t['id'] for t in tournaments]) + 1 if len(tournaments) > 0 else 0
        categories = self.get_categories({})
        n_categories = max([t['id'] for t in categories]) + 1 if len(categories) > 0 else 0
        heats = self.get_heats({})
        n_heats = max([t['id'] for t in heats]) + 1 if len(heats) > 0 else 0
        surfers = self.get_surfers({})
        n_surfers = max([t['id'] for t in surfers]) + 1 if len(surfers) > 0 else 0
        judges = self.get_judges({})
        n_judges = max([t['id'] for t in judges]) + 1 if len(judges) > 0 else 0

        self._db_info = {'n_tournaments': n_tournaments,
                         'n_categories': n_categories,
                         'n_heats': n_heats,
                         'n_surfers': n_surfers,
                         'n_judges': n_judges,}

        #self._db_info = self._read_db_info()

        return

    def _read_db_info(self):
        import os
        filename = _CONFIG['db_info']['filename']
        if os.path.isfile(filename):
            with open(filename, 'rb') as fp:
                res = json.load(fp)
        else:
            res = {}
        return res




    ############ scores interface ##############
    def insert_score(self, score):
        pipe_recv, pipe_send = multiprocessing.Pipe(False)
        self.__access_queue.put( (self._insert_score, score, pipe_send), block=True)
        res = pipe_recv.recv()
        return res


    def get_scores(self, query_info):
        pipe_recv, pipe_send = multiprocessing.Pipe(False)
        self.__access_queue.put( (self._get_scores, query_info, pipe_send), block=True)
        res = pipe_recv.recv()
        return res

    def delete_score(self, score):
        pipe_recv, pipe_send = multiprocessing.Pipe(False)
        self.__access_queue.put( (self._delete_score, score, pipe_send), block=True)
        res = pipe_recv.recv()
        return res



    ############ tournaments interface ##############
    def get_tournaments(self, query_info):
        pipe_recv, pipe_send = multiprocessing.Pipe(False)
        self.__access_queue.put( (self._get_tournaments, query_info, pipe_send), block=True)
        res = pipe_recv.recv()
        return res

    def insert_tournament(self, tournament):
        pipe_recv, pipe_send = multiprocessing.Pipe(False)
        self.__access_queue.put( (self._insert_tournament, tournament, pipe_send), block=True)
        res = pipe_recv.recv()
        return res

    def delete_tournament(self, tournament):
        pipe_recv, pipe_send = multiprocessing.Pipe(False)
        self.__access_queue.put( (self._delete_tournament, tournament, pipe_send), block=True)
        res = pipe_recv.recv()
        return res


    ########### categories interface ##############
    def get_categories(self, query_info):
        pipe_recv, pipe_send = multiprocessing.Pipe(False)
        self.__access_queue.put( (self._get_categories, query_info, pipe_send), block=True)
        res = pipe_recv.recv()
        return res

    def insert_category(self, category):
        pipe_recv, pipe_send = multiprocessing.Pipe(False)
        self.__access_queue.put( (self._insert_category, category, pipe_send), block=True)
        res = pipe_recv.recv()
        return res

    def delete_category(self, category):
        pipe_recv, pipe_send = multiprocessing.Pipe(False)
        self.__access_queue.put( (self._delete_category, category, pipe_send), block=True)
        res = pipe_recv.recv()
        return res

    ############ heats interface ##############
    def get_heats(self, query_info):
        pipe_recv, pipe_send = multiprocessing.Pipe(False)
        self.__access_queue.put( (self._get_heats, query_info, pipe_send), block=True)
        res = pipe_recv.recv()
        return res

    def insert_heat(self, heat):
        pipe_recv, pipe_send = multiprocessing.Pipe(False)
        self.__access_queue.put( (self._insert_heat, heat, pipe_send), block=True)
        res = pipe_recv.recv()
        return res

    def delete_heat(self, heat):
        pipe_recv, pipe_send = multiprocessing.Pipe(False)
        self.__access_queue.put( (self._delete_heat, heat, pipe_send), block=True)
        res = pipe_recv.recv()
        return res


    ############ judge interface ##############

    def get_judge_id_for_username(self, username):
        pipe_recv, pipe_send = multiprocessing.Pipe(False)
        self.__access_queue.put( (self._get_judge_id, username, pipe_send), block=True )
        res = pipe_recv.recv()
        return res

    def get_judges(self, query_info):
        pipe_recv, pipe_send = multiprocessing.Pipe(False)
        self.__access_queue.put( (self._get_judges, query_info, pipe_send), block=True )
        res = pipe_recv.recv()
        return res

    def insert_judge(self, judge):
        pipe_recv, pipe_send = multiprocessing.Pipe(False)
        self.__access_queue.put( (self._insert_judge, judge, pipe_send), block=True)
        res = pipe_recv.recv()
        return res

    def delete_judge(self, judge):
        pipe_recv, pipe_send = multiprocessing.Pipe(False)
        self.__access_queue.put( (self._delete_judge, judge, pipe_send), block=True)
        res = pipe_recv.recv()
        return res

    ############ surfers interface ##############
    def get_surfers(self, query_info):
        pipe_recv, pipe_send = multiprocessing.Pipe(False)
        self.__access_queue.put( (self._get_surfers, query_info, pipe_send), block=True )
        res = pipe_recv.recv()
        return res

    def insert_surfer(self, surfer):
        pipe_recv, pipe_send = multiprocessing.Pipe(False)
        self.__access_queue.put( (self._insert_surfer, surfer, pipe_send), block=True)
        res = pipe_recv.recv()
        return res

    def delete_surfer(self, surfer):
        pipe_recv, pipe_send = multiprocessing.Pipe(False)
        self.__access_queue.put( (self._delete_surfer, surfer, pipe_send), block=True)
        res = pipe_recv.recv()
        return res


    def get_participants(self, heat_id):
        pipe_recv, pipe_send = multiprocessing.Pipe(False)
        self.__access_queue.put( (self._get_participants, heat_id, pipe_send), block=True)
        res = pipe_recv.recv()
        return res

    def set_participants(self, data):
        pipe_recv, pipe_send = multiprocessing.Pipe(False)
        self.__access_queue.put( (self._set_participants, data, pipe_send), block=True)
        res = pipe_recv.recv()
        return res


    ############ joins #################
    def get_judge_activities(self, query_info):
        pipe_recv, pipe_send = multiprocessing.Pipe(False)
        self.__access_queue.put( (self._get_judge_activities, query_info, pipe_send), block=True )
        res = pipe_recv.recv()
        return res


    def set_judge_activities(self, data):
        pipe_recv, pipe_send = multiprocessing.Pipe(False)
        self.__access_queue.put( (self._set_judge_activities, data, pipe_send), block=True )
        res = pipe_recv.recv()
        return res

    def get_judges_for_heat(self, heat_id):
        pipe_recv, pipe_send = multiprocessing.Pipe(False)
        self.__access_queue.put( (self._get_judges_for_heat, heat_id, pipe_send), block=True )
        res = pipe_recv.recv()
        return res

    def get_heat_info(self, query_info):
        pipe_recv, pipe_send = multiprocessing.Pipe(False)
        self.__access_queue.put( (self._get_heat_info, query_info, pipe_send), block=True )
        res = pipe_recv.recv()
        return res


    def get_results(self, query_info):
        pipe_recv, pipe_send = multiprocessing.Pipe(False)
        self.__access_queue.put( (self._get_results, query_info, pipe_send), block=True )
        res = pipe_recv.recv()
        return res

    def insert_result(self, result):
        pipe_recv, pipe_send = multiprocessing.Pipe(False)
        self.__access_queue.put( (self._insert_result, result, pipe_send), block=True )
        res = pipe_recv.recv()
        return res

    def delete_result(self, query_info):
        pipe_recv, pipe_send = multiprocessing.Pipe(False)
        self.__access_queue.put( (self._delete_result, query_info, pipe_send), block=True )
        res = pipe_recv.recv()
        return res

    ############ db admin interface ##############
    def shutdown(self):
        if not self._thread.isAlive():
            return
        print 'Stopping database thread'
        self.__access_queue.put( (KEY_SHUTDOWN, None, None), block=True)
        return


    def _init_db(self):
        self._db = self._connect_db(self._db_name)
        self._initialize_tables()
        self._table_info = self._get_tables_info()
        return


    def _run(self):
        self._init_db()
        print 'Starting database'
        while True:
            #print 'waiting for db commands'
            task_processor, data, pipe_conn = self.__access_queue.get()
            #print '***** DB task {} (remaining {}) *****'.format(data, self.__access_queue.qsize())
            if task_processor == KEY_SHUTDOWN:
                self.__access_queue.task_done()
                self._db.close()
                break

            res = task_processor(data)
            pipe_conn.send(res)
            pipe_conn.close()
            #print '***** DB done task (remaining {}) *****'.format(self.__access_queue.qsize())
            self.__access_queue.task_done()


    def _get_scores(self, query_info, cols = None):
        res = self._query_db(query_info, 'scores', cols = cols)
        return res


    def _insert_score(self, score):
        query = {'wave': score['wave'], 'judge_id': score['judge_id'], 'heat_id': score['heat_id'], 'surfer_id': score['surfer_id']}
        if len(self._get_scores(query)) > 0:
            self._modify_in_db(query, score, 'scores')
        else:
            self._insert_into_db(score, 'scores')
        return

    def _delete_score(self, score):
        self._delete_from_db(score, 'scores')
        return


    def _get_tournaments(self, query_info, cols = None):
        # TODO: make a JOIN on categories, tournaments and events
        # --> get tournaments with a list of their categories and events
        return self._query_db(query_info, 'tournaments', cols = cols)


    def _insert_tournament(self, tournament):
        if 'id' not in tournament or tournament['id'] is None:
            # generate new id
            n_tournaments = self._db_info.setdefault('n_tournaments', 0)
            tournament['id'] = n_tournaments
            self._db_info['n_tournaments'] += 1
        # check if id exists
        if len(self._get_tournaments({'id': tournament.get('id')})) > 0:
            self._modify_in_db({'id': tournament.get('id')}, tournament, 'tournaments')
        else:
            self._insert_into_db(tournament, 'tournaments')
        return tournament['id']

    def _delete_tournament(self, tournament):
        self._delete_from_db(tournament, 'tournaments')
        self._delete_from_db({'tournament_id': tournament['id']}, 'categories')
        return


    def _get_categories(self, query_info, cols=None):
        return self._query_db(query_info, 'categories', cols = cols)

    def _insert_category(self, category):
        if 'id' not in category or category['id'] is None:
            # generate new id
            n_categories = self._db_info.setdefault('n_categories', 0)
            category['id'] = n_categories
            self._db_info['n_categories'] += 1
        # check if id exists
        if len(self._get_categories({'id': category.get('id')})) > 0:
            self._modify_in_db({'id': category.get('id')}, category, 'categories')
        else:
            self._insert_into_db(category, 'categories')
        return category['id']

    def _delete_category(self, category):
        self._delete_from_db(category, 'categories')
        self._delete_from_db({'category_id': category['id']}, 'heats')
        return


    def _get_heats(self, query_info, cols = None):
        return self._query_db(query_info, 'heats', cols = cols)

    def _delete_heat(self, data):
        self._delete_from_db(data, 'heats')
        self._delete_from_db({'heat_id': data['id']}, 'participants')
        self._delete_from_db({'heat_id': data['id']}, 'judge_activities')
        self._delete_from_db({'heat_id': data['id']}, 'scores')
        return

    def _insert_heat(self, heat):
        if 'id' not in heat or heat['id'] is None:
            # generate new id
            n_heats = self._db_info.setdefault('n_heats', 0)
            heat['id'] = n_heats
            self._db_info['n_heats'] += 1
        # check if id exists
        if len(self._get_heats({'id': heat.get('id')})) > 0:
            self._modify_in_db({'id': heat.get('id')}, heat, 'heats')
        else:
            self._insert_into_db(heat, 'heats')
        return heat['id']



    def _get_judge_id(self, username):
        query_info = {'username': username}
        return self._query_db(query_info, 'judges', cols = ['id'])

    def _get_judges(self, query_info):
        return self._query_db(query_info, 'judges')

    def _insert_judge(self, judge):
        if 'id' not in judge or judge['id'] is None:
            # generate new id
            n_judges = self._db_info.setdefault('n_judges', 0)
            judge['id'] = n_judges
            self._db_info['n_judges'] += 1
        # check if id exists
        if len(self._get_judges({'username': judge.get('username')})) > 0:
            self._modify_in_db({'username': judge.get('username')}, judge, 'judges')
        else:
            self._insert_into_db(judge, 'judges')
        return judge['id']

    def _delete_judge(self, judge):
        self._delete_from_db(judge, 'judges')
        self._delete_from_db({'judge_id': judge['id']}, 'judge_activities')
        self._delete_from_db({'judge_id': judge['id']}, 'scores')
        return



    def _get_surfers(self, query_info):
        return self._query_db(query_info, 'surfers')

    def _insert_surfer(self, surfer):
        if 'id' not in surfer or surfer['id'] is None:
            #check if surfer already exists
            existing_surfers = self._get_surfers({'first_name': surfer.get('first_name', ''), 'last_name': surfer.get('last_name', '')})
            if len(existing_surfers) > 0:
                print 'database: Surfer "{} {}" already exists!'.format(surfer.get('first_name', ''), surfer.get('last_name', ''))
                surfer['id'] = existing_surfers[0].get('id')
            else:
                # generate new id
                n_surfers = self._db_info.setdefault('n_surfers', 0)
                surfer['id'] = n_surfers
                self._db_info['n_surfers'] += 1

        # check if id exists
        if len(self._get_surfers({'id': surfer.get('id')})) > 0:
            self._modify_in_db({'id': surfer.get('id')}, surfer, 'surfers')
        else:
            self._insert_into_db(surfer, 'surfers')
        return surfer['id']

    def _delete_surfer(self, surfer):
        self._delete_from_db(surfer, 'surfers')
        self._delete_from_db({'surfer_id': surfer['id']}, 'participants')
        self._delete_from_db({'surfer_id': surfer['id']}, 'scores')
        return


    def _get_participants(self, heat_id):
        query_info = {'participants': {'heat_id': heat_id}}
        cols = ['participants.heat_id AS heat_id',
                'participants.surfer_color AS surfer_color',
                'participants.surfer_id AS surfer_id',
                'surfers.first_name AS first_name',
                'surfers.last_name AS last_name',
                'surfers.name AS name',
                'surfers.country AS country',
                'surfers.additional_info AS additional_info']
        return self._query_join(query_info, 'participants', 'surfer_id', 'id', 'surfers', cols=cols)
        #return self._query_db(query_info, 'participants')

    def _set_participants(self, data):
        heat_id = data['heat_id']
        surfers = data['surfers']
        if len(self._get_participants(heat_id)) > 0:
            self._delete_from_db({'heat_id': heat_id}, 'participants')
        for (surfer_id, surfer_color) in surfers:
            self._insert_into_db({'heat_id': heat_id, 'surfer_id': surfer_id, 'surfer_color': surfer_color}, 'participants')
        return



    def _get_judge_activities(self, query_info):
        cols = ['judges.id AS judge_id',
                'judges.first_name AS judge_first_name',
                'judges.last_name AS judge_last_name',
                'judges.username AS judge_username',
                'judges.additional_info AS judge_additional_info',
                'heats.id AS heat_id',
                'heats.name AS heat_name',
                'heats.additional_info AS heat_additional_info']
        return self._query_join(query_info, 'judges', 'id', 'judge_id', 'judge_activities', 'heat_id', 'id', 'heats', cols=cols)

    def _set_judge_activities(self, data):
        heat_id = data['heat_id']
        judges = data['judges']
        if len(self._get_judge_activities({'heat_id': heat_id})) > 0:
            self._delete_from_db({'heat_id': heat_id}, 'judge_activities')
        for judge_id in judges:
            self._insert_into_db({'heat_id': heat_id, 'judge_id': judge_id}, 'judge_activities')
        return



    def _get_judges_for_heat(self, heat_id):
        query_info = {'judge_activities': {'heat_id': heat_id}}
        return self._query_join(query_info, 'judges', 'id', 'judge_id', 'judge_activities')


    def _get_heat_info(self, query_info):
        qinfo = {}
        if query_info.get('heat_id') is not None:
            qinfo['heats'] = {'id': query_info['heat_id']}
        if query_info.get('category_id') is not None:
            qinfo['categories'] = {'id': query_info['category_id']}
        if query_info.get('tournament_id') is not None:
            qinfo['tournaments'] = {'id': query_info['tournament_id']}

        cols = ['heats.id AS heat_id',
                'heats.name AS heat_name',
                'heats.start_datetime AS heat_start_datetime',
                'heats.number_of_waves AS number_of_waves',
                'heats.additional_info AS heat_additional_info',
                'categories.id AS category_id',
                'categories.name AS category_name',
                'categories.additional_info AS categories_additional_info',
                'tournaments.id AS tournament_id',
                'tournaments.name AS tournament_name',
                'tournaments.start_datetime AS tournament_start_datetime',
                'tournaments.end_datetime AS tournament_end_datetime',
                'tournaments.additional_info AS tournament_additional_info']
        return self._query_join(qinfo, 'tournaments', 'id', 'tournament_id', 'categories', 'id',  'category_id','heats', cols=cols)



    def _get_results(self, query_info):
        return self._query_db(query_info, 'results')

    def _insert_result(self, result):
        if not isinstance(result.setdefault('wave_scores', '[]'), basestring):
            result['wave_scores'] = json.dumps(result['wave_scores'])

        query = {'heat_id': result['heat_id'], 'surfer_id': result['surfer_id']}
        if len(self._get_results(query)) > 0:
            self._modify_in_db(query, result, 'results')
        else:
            self._insert_into_db(result, 'results')
        return

    def _delete_result(self, query_info):
        self._delete_from_db(query_info, 'results')
        return


    def _register_converter_adapter(self, sql):
        for t, adapter in self._pysql_adapt.adapter.items():
            sql.register_adapter(t, adapter)
        for sql_type, converter in self._pysql_adapt.converter.items():
            sql.register_converter(sql_type, converter)
        return


    def _connect_db(self, db_name, row_factory = None):
        import sqlite3 as sql
        self._register_converter_adapter(sql)
        try:
            con = sql.connect(db_name, detect_types=sql.PARSE_DECLTYPES)
        except sql.Error as e:
            print('Error {}'.format(e.args[0]))
            return None


        if row_factory is None:
            def dict_factory(cursor, row):
                return dict(sql.Row(cursor, row))
            con.row_factory = dict_factory
        else:
            con.row_factory = row_factory
        return con


    def _cols_str(self, table, col_names):
        cols = ['{}.{}'.format(table, c) for c in col_names]
        cols_str = ', '.join(cols)
        return cols_str


    def _where_str(self, table, col_names, val_dict):
        conditions = ['{}.{} = "{}"'.format(table, c, val_dict[c]) for c in col_names]
        where_str = ' AND '.join(conditions)
        return where_str


    def _update_str(self, table, col_names, val_dict):
        updates = ['{} = "{}"'.format(c, val_dict[c]) for c in col_names]
        update_str = ', '.join(updates)
        return update_str


    def _query_db(self, query_info, target_table, cols = None):
        print '** DB ** querying "{}" from "{}"'.format(query_info, target_table)

        if cols is None:
            cols_str = '*'
        else:
            return_cols = cols
            cols_str = self._cols_str(target_table, return_cols)

        tables_str = target_table

        col_info = self._table_info.get(target_table, {})
        common_cols = set(query_info.keys()).intersection(set(col_info.keys()))
        where_str = self._where_str(target_table, common_cols, query_info)

        sql_command = 'SELECT {cols} FROM {tables}'.format(cols = cols_str, tables = tables_str)
        if len(where_str) > 0:
            sql_command += ' WHERE {cond}'.format(cond = where_str)

        cursor = self._db.cursor()
        try:
            res = [x for x in cursor.execute(sql_command)]
        except Exception as e:
            print 'Error executing sql command "{}": {}'.format(sql_command, e)
            res = []
        return res



    # TODO: put table name in query_info
    def _query_join(self, query_info, *args, **kwargs):
        print '** DB ** querying "{}" from join of multiple tables'.format(query_info)

        join_type = kwargs.get('join_type', 'INNER JOIN')

        if len(args) % 3 != 1:
            print 'Wrong number of arguments for multiple db join: {}, {}, {}'.format(query_info, cols, args)
            return []


        table = args[0]
        qinfo = query_info.get(table, {})
        col_info = self._table_info.get(table, {})
        common_cols = set(qinfo.keys()).intersection(set(col_info.keys()))
        where_str = self._where_str(table, common_cols, qinfo)


        tables = [table]
        join_keys = []
        common_cols_list = [common_cols]
        where_str_list = [where_str]
        for i in range(len(args)/3):
            table = args[3*i+3]
            join_key1 = args[3*i+1]
            join_key2 = args[3*i+2]
            tables.append(table)
            join_keys.extend([join_key1, join_key2])
            qinfo = query_info.get(table, {})
            col_info = self._table_info.get(table, {})
            common_cols = set(qinfo.keys()).intersection(set(col_info.keys()))
            common_cols_list.append(common_cols)
            where_str_list.append(self._where_str(table, common_cols, qinfo))

        join_cols = set.union(*common_cols_list)
        if kwargs.get('cols') is None:
            cols_str = '*'
        else:
            cols_str = ", ".join(kwargs['cols'])

        old_table = tables[0]
        join_str = str(old_table)
        for idx, table in enumerate(tables[1:]):
            join_str += \
"""
    {join_type} {table}
        ON {old_table}.{key1} = {table}.{key2}""".format(join_type = join_type, old_table = old_table, table = table, key1 = join_keys[2*idx], key2 = join_keys[2*idx+1], join_str = join_str)
            old_table = table

        sql_command = \
"""SELECT {cols}
FROM {joins}
""".format(cols = cols_str, joins = join_str)
        where_conditions = []
        for where_str in where_str_list:
            if len(where_str) > 0:
                where_conditions.append(where_str)

        where_str = ' AND '.join(where_conditions)
        if len(where_str) > 0:
            sql_command += ' WHERE {cond}'.format(cond = where_str)

        cursor = self._db.cursor()
        try:
            res = [x for x in cursor.execute(sql_command)]
        except Exception as e:
            print 'Error executing sql command "{}": {}'.format(sql_command, e)
            res = []

#        print '*********************************'
#        print '*******SQL COMMAND: ', sql_command
#        print '*******RESULT     : ', res
#        print '*********************************'
        return res


    def _modify_in_db(self, query_info, new_vals, target_table):
        print '** DB ** modifying "{}" from "{}"'.format(query_info, target_table)

        tables_str = target_table

        col_info = self._table_info.get(target_table,{})

        common_cols = set(query_info.keys()).intersection(set(col_info.keys()))
        where_str = self._where_str(target_table, common_cols, query_info)

        upd_cols = set(new_vals.keys()).intersection(set(col_info.keys()))
        upd_str = self._update_str(target_table, upd_cols, new_vals)

        sql_command = 'UPDATE {tables} SET {upd}'.format(tables = tables_str, upd=upd_str)
        if len(where_str) > 0:
            sql_command += ' WHERE {cond}'.format(cond = where_str)

        cursor = self._db.cursor()
        try:
            cursor.execute(sql_command)
        except Exception as e:
            print 'Error executing sql command "{}": {}'.format(sql_command, e)
        return



    def _delete_from_db(self, query_info, target_table):
        print '** DB ** deleting "{}" from "{}"'.format(query_info, target_table)

        tables_str = target_table

        col_info = self._table_info.get(target_table,{})
        common_cols = set(query_info.keys()).intersection(set(col_info.keys()))
        where_str = self._where_str(target_table, common_cols, query_info)

        sql_command = 'DELETE FROM {tables}'.format(tables = tables_str)
        if len(where_str) > 0:
            sql_command += ' WHERE {cond}'.format(cond = where_str)

        cursor = self._db.cursor()
        try:
            cursor.execute(sql_command)
        except Exception as e:
            print 'Error executing sql command "{}": {}'.format(sql_command, e)
        return



    def _insert_into_db(self, data, table):
        print '** DB ** inserting "{}" into "{}"'.format(data, table)
        col_info = self._table_info.get(table, {})
        values = []

        for col in sorted(col_info.values(), key = lambda val: val['cid']):
            values.append( data.get(col['name'], None) )

        cursor = self._db.cursor()
        values_str = ', '.join(['?']*len(values))

        sql_command = 'INSERT INTO {table} VALUES ({values})'.format(table = table, values = values_str)

        try:
            cursor.execute(sql_command, values)
        except Exception as e:
            print 'Error executing sql command: {}'.format(e)
        self._db.commit()
        return


    def _available_tables(self):
        cursor = self._db.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        table_data = cursor.fetchall()
        if len(table_data) == 0:
            return set()
        else:
            return set([table['name'] for table in table_data])


    def _get_table_column_info(self, table_name):
        cursor = self._db.cursor()
        cursor.execute('PRAGMA table_info({})'.format(table_name))
        table_data = cursor.fetchall()
        cols = [table['name'] for table in table_data]
        res = dict(zip(cols, table_data))
        for col in res:
            res[col]['python_type'] = _CONFIG['sqlite_db']['tables'].get(table_name, {}).get(col, 'unknown')
        return res


    def _get_tables_info(self):
        table_info = {}
        for table in self._available_tables():
            table_info[table] = self._get_table_column_info(table)
        return table_info


    def _columns_okay(self, intended_columns, table):
        is_okay = True
        col_info = self._get_table_column_info(table)
        for col_name, typ in intended_columns.items():
            if col_name not in col_info:
                print('Column {} not in table {}. Recreating the table!'.format(col_name, table))
                is_okay = False
            else:
                av_col_type = col_info[col_name]['type']
                intended_type = self._pysql_adapt.py2sql.get(typ, typ)
                if av_col_type != intended_type:
                    print('Column type "{}" in table "{}" does not match "{}".'.format(col_name, table, str(typ)))
                    is_okay = False
        return is_okay



    def _initialize_tables(self):
        intended_tables = _CONFIG['sqlite_db']['tables']
        available_tables = self._available_tables()

        for table, cols in intended_tables.items():
            recreate = False
            if table not in available_tables:
                recreate = True
            else:
                recreate = not self._columns_okay(cols, table)
            if recreate:
                #TODO: still gives error if table is already there
                fields = []
                for col_name, typ in cols.items():
                    fields.append( (col_name, typ) )

                self._create_table(table, fields)
        return


    def _create_table(self, name, fields):
        '''
        Creates a table in the database.

        Parameters:
          name   - name of the table
          fields - list of pairs (field name, field type)
        '''

        cols_str = ', '.join( [' '.join([field, self._pysql_adapt.py2sql.get(typ, typ)]) for field, typ in fields] )

        sql_command = 'CREATE TABLE {name} ({col_info})'.format(name=name, col_info = cols_str)

        print('Creating table "{}" with columns {}.'.format(name, cols_str))

        cursor = self._db.cursor()
        cursor.execute(sql_command)
        return
