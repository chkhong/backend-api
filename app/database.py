from loguru import logger
import traceback
import pymysql
import os
from dotenv import load_dotenv
from typing import List, Union
import utils.DataTools as dt 
import re
import unittest

class Database:
  def __init__(self, host: str='', user: str='', password: str='', name: str=''):
    logger.debug('Initializing Database class...')
    load_dotenv()
    self.db_host = host or os.getenv('DB_HOST')
    self.db_user = user or os.getenv('DB_USER')
    self.db_password = password or os.getenv('DB_PASSWORD')
    self.db_name = name or os.getenv('DB_DATABASE')
    self.connection = None
    self.cursor = None
    self.statement_builder = StatementBuilder()

  def __connect(self) -> pymysql.Connection:
    ''' Make connection with the database

      Returns:
        connected cursor object
    '''
    try:
      logger.debug('Initializing connection to database...')
      logger.debug(f'Credentials: Host: {self.db_host}, Username: {self.db_user}, Password: {"********"}, Database Name: {self.db_name}')
      self.connection = pymysql.connect(host=self.db_host, user=self.db_user, password=self.db_password, database=self.db_name, cursorclass=pymysql.cursors.DictCursor)
      self.cursor = self.connection.cursor()
      logger.debug('Connection success!')
    except Exception as e:
      logger.error(e)
      logger.error(traceback.format_exc())
    finally:
      return self.connection

  def __disconnect(self):
    ''' Disconnect database object
    '''
    self.connection.close()
    logger.debug('Disconnect success!')

  def insert(self, table: str, columns: Union[List[str], str]=None, values: Union[List[str],str]=None, columns_values: dict={}) -> dict:
    ''' INSERT SQL statement
  
      Args:
        table: targeted table to interact with
        columns: columns of values to be created
        values: new values
        columns_values: dictionary of columns and values (support single insertion only)
      Returns:
        response: dict, (success, message, data, rows_affected, last_insert_id)
    '''

    response = {'success': False, 'message': '', 'data': [], 'rows_affected': 0, 'last_insert_id': 0}

    try:
      self.__connect()
      sql = self.statement_builder.build_statement(crud_mode="INSERT",table=table, columns=columns, values=values, columns_values=columns_values)
      response['rows_affected'] = self.cursor.execute(sql)
      if response['rows_affected']:
        response['last_insert_id'] = self.cursor.lastrowid
        response['success'] = True
        self.connection.commit()
      else:
        response['message'] = f'Insert failed! Please check log...'
        response['success'] = False
        self.connection.rollback()
      self.__disconnect()
    except Exception as e:
      logger.error(e)
      logger.error(traceback.format_exc())
      self.connection.rollback()
    finally:
      return response

  def select(self, table: Union[List[str], str], join: str='', join_condition: str='', columns: Union[List[str], str]=None, conditions: Union[dict, str]=None, offset: int=0, limit: int=0) -> dict:
    ''' SELECT SQL statement
  
      Args:
        table: targeted table(s) to interact with
        columns: columns to be selected
        join: ('INNER JOIN', 'LEFT JOIN', 'RIGHT JOIN', 'CROSS JOIN')
        join_condition: columns to be evaluated for joining
        conditions: to find rows with values matching the given conditions
        offset: select returned rows starting from n
        limit: 0 is search all, 1-n is find n number of matching rows
      Returns:
        response: dict, including success, data, rows_affected
    '''

    response = {'success': False, 'message': '', 'data': [], 'rows_affected': 0}

    try:
      self.__connect()
      sql = self.statement_builder.build_statement(crud_mode="SELECT",table=table, columns=columns, join=join, join_condition=join_condition, conditions=conditions, offset=offset, limit=limit)
      self.cursor.execute(sql)
      response['rows_affected'] = self.cursor.rowcount
      if response['rows_affected']:
        response['data'] = self.cursor.fetchall()
      else:
        response['message'] = f'Select execution success, however nothing is matched...'
      response['success'] = True
      self.__disconnect()
    except Exception as e:
      logger.error(e)
      logger.error(traceback.format_exc())
    finally:
      return response

  def update(self, table: str, conditions: Union[dict, str]=None, columns: Union[List[str], str]=None, values: Union[List[str],str]=None, columns_values: dict={}) -> dict:
    ''' UPDATE SQL statement
  
      Args:
        table: targeted table to interact with
        columns: columns of values to be modified
        values: new values
        columns_values: dictionary of columns and values
      Returns:
        response: dict, including success, data, rows_affected
    '''

    response = {'success': False,'message': '', 'data': [], 'rows_affected': 0}

    try:
      self.__connect()
      sql = self.statement_builder.build_statement(crud_mode="UPDATE",table=table, conditions=conditions, columns=columns, values=values, columns_values=columns_values)
      response['rows_affected'] = self.cursor.execute(sql)
      if not self.cursor.rowcount:
        response['success'] = False
        response['message'] = 'SQL did not update any rows'
      else:
        response['success'] = True
      self.connection.commit()
      self.__disconnect()
    except Exception as e:
      logger.error(e)
      logger.error(traceback.format_exc())
      self.connection.rollback()
    finally:
      return response

  def delete(self, table: str, conditions: Union[dict, str]=None) -> dict:
    ''' DELETE SQL statement
  
      Args:
        table: targeted table to interact with
      Returns:
        response: dict, including success, data, rows_affected
    '''

    response = {'success': False, 'data': [], 'rows_affected': 0}

    try:
      self.__connect()
      sql = self.statement_builder.build_statement(crud_mode="DELETE",table=table, conditions=conditions)
      response['rows_affected'] = self.cursor.execute(sql)
      response['success'] = True
      self.connection.commit()
      self.__disconnect()
    except Exception as e:
      logger.error(e)
      logger.error(traceback.format_exc())
      self.connection.rollback()
    finally:
      return response

  def execute(self, sql:str, args:list = []) -> dict:
    ''' Execute given sql statement (INSERT, UPDATE, DELETE)
  
      Args:
        sql: the statement to be executed
        args: variable to append in sql statement
      Returns:
        response: dict, including success, data, rows_affected
    '''
    response = {'success': False, 'data': [], 'rows_affected': 0}
    try:
      logger.info(f'SQL statement: {sql},    args: {", ".join(map(str, args))}')
      self.__connect()
      self.cursor.execute(sql, args)
      response['rows_affected'] = self.cursor.rowcount
      response['success'] = True
      self.connection.commit()
      self.__disconnect() 
    except Exception as e:
      logger.error(e)
      logger.error(traceback.format_exc())
    finally:
      return response

  def retrieve(self, sql:str, args:list = []) -> dict:
    ''' Retrieve data given sql statement (SELECT)
  
      Args:
        sql: the statement to be executed
        args: variable to append in sql statement
      Returns:
        response: dict, including success, data, rows_affected
    '''
    response = {'success': False, 'data': [], 'rows_affected': 0}
    try:
      logger.info(f'SQL statement: {sql},    args: {", ".join(map(str, args))}')
      self.__connect()
      self.cursor.execute(sql, args)
      response['rows_affected'] = self.cursor.rowcount
      if response['rows_affected']:
        response['data'] = self.cursor.fetchall()
      else:
        response['message'] = f'Select execution success, however nothing is matched...'
      response['success'] = True
      self.__disconnect()
    except Exception as e:
      logger.error(e)
      logger.error(traceback.format_exc())
    finally:
      return response


