from loguru import logger
import traceback
import time


def time_exec(f, seconds: int=5):
  ''' Time an execution time of a function

    Args:
      f: function to be executed (use lambda to pass function) eg. time_exec(lambda: hello_world(a=1, b='abc'))
      seconds: duration of the execution loop
    Returns:
      prints a counter and average time per execution      
  '''

  logger.info('-'*100)
  logger.info('time_exec() running...')
  counter = 0
  try:
    f()
    start_time = time.time()
    end_time = start_time + float(seconds)
    while time.time() < end_time:
      f()
      counter += 1
    logger.info(f'--- Finished {counter} times in {seconds} seconds ---')
    logger.info(f'--- Avg time: {(seconds / counter) * 1000} ms ---')
  except Exception as e:
    logger.error(e)
    logger.error(traceback.format_exc())
