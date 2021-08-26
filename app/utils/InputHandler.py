from loguru import logger
import traceback
from typing import List
from utils.OutputHandler import std_response

def check_params(args: dict, required: List[str]=[], either: List[List[str]]=[]) -> std_response:
  ''' Check if args contain parameters in requires_list

    Args:
      args: a dictionary to be checked
      required: list of required parameters
    Returns:
      response: dict, (success, message, data)
  '''
  is_complete = False
  required_checked = False
  either_checked = False
  e = ''
  try:
    if required:
      missing = [item for item in required if item not in args]
      required_checked = True if missing == [] else False
      if not required_checked:
        e = f'({", ".join(missing)}) required but missing!'
        raise TypeError(e)
    else:
      required_checked = True
    if either:
      if not isinstance(either[0], list):
        # make 1D list 2D
        either = [either]
      for ei in either:
        exist = [item for item in ei if item in args]
        either_checked = False if exist == [] else True
        if not either_checked:
          e = f'Either ({", ".join(ei)}) is required but missing!'
          raise TypeError(e)
    else:
      either_checked = True
    if required_checked and either_checked:
      is_complete = True
  except:
    logger.error(e)
    logger.error(traceback.format_exc())
  finally:
    return std_response(success=is_complete, message=e)


#################################################################
import unittest

class TestInputHandler(unittest.TestCase):

  def test_check_params(self):
    self.assertRaises(TypeError, check_params({'username': 'chkhong', 'passwords': '12345678', 'email': 'hckj1999@gmail.com', 'first_name': 'Chu Henn', 'last_name': 'Khong'},required=['username', 'password', 'email']))


if __name__ == '__main__':
  unittest.main()
  # test = check_params({'username': 'chkhong', 'password': '12345678', 'email': 'hckj1999@gmail.com', 'first_name': 'Chu Henn', 'last_name': 'Khong'},required=['username', 'password', 'email'])
  # logger.debug(test)
  # test2 = check_params({'test': 'test', 'either': 'hoho'},required=['test'], either=[['either', 'neither'], ['abc', 'def']])
  # logger.debug(test2)