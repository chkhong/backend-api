from pydantic import BaseModel, Field
from typing import Optional

class Tag:
  tags_metadata = [
    {
      "name": "Authentication"
    },
    {
      "name": "Registration"
    }
  ]

class StdResponse(BaseModel):
  success: bool = Field(..., title="")
  message: str = Field(..., title="Message")

class Schema:
  
  class Authentication:
    class LoginRequest(BaseModel):
      username: Optional[str] = Field(None)
      email: Optional[str] = Field(None)
      password: str = Field(...)

      class Example:
        examples = {
          'example 1': {
            'summary': 'Example 1',
            'description': 'Either username or email is required',
            'value': {
              'username': 'your_username',
              'email': 'your_email',
              'password': 'your_password',
            }
          }
        }

    class LoginResponse(StdResponse):
      data: Optional[dict] = Field(None, description='Includes token if successful')
      
      class Config:
        schema_extra = {
          'example': {
            'success': True,
            'message': '',
            'data': {
              'token': 'xxxxxxxxxxxxxxxxxxxxx'
            }
          }
        }


    class LogoutRequest(BaseModel):
      token: str = Field(..., description='Access token given during successful login.')

      class Example:
        examples = {
          'example 1': {
            'summary': 'Example 1',
            'value': {
              'token': 'xxxxxxxxxxxxxxxxxxxxx',
            }
          }
        }

    class LogoutResponse(StdResponse):
      data: Optional[dict] = Field(None)
      
      class Config:
        schema_extra = {
          'example': {
            'success': True,
            'message': '',
            'data': []
          }
        }
  



  class Registration:
    class CreateUserRequest(BaseModel):
      username: str = Field(...)
      email: str = Field(...)
      password: str = Field(...)
      first_name: Optional[str] = Field(None)
      last_name: Optional[str] = Field(None)
      
      class Example:
        examples = {
          'Example 1': {
            'summary': 'Example 1',
            'value': {
              'username': 'your_username',
              'email': 'your_email',
              'password': 'your_password',
              'first_name': 'your_first_name',
              'last_name': 'your_last_name',
            }
          },
        }
 

    class CreateUserResponse(StdResponse):
      data: Optional[dict] = Field(None)

      class Config:
        schema_extra = {
          'response': {
            'success': True,
            'message': '',
            'data': []
          }
        }


    class EditUserRequest(BaseModel):
      user_id: int = Field(...)
      username: Optional[str] = Field(None)
      email: str = Field(None)
      password: Optional[str] = Field(None)
      first_name: Optional[str] = Field(None)
      last_name: Optional[str] = Field(None)

      class Example:
        examples = {
          'Example 1': {
            'summary': 'Example 1',
            'value': {
              'user_id': 1,
              'username': 'your_username',
              'email': 'your_email',
              'password': 'your_password',
              'first_name': 'your_first_name',
              'last_name': 'your_last_name',
            }
          },
        }

    class EditUserResponse(StdResponse):
      data: Optional[dict] = Field(None)

      class Config:
        schema_extra = {
          'response': {
            'success': True,
            'message': '',
            'data': []
          }
        }

    class RemoveUserRequest(BaseModel):
      user_id: int = Field(...)

      class Example:
        examples = {
          'Example 1': {
            'summary': 'Example 1',
            'value': {
              'user_id': 'your_user_id',
            }
          },
        }

    class RemoveUserResponse(StdResponse):
      data: Optional[dict] = Field(None)

      class Config:
        schema_extra = {
          'response': {
            'success': True,
            'message': '',
            'data': []
          }
        }

    