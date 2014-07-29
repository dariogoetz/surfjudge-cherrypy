from config import Config #path relative to main path
from sql_adapter import PythonSQLAdapter


_CONFIG = Config(__name__)

class _DatabaseHandler(object):
    '''
    Handles the interface to the database (file, SQLite, mongodb, ...)
    '''

    def __init__(self):
        self.__db = None
        return

    def insert_score(self, score):
        '''
        Push a score to the database
        '''
        pass

    def get_scores(self, score):
        '''
        Retrieve a score from the database
        '''
        return


class SQLiteDatabaseHandler(_DatabaseHandler):
    '''
    SQLite implementation of the database hander
    '''

    def __init__(self, db_name = _CONFIG['sqlite_db']['default_name']):
        self._pysql_adapt = PythonSQLAdapter()

        self.__db = self._connect_db(db_name)
        self._initialize_tables()
        self._table_info = self._get_tables_info()
        return

    @property
    def _db(self):
        return self.__db

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
        except sql.Error, e:
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


    def get_scores(self, query_info, cols = None):
        target_table = 'scores'
        if cols is None:
            cols_str = '*'
        else:
            return_cols = cols
            cols_str = self._cols_str(target_table, return_cols)

        tables_str = target_table

        col_info = self._table_info.get(target_table,{})
        common_cols = set(query_info.keys()).intersection(set(col_info.keys()))
        where_str = self._where_str(target_table, common_cols, query_info)

        sql_command = 'SELECT {cols} FROM {tables} WHERE {cond}'.format(cols = cols_str, tables = tables_str, cond = where_str)
        cursor = self._db.cursor()
        return cursor.execute(sql_command)


    def insert_score(self, score):
        target_table = 'scores'
        col_info = self._table_info.get(target_table, {})
        vals = []

        for col in sorted(col_info.values(), key = lambda val: val['cid']):
            vals.append( score.get(col['name'], None) )
        self._insert_db(target_table, vals)
        return


    def _insert_db(self, table, values):
        cursor = self._db.cursor()
        values_str = ', '.join(['?']*len(values))

        sql_command = 'INSERT INTO {table} VALUES ({values})'.format(table = table, values = values_str)
        cursor.execute(sql_command, values)
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
