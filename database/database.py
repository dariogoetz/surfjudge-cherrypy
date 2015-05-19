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

        self._db_info = self._read_db_info()

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

    def _write_db_info(self):
        filename = _CONFIG['db_info']['filename']
        with open(filename, 'wb') as fp:
            json.dump(self._db_info, fp)
        return



    ############ scores interface ##############
    def insert_score(self, score):
        pipe_recv, pipe_send = multiprocessing.Pipe(False)
        self.__access_queue.put( (self._insert_score, score, None), block=True)
        res = pipe_recv()
        return res


    def get_scores(self, query_info):
        pipe_recv, pipe_send = multiprocessing.Pipe(False)
        self.__access_queue.put( (self._get_scores, query_info, pipe_send), block=True)
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
        del_tournament = lambda data: self._delete_from_db(data, 'tournaments')
        self.__access_queue.put( (del_tournament, tournament, pipe_send), block=True)
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
        del_heat = lambda data: self._delete_from_db(data, 'heats')
        self.__access_queue.put( (del_heat, heat, pipe_send), block=True)
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

            if task_processor == KEY_SHUTDOWN:
                self.__access_queue.task_done()
                break

            res = task_processor(data)
            pipe_conn.send(res)
            pipe_conn.close()
            self.__access_queue.task_done()


    def _get_scores(self, query_info, cols = None):
        return self._query_db(query_info, 'scores', cols = cols)


    def _insert_score(self, score):
        self._insert_into_db(score, 'scores')
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
            self._write_db_info()
        # check if id exists
        if len(self._get_tournaments({'id': tournament.get('id')})) > 0:
            self._modify_in_db({'id': tournament.get('id')}, tournament, 'tournaments')
        else:
            self._insert_into_db(tournament, 'tournaments')
        return

    def _get_heats(self, query_info, cols = None):
        return self._query_db(query_info, 'heats', cols = cols)


    def _insert_heat(self, heat):
        if 'id' not in heat or heat['id'] is None:
            # generate new id
            n_heats = self._db_info.setdefault('n_heats', 0)
            heat['id'] = n_heats
            self._db_info['n_heats'] += 1
            self._write_db_info()
        # check if id exists
        if len(self._get_heats({'id': heat.get('id')})) > 0:
            self._modify_in_db({'id': heat.get('id')}, heat, 'heats')
        else:
            self._insert_into_db(heat, 'heats')
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
        where_str = 'AND '.join(conditions)
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

        col_info = self._table_info.get(target_table,{})
        common_cols = set(query_info.keys()).intersection(set(col_info.keys()))
        where_str = self._where_str(target_table, common_cols, query_info)

        sql_command = 'SELECT {cols} FROM {tables}'.format(cols = cols_str, tables = tables_str)
        if len(where_str) > 0:
            sql_command += ' WHERE {cond}'.format(cond = where_str)

        cursor = self._db.cursor()
        try:
            res = [x for x in cursor.execute(sql_command)]
        except Exception as e:
            print 'Error executing sql command: {}'.format(e)
            res = []
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
            print 'Error executing sql command: {}'.format(e)
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
            print 'Error executing sql command: {}'.format(e)
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
