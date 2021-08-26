import uvicorn
from loguru import logger
import traceback
from fastapi import FastAPI, Request, status, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from schema import Schema, Tag

from utils.OutputHandler import std_response
from database import Database
from authentication import Authentication
from registration import Registration

schema = Schema()
tag = Tag()
app = FastAPI(
  title="Registration & Authentication",
  description="Backend API",
  openapi_tags=tag.tags_metadata
)

# allow CORS setting
origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# security setting
# https://geekflare.com/http-header-implementation/https://geekflare.com/http-header-implementation/
HEADERS = {
    # CORS setting
    "Access-Control-Allow-Credentials": "true",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "*",
    "Access-Control-Allow-Headers": "*",
    # security setting
    "X-Frame-Options": "SAMEORIGIN",
    "X-Content-Type-Options": "nosniff",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Expect-CT": "max-age=86400, enforce", # enforcement of Certificate Transparency for 24 hours
    "Content-Security-Policy": "default-src https:"
}

db = Database()
auth = Authentication(db=db)
reg = Registration(db=db)

OUTPUT_RESPONSE = {
    "success": False,
    "message": "",
    "data": {}
}

def set_out_response(**args)->dict:
    ''' merge args into OUTPUT_RESPONSE,
        param @args, e.g. args = { 'success': True, 'data': {...} }
    '''
    # content = dict(OUTPUT_RESPONSE, **args)

    response = JSONResponse(content=args, headers=HEADERS)

    # return content # return content w/o headers
    return response # return content w/ headers

@app.middleware('http')
async def verifyToken(request: Request, call_next):
    response = std_response()
    exception_list = ['login', 'logout', 'docs', 'openapi.json']
    try:
      url = str(request.url)
      endpoint = url.split('/')[-1]
      if endpoint not in exception_list:
        # verify token before any action
        if 'token' not in request.headers:
          response['message'] = 'Error occurred, please attach token on header to perform action.'
          return JSONResponse(content=response, headers=HEADERS, status_code=status.HTTP_401_UNAUTHORIZED)
        token = request.headers['token']
        result = auth.verify_token(token=token)
        if result['success']:
          response = await call_next(request)
          return response
        else:
          response['message'] = result['message']
          return JSONResponse(content=response, headers=HEADERS, status_code=status.HTTP_401_UNAUTHORIZED)
      else:
        # runs exception list without verification
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())


@app.post('/login', response_model=schema.Authentication.LoginResponse, tags=['Authentication'])
async def login(request: schema.Authentication.LoginRequest = Body(..., examples=schema.Authentication.LoginRequest.Example.examples)):
  response = std_response()
  try:
    args = request.dict(exclude_unset=True)
    logger.debug(args)
    response = auth.login(args=args)
  except Exception as e:
    logger.error(e)
    logger.error(traceback.format_exc())
  finally:
    return set_out_response(**response)

@app.post('/logout', response_model=schema.Authentication.LogoutResponse, tags=['Authentication'])
async def logout(request: schema.Authentication.LogoutRequest = Body(..., examples=schema.Authentication.LogoutRequest.Example.examples)):
  response = std_response()
  try:
    args = request.dict()
    response = auth.logout(token=args['token'])
  except Exception as e:
    logger.error(e)
    logger.error(traceback.format_exc())
  finally:
    return set_out_response(**response)

@app.post('/user', response_model=schema.Registration.CreateUserResponse, tags=['Registration'])
async def create_user(request: schema.Registration.CreateUserRequest = Body(..., examples=schema.Registration.CreateUserRequest.Example.examples)):
  response = std_response()
  try:
    args = request.dict(exclude_unset=True)
    response = reg.create_user(args=args)
  except Exception as e:
    logger.error(e)
    logger.error(traceback.format_exc())
  finally:
    return set_out_response(**response)

@app.put('/user', response_model=schema.Registration.EditUserResponse, tags=['Registration'])
async def edit_user(request: schema.Registration.EditUserRequest = Body(..., examples=schema.Registration.EditUserRequest.Example.examples)):
  response = std_response()
  try:
    args = request.dict(exclude_unset=True)
    response = reg.edit_user(args=args)
  except Exception as e:
    logger.error(e)
    logger.error(traceback.format_exc())
  finally:
    return set_out_response(**response)

@app.delete('/user', response_model=schema.Registration.RemoveUserResponse, tags=['Registration'])
async def remove_user(request: schema.Registration.RemoveUserRequest = Body(..., examples=schema.Registration.RemoveUserRequest.Example.examples)):
  response = std_response()
  try:
    args = request.dict(exclude_unset=True)
    response = reg.remove_user(args=args)
  except Exception as e:
    logger.error(e)
    logger.error(traceback.format_exc())
  finally:
    return set_out_response(**response)



if __name__ == '__main__':
  uvicorn.run("main:app", host="127.0.0.1", port=5000, log_level="info", reload=True)