class StatementBuilder():
  def build_statement(self, crud_mode: str, table: str, conditions: Union[dict, str]=None, columns: Union[List[str], str]=None, join: str='', join_condition: str='', values: Union[List[str],str]=None, columns_values: dict={}, offset: int=0, limit: int=0) -> str:
    ''' Function description
  
      Args:
        crud_mode: the purpose of the sql statement, eg. INSERT, SELECT, UPDATE, DELETE
        table: table to be queried
        condition: conditions of the rows this sql statement will match/find
        columns: columns of values to be selected/created/modified, (SELECT, INSERT, UPDATE)
        join: ('INNER JOIN', 'LEFT JOIN', 'RIGHT JOIN', 'CROSS JOIN')
        join_condition: columns to be evaluated for joining
        values: new values for (INSERT, UPDATE)
        columns_values: list of dictionary of columns and values for single INSERT, UPDATE
        offset: select returned rows starting from n
        limit: 0 is search all, 1-n is find n number of matching rows
      Returns:
        sql_statement: str, a valid sql statement
      
      Examples:
        condition: 
          dict: {'id': 1, 'name': 'your name'} *operator is = for all
          str: "id=1, name='your name', price <= 60"
        columns: 
          list: ['id', 'name', 'datetime']
          str: "id, name, datetime"
        join:
          str: 'INNER JOIN', 'LEFT JOIN', 'RIGHT JOIN', 'CROSS JOIN'
        join_condition:
          str: 'table_a.id = table_b.id'
        values: 
          list: ['1', 'chuhenn', 'now()']
          str: "1, your name, now()"
    '''

    # general parameters validation
    if crud_mode not in ['INSERT', 'SELECT', 'UPDATE', 'DELETE']:
      raise Exception(f'Error: crud_mode not supported, supported methods: INSERT, SELECT, UPDATE, DELETE')
    if not table:
      raise Exception(f'Error: no table is specified')

    cond = ''
    cols = ''
    vals = ''
    sql_statement = ''

    logger.info('-'*100)
    logger.info('SQL Statement Builder Running...')

    # insert statement
    if crud_mode == 'INSERT':
      if columns_values:
        columns, values = dt.dict_to_two_list(columns_values)
      if columns:
        cols = self.__build_columns(columns)
      else:
        raise Exception(f'Error: columns are expected')
      if values:
        if not isinstance(values[0], list):
          vals = self.__build_values(values)
        else:
          vals = self.__build_values_batch(values)
      else:
        raise Exception(f'Error: values are expected')
      sql_statement = f'INSERT INTO {table} ({cols}) VALUES ({vals})'

    # select statement
    elif crud_mode == 'SELECT':
      if isinstance(table, str):
        table = [table]
      if len(table) == 2:
        if join:
          join = join.upper()
          if join not in ['INNER JOIN', 'LEFT JOIN', 'RIGHT JOIN', 'CROSS JOIN']:
            raise Exception(f'Error: join method not supported')
          if not join_condition:
            raise Exception(f'Error: join condition is expected for table join')
        else:
          raise Exception(f'Error: join method and condition are required for multiple tables')
      if columns:
        cols = self.__build_columns(columns)
      else:
        cols = '*'
      if conditions:
        cond = self.__build_conditions(conditions)
      
      sql_statement = f'SELECT {cols} FROM {table[0]}'
      sql_statement += f' {join} {table[1]} ON {join_condition}' if join else f''
      sql_statement += f' WHERE {cond}' if cond else f''
      sql_statement += f' LIMIT {limit}' if limit > 0 else f''
      sql_statement += f' OFFSET {offset}' if offset > 0 else f''
      
    # update statement
    elif crud_mode == 'UPDATE':
      if columns_values:
        columns, values = dt.dict_to_two_list(columns_values)
      if columns:
        cols = self.__build_columns(columns, return_list=True)
      else:
        raise Exception(f'Error: columns are expected')
      if values:
        vals = self.__build_values(values, return_list=True)
      else:
        raise Exception(f'Error: values are expected')
      if conditions:
        cond = self.__build_conditions(conditions)
      
      to_add = []
      for i in range(0, len(cols)):
        if vals[i] == 'now()':
          to_add.append(f"`{cols[i]}`={vals[i]}")
        else:
          to_add.append(f"`{cols[i]}`='{vals[i]}'")
      cols_vals = ', '.join(to_add)  

      sql_statement = f'UPDATE {table} SET {cols_vals}'
      sql_statement += f' WHERE {cond}' if cond else f''

    # delete statement
    else:
      if conditions:
        cond = self.__build_conditions(conditions)
      
      sql_statement = f'DELETE FROM {table} WHERE {cond}'

    # print statement
    logger.info(f'SQL statement: {sql_statement}')
    logger.info('-'*100)
    return sql_statement


  def __build_conditions(self, conditions: Union[str, dict]):
    ''' Concatenate conditions

      Example:
        'id=1, name=chuhenn' --> `id`='1' AND `name`='chu henn'
        {'id': '1', 'name': 'chuhenn'} --> `id`='1' AND `name`='chu henn'
        
    '''
    # logger.debug('Building conditions...')
    cond = ''
    temp_conditions = []
    to_add = []

    if type(conditions) is str:
      temp_operators = re.findall('>=|<=|!=|=|<|>', conditions)
      logger.debug(temp_operators)
      temp_conditions = re.split('>=|<=|!=|=|<|>|,', conditions)
      logger.debug(temp_conditions)
      temp_conditions = [re.sub('[\'\"\`]','',temp.strip()) for temp in temp_conditions]
      for i in range(0, len(temp_conditions), 2):
        if temp_conditions[i+1] == 'now()':
          to_add.append(f"`{temp_conditions[i]}`{temp_operators.pop(0)}{temp_conditions[i+1]}")
        else:
          to_add.append(f"`{temp_conditions[i]}`{temp_operators.pop(0)}'{temp_conditions[i+1]}'")
    elif type(conditions) is dict:
      for k, v in conditions.items():
        to_add.append(f"`{k}`='{v}'")
    cond = ' AND '.join(to_add)
    # logger.debug(f'conditions: {cond}')
    return cond
  
  def __build_columns(self, columns: Union[List[str],str], return_list: bool=False) -> str:
    ''' Concatenate columns
      
      Example:
        'id, name, datetime' --> `id`, `name`, `datetime`
        ['id', 'name', 'datetime'] --> `id`, `name`, `datetime`
    '''
    # logger.debug('Building columns...')
    temp_columns = []
    cols = ''
    to_add = []

    if type(columns) is list:
      temp_columns = [column.strip() for column in columns]
    elif type(columns) is str:
      columns = columns.replace(' ','')
      temp_columns = columns.split(',')
    else:
      raise Exception('Error: invalid columns input format. Accept list or string only')
    if return_list:
      return temp_columns  
    for temp in temp_columns:
      to_add.append(f'`{temp}`')
    cols = ', '.join(to_add)
    # logger.debug(f'columns: {cols}')
    return cols

  def __build_values(self, values: Union[List[str],str], return_list: bool=False) -> str:
    ''' Concatenate values
      
      Example:
        'id, name,      datetime    ' --> 'id', 'name', 'datetime' if return_list False
        ['id', 'name', 'datetime'] --> same if return_list True
    '''
    # logger.debug('Building values...')
    temp_values = []
    vals = ''
    to_add = []

    if type(values) is list:
      temp_values = [str(value).strip() for value in values ]
    elif type(values) is str:
      values = values.replace(' ','')
      temp_values = values.split(',')
    else:
      raise Exception('Error: invalid values input format. Accept list or string only') 
    if return_list:
      return temp_values
    for temp in temp_values:
      if temp == 'now()':
        to_add.append(f"{temp}")
      else:
        to_add.append(f"'{temp}'")
    vals = ', '.join(to_add)
    # logger.debug(f'values: {vals}')
    return vals

  def __build_values_batch(self, values: list) -> str:
    ''' Concetenate values (batch INSERT mode)
  
        Example:
          ['id', 'name', 'datetime'] --> same if return_list True
    '''
    # logger.debug('Building values_batch...')
    vals = ''
    to_add = []
    for value in values:
      to_add.append(self.__build_values(value))
      logger.debug(to_add)
    vals = '), ('.join(to_add)
    # logger.debug(f'batch_values: {vals}')
    return vals
      
      

