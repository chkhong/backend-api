from loguru import logger
import traceback
from typing import Tuple


def dict_to_two_list(args: dict) -> Tuple[list, list]:
  ''' Split a dictionary to a list of keys and a list of values

    Args:
      args: dictionary to be parsed
    Returns:
      key: list of keys
      value: list of values
  '''
  key = []
  value = []
  try:
    if not isinstance(args, dict):
      raise Exception('Error: args is a not dict type')
    for k, v in args.items():
      key.append(k)
      value.append(v)
  except Exception as e:
    logger.error(e)
    logger.error(traceback.format_exc())
  finally:
    return key, value



if __name__ == '__main__':
  key, value = dict_to_two_list({'username': 'chkhong', 'passwordd': '12345678', 'email': 'hckj1999@gmail.com', 'first_name': 'Chu Henn', 'last_name': 'Khong'})
