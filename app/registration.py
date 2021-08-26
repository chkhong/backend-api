from loguru import logger
import traceback

from database import Database
from utils.InputHandler import check_params
from utils.OutputHandler import std_response
from utils.Hash import hash

class Registration:
  def __init__(self, db: Database):
    logger.debug('Initializing Registration class...')
    self.db = db

  def __del__(self):
    pass

  def create_user(self, args: dict) -> dict:
    ''' Create new user

      Remarks:
        ^required
      Args:
        args: a dictionary contains (^username, ^password, ^email, first_name, last_name)
      Returns:
        response: dict, (success, message, data ...)
    '''
    logger.info('='*100)
    logger.info(f'create_user() running...')
    response = std_response()
    try:
      r = check_params(args, required=['username', 'password', 'email'])
      if r['success']:
        args['password'] = hash(args['password'])
        find = self.db.retrieve('SELECT * FROM users WHERE (username=%s OR email=%s) AND is_active=1', [args['username'], args['email']])
        if find['rows_affected']:
          response['message'] = 'Username or email already existed.'
        else:
          r = self.db.insert(table='users', columns_values=args)
          if r['success']:
            r['message'] = 'User has been created successfully.'
            response = r
      else:
        response = r
    except Exception as e:
      logger.error(e)
      logger.error(traceback.format_exc())
    finally:
      return response

  def edit_user(self, args: dict) -> dict:
    ''' Edit user information
  
      Remarks:
        ^required
      Args:
        args: a dictionary of new information (^user_id, username, password, email, first_name, last_name)
      Returns:
        response: dict, (success, message, data ...)
    '''
    logger.info('='*100)
    logger.info(f'edit_user() running...')
    response = std_response()
    try:
      r = check_params(args, required=['user_id'])
      if r['success']:
        if 'password' in args:
          args['password'] = hash(args['password'])
        r = self.db.retrieve(f'SELECT * FROM users WHERE user_id=%s AND is_active=1',[args['user_id']])
        if not r['rows_affected']:
          response['message'] = 'User does not exist.'   
        else:
          conditions = {'user_id': args['user_id'], 'is_active': 1}
          r = self.db.update(table='users', conditions=conditions, columns_values=args)
          if r['success']:
            response['success'] = True
            response['message'] = f'User information has been updated.'
    except Exception as e:
      logger.error(e)
      logger.error(traceback.format_exc())
    finally:
      return response

  def remove_user(self, args: dict) -> dict:
    ''' Remove Existing user
  
      Args:
        args: a dictionary contains (user_id)
      Returns:
        response: dict, (success, message, data ...)
    '''
    logger.info('='*100)
    logger.info(f'remove_user() running...')
    response = std_response()
    try:
      r = check_params(args, required=['user_id'])
      if r['success']:
        search_condition = args
        search_condition.update({'is_active': 1})
        r = self.db.select(table='users', conditions=search_condition)
        if not r['rows_affected']:
          response['message'] = 'Invalid credentials!'   
        else:
          r = self.db.update(table='users', conditions=args, columns_values={'is_active': 0})
          if r['success']:
            response['success'] = True
            response['message'] = f'User has been removed.'
    except Exception as e:
      logger.error(e)
      logger.error(traceback.format_exc())
    finally:
      return response

if __name__ == '__main__':
  r = Registration()
  # test_create = r.create_user({'username': 'chkhong', 'password': '12345678', 'email': 'hckj1999@gmail.com', 'first_name': 'Chu Henn', 'last_name': 'Khong'})
  # logger.debug(test_create)
  # test_remove = r.remove_user({'username': 'jessloh', 'email': 'hckj1999@gmail.com'})
  # logger.debug(test_remove)
  # test_edit = r.edit_user({'username': 'jessloh', 'email': 'hckj1999@gmail.com'})
  # logger.debug(test_edit)
  