class TestDatabase(unittest.TestCase):
  def setUp(self):
    self.statement_builder = StatementBuilder()

  def tearDown(self):
    pass

  def test_build_insert_statement(self):
    self.assertEqual(self.statement_builder.build_statement(crud_mode='INSERT',table='test', conditions={'id': '1', 'name': 'chu henn'}, columns=['id', 'name', 'datetime'], values="1, henn, now()"), "INSERT INTO test (`id`, `name`, `datetime`) VALUES ('1', 'henn', now())")
    self.assertEqual(self.statement_builder.build_statement(crud_mode='INSERT',table='test', conditions={'id': '1', 'name': 'chu henn'}, columns_values={'id': '1', 'name': 'henn', 'datetime': 'now()'}), "INSERT INTO test (`id`, `name`, `datetime`) VALUES ('1', 'henn', now())")
    self.assertEqual(self.statement_builder.build_statement(crud_mode='INSERT',table='test', conditions={'id': '1', 'name': 'chu henn'}, columns='id, name, datetime', values=['1','henn','now()']), "INSERT INTO test (`id`, `name`, `datetime`) VALUES ('1', 'henn', now())")
    self.assertEqual(self.statement_builder.build_statement(crud_mode='INSERT',table='test', conditions={'id': '1', 'name': 'chu henn'}, columns='id, name, datetime', values=[['1','henn','now()'],['2','test1','now()'],['3','test 2','now()']]), "INSERT INTO test (`id`, `name`, `datetime`) VALUES ('1', 'henn', now()), ('2', 'test1', now()), ('3', 'test 2', now())")
  
  def test_build_select_statement(self):
    self.assertEqual(self.statement_builder.build_statement(crud_mode='SELECT',table='test', conditions={'id': '1', 'name': 'chu henn'}, columns='id, name, datetime',values=['1','henn','now()']), "SELECT `id`, `name`, `datetime` FROM test WHERE `id`='1' AND `name`='chu henn'")
    self.assertEqual(self.statement_builder.build_statement(crud_mode='SELECT',table='test', conditions={}, columns=['id', 'name', 'datetime'], values=['1','henn','now()']), 'SELECT `id`, `name`, `datetime` FROM test')
    self.assertEqual(self.statement_builder.build_statement(crud_mode='SELECT',table='test', conditions='name="chu henn", id > 12, datetime <= now()', columns=['id', 'name', 'datetime'], values=['1','henn','now()']), "SELECT `id`, `name`, `datetime` FROM test WHERE `name`='chu henn' AND `id`>'12' AND `datetime`<=now()")
    self.assertEqual(self.statement_builder.build_statement(crud_mode='SELECT',table=['test', 'test2'], join='inner join', join_condition='test.id=test2.id', conditions={'test.id': 1, 'test2.name': 'chuuu'}),"SELECT * FROM test INNER JOIN test2 ON test.id=test2.id WHERE `test.id`='1' AND `test2.name`='chuuu'")
    self.assertEqual(self.statement_builder.build_statement(crud_mode='SELECT',table='test', conditions={'test.id': 1, 'test2.name': 'chuuu'}, limit=50, offset=5),"SELECT * FROM test WHERE `test.id`='1' AND `test2.name`='chuuu' LIMIT 50 OFFSET 5")
    
  def test_build_update_statement(self):
    self.assertEqual(self.statement_builder.build_statement(crud_mode='UPDATE',table='test', conditions={'id': '1', 'name': 'chu henn'}, columns=['id', 'name', 'datetime'], values=['1','henn','now()']), "UPDATE test SET `id`='1', `name`='henn', `datetime`=now() WHERE `id`='1' AND `name`='chu henn'")
    self.assertEqual(self.statement_builder.build_statement(crud_mode='UPDATE',table='test', conditions={'id': '1', 'name': 'chu henn'}, columns_values={'id': '1', 'name': 'henn', 'datetime': 'now()'}), "UPDATE test SET `id`='1', `name`='henn', `datetime`=now() WHERE `id`='1' AND `name`='chu henn'")

  def test_build_delete_statement(self):
    self.assertEqual(self.statement_builder.build_statement(crud_mode='DELETE',table='test', conditions={'id': '1', 'name': 'chu henn'}, columns=['id', 'name', 'datetime'], values=['1','henn','now()']), "DELETE FROM test WHERE `id`='1' AND `name`='chu henn'")

if __name__ == '__main__':
  unittest.main()
  # import utils.TimeExecution as te
  # db = Database()
  # te.time_exec(lambda: db.statement_builder.build_statement(crud_mode='UPDATE',table='test', conditions={'id': '1', 'name': 'chu henn'}, columns_values={'id': '1', 'name': 'henn', 'datetime': 'now()'}), seconds=10)
