from loguru import logger
import unittest
import traceback
import hashlib


HASH_SALT = 'chu henn'


def hash(password: str, algorithm: str='SHA256') -> str:
  ''' Hash password with hashing algorithms

    Args:
      password: password to be hashed
      algorithm: hashing algorithm
        *default value: SHA256

    Returns:
      hashed_password: str, hashed password

    References:
      https://docs.python.org/3/library/hashlib.html#key-derivation
  '''
  hashed_password:str = ''
  try:
    logger.debug('Hashing password...')
    hashcode = hashlib.pbkdf2_hmac(algorithm, str.encode(password), str.encode(HASH_SALT), 100000)
    hashed_password = hashcode.hex()
  except Exception as e:
    logger.error(e)
    logger.error(traceback.format_exc())
  finally:
    return hashed_password


class TestHash(unittest.TestCase):
  def test_hash(self):
    ''' Test failure might be due to salt changes
    '''
    self.assertEqual(hash(password='12345678',algorithm='sha1'),'2f27b0e239ad12605978cd792e299323a8f98ee5')
    self.assertEqual(hash(password='12345678',algorithm='sha224'),'de6b3feb754628255e40b08cafa95a2a4d54674b112793feb82654c4')
    self.assertEqual(hash(password='12345678',algorithm='sha256'),'d47f8689e39f0bc3fb1b9ad25c30a24ba246101c8deacb3e0bad91d4a03b3553')
    self.assertEqual(hash(password='123456789',algorithm='sha256'),'263d54ccbf431ddb872e14646ed06aedc0111994c719445dee69ce6715b090f9')

if __name__ == '__main__':
  unittest.main()