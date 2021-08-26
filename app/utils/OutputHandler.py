from typing import Union

def std_response(success: bool=False, message: str='', data: Union[list,dict]=[], **kwargs) -> dict:
  ''' standard response containing success, message, data at least

    Args:
      success: if the function is success or not
      message: message if the function fails
      data: data to be returned if the function contains
    Returns:
      response: dict, (success, message, data)
  '''
  response = {'success': success, 'message': message, 'data': data}
  for k, v in kwargs.items():
    response.update({k : v})
  return response