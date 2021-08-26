from ntpath import join
from utils.InputHandler import check_params
from utils.OutputHandler import std_response
from utils.Hash import hash
from loguru import logger
import traceback
import jwt
import os
from dotenv import load_dotenv
from database import Database
import time

class Authentication:
  def __init__(self, db: Database=None):
    logger.debug('Initializing Authentication class...')
    self.db = Database()
    load_dotenv()
    self.secret_key = os.getenv('SECRET_KEY')

  def __del__(self):
    pass

  def verify_token(self, token: str) -> dict:
    ''' Verify JWT Token
  
      Args:
        token: jwt token to be verified
      Returns:
        response: dict, (success, message, data)
    '''
    # Flow: 
    # 1. get token from db
    # 2. decode token to get payload (must include exp)
    # 3. check exp (automatically)
    # 4. return false if 3 failed else true
    logger.info('='*100)
    logger.info(f'verify_token() running...')
    response = std_response()
    try:
      r = self.db.select(table='token_log', conditions={'jwt_token': token}, limit=1)
      logger.debug(r)
      if not r['rows_affected']:
        response['success'] = False
        response['message'] = 'Invalid token!'
        return
      data = r['data'][0]
      jwt.decode(data['jwt_token'], self.secret_key, algorithms='HS256')
      response['success'] = True
      response['message'] = 'Valid token!'
    except jwt.exceptions.ExpiredSignatureError:
      response['message'] = 'Invalid token!'
    except Exception as e:
      logger.error(e)
      logger.error(traceback.format_exc())
    finally:
      return response

  def __generate_token(self, args: dict={}) -> str:
    ''' Generate JWT Token
  
      Remarks:
        ^required
      Args:
        args: dictionary to be encoded (^user_id)
      Returns:
        jwt_token: str, an encoded JSON Web Token
    '''
    # Flow:
    # 1. get role_id, expiry_delta from args (determine expiry datetime)
    # 2. generate new token (set exp)
    # 3. add token to token_log, update last_log_id
    # 4. return token
    logger.info('='*100)
    logger.info(f'__generate_token() running...')
    encoded_jwt = ''
    try:
      r = check_params(args, required=['user_id'])
      if not r['success']:
        return
      # 1.
      r = self.db.retrieve('SELECT * FROM users INNER JOIN roles ON users.role_id=roles.role_id WHERE users.user_id=%s', [args['user_id']], 1)
      if not r['success']:
        return
      data = r['data'][0]
      # 2.
      unix_now = int(time.time())
      expiry_unix = unix_now + data['expiry_delta']
      to_encode = {'exp': expiry_unix}
      encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm='HS256')
      logger.info(f'JWT Token generated: {encoded_jwt} for user: {data["username"]}')
      args.update({'jwt_token': encoded_jwt})
      # 3.
      r = self.db.insert(table='token_log', columns_values=args)
      # 4.
      r = self.db.update(table='users', conditions={'user_id': args['user_id']}, columns_values={'last_log_id': r['last_insert_id']})
    except Exception as e:
      logger.error(e)
      logger.error(traceback.format_exc())
    finally:
      return encoded_jwt

  def login(self, args: dict) -> dict:
    ''' Login user
  
      Remarks:
        ^required,
        &either one required
      Args:
        args: a dictionary contains (&username, ^password, &email)
      Returns:
        response: dict, (success, message, data ...)
    '''
    logger.info('='*100)
    logger.info(f'login() running...')
    response = std_response()
    try:
      r = check_params(args, required=['password'], either=['username', 'email'])
      if not r['success']:
        return
      args['password'] = hash(args['password'])
      args.update({'is_active': 1})
      r = self.db.select(table=['users', 'token_log'], join='LEFT JOIN', join_condition='users.last_log_id=token_log.log_id', conditions=args)
      if not r['rows_affected']:
        response['message'] = 'Invalid username or password!'
        return
      data = r['data'][0]
      # if jwt_token is empty, decode error is raised
      jwt.decode(data['jwt_token'], self.secret_key, algorithms='HS256')  
      response['data'] = {'token': data['jwt_token']}
      response['message'] = 'Already logged in!'
      response['success'] = True
    except (jwt.exceptions.ExpiredSignatureError, jwt.exceptions.DecodeError):
      token = self.__generate_token({'user_id': data['user_id']})
      response['data'] = {'token': token}
      response['message'] = 'Login successful!'
      response['success'] = True
    except Exception as e:
      logger.error(e)
      logger.error(traceback.format_exc())
    finally:
      return response

  def logout(self, token: str) -> dict:
    ''' Logout user
  
      Args:
        token: jwt token to be deactivated
      Returns:
        response: dict, (success, message, data ...)
    '''
    # Flow
    # 1. retrieve jwt_token from token_log
    # 2. set exp time to now, encode
    # 3. update token_log
    logger.info('='*100)
    logger.info(f'logout() running...')
    response = std_response()
    try:
      # 1. 
      r = self.db.select(table='token_log', conditions={'jwt_token': token}, limit=1)
      if not r['rows_affected']:
        response['message'] = "Invalid token!"
        return
      # 2.
      data = r['data'][0]
      decoded_jwt = jwt.decode(data['jwt_token'], self.secret_key, algorithms='HS256')
      unix_now = int(time.time())
      decoded_jwt['exp'] = unix_now
      encoded_jwt = jwt.encode(decoded_jwt, self.secret_key, algorithm='HS256')
      # 3.
      r = self.db.update(table='token_log', conditions={'log_id': data['log_id']}, columns_values={'jwt_token': encoded_jwt})
      if r['success']:
        response['message'] = 'Logout successful!'
        response['success'] = True
    except Exception as e:
      logger.error(e)
      logger.error(traceback.format_exc())
    finally:
      return response

if __name__ == '__main__':
  import time
  start_time = time.time()
  a = Authentication()
  # a.generate_token(args={'user_id': 17})
  # test = a.verify_token('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2Mjg5MzI0MTV9.8yknRlZOVX2Jz6xe2gYyDde8X2sW3qG8YvDYrcg_L9g')
  # logger.debug(test)
  # params = {
  #   'username': 'chkhong',
  #   'password': '12345678'
  # }
  # test = a.login(params)
  # logger.debug(test)
  # test = a.logout('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2Mjg5NjA1MTl9.YPI3GCezIcBAA-CwGqmEQ92WaJbiPEoxTKIsXDIveFw')
  # logger.debug(test)
  logger.warning('--- %s seconds ---' % (time.time() - start_time))