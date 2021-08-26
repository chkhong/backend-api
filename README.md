# Authentication & Registration Docs

API for user login, logout, token authenticaion and configure user database

---

- [1. Database Design](#1-database-design)
- [2. Authentication](#2-authentication)
  - [2.1. Login](#21-login)
    - [2.1.1. Request](#211-request)
    - [2.1.2. Response (Success)](#212-response-success)
    - [2.1.3. Response (Error)](#213-response-error)
  - [2.2. Logout](#22-logout)
    - [2.2.1. Request](#221-request)
    - [2.2.2. Response (Success)](#222-response-success)
    - [2.2.3. Response (Error)](#223-response-error)
- [3. Configure User](#3-configure-user)
  - [3.1. Create User](#31-create-user)
    - [3.1.1. Request](#311-request)
    - [3.1.2. Response (Success)](#312-response-success)
    - [3.1.3. Response (Error)](#313-response-error)
  - [3.2. Edit User](#32-edit-user)
    - [3.2.1. Request](#321-request)
    - [3.2.2. Response (Success)](#322-response-success)
    - [3.2.3. Response (Error)](#323-response-error)
  - [3.3. Remove User](#33-remove-user)
    - [3.3.1. Request](#331-request)
    - [3.3.2. Response (Success)](#332-response-success)
    - [3.3.3. Response (Error)](#333-response-error)

---

## 1. Database Design

![Database Design](/docs/db_design.png)

---

## 2. Authentication

### 2.1. Login

Authenticate user and return access `token` if success.

#### 2.1.1. Request

**URL** : `/login`

**Method** : `POST`

**Header Parameters** : Not required

**JSON Parameters**

| Name     | Required | Description                          |
| -------- | -------- | ------------------------------------ |
| username | true     | Either username or email is required |
| email    | true     | Either username or email is required |
| password | true     |                                      |

**Example**

```json
{
  "username": "your_username",
  "email": "your_email",
  "password": "your_password"
}
```

#### 2.1.2. Response (Success)

**Code** : `200 OK`

**Content** :

```json
{
  "success": True,
  "message": '',
  "data": {
    "token": "xxxxxxxxxxxxxxxxxxxxx"
  }
}
```

#### 2.1.3. Response (Error)

**Code** : `400 BAD REQUEST`

**Content** :

```json
{
  "success": False,
  "message": 'Error message',
  "data": []
}
```

---

### 2.2. Logout

Logout user, deactivate `token`.

#### 2.2.1. Request

**URL** : `/logout`

**Method** : `POST`

**JSON Parameters**

| Name  | Required | Description                                |
| ----- | -------- | ------------------------------------------ |
| token | yes      | Access token given during successful login |

**Example**

```json
{
  "token": "xxxxxxxxxxxxxxxxxxxxx"
}
```

#### 2.2.2. Response (Success)

**Code** : `200 OK`

**Content** :

```json
{
  "success": True,
  "message": '',
  "data": []
}
```

#### 2.2.3. Response (Error)

**Code** : `400 BAD REQUEST`

**Content** :

```json
{
  "success": False,
  "message": 'Error message',
  "data": []
}
```

---

## 3. Configure User

### 3.1. Create User

Create a new user

#### 3.1.1. Request

**URL** : `/user`

**Method** : `POST`

**Header Parameters**

| Name  | Required | Description        |
| ----- | -------- | ------------------ |
| token | yes      | valid access token |

**JSON Parameters**

| Name       | Required | Description |
| ---------- | -------- | ----------- |
| username   | yes      |             |
| email      | yes      |             |
| password   | yes      |             |
| first_name | no       |             |
| last_name  | no       |             |

**Example**

```json
{
  "username": "your_username",
  "email": "your_email",
  "password": "your_password",
  "first_name": "your_first_name",
  "last_name": "your_last_name"
}
```

#### 3.1.2. Response (Success)

**Code** : `200 OK`

**Content** :

```json
{
  "success": True,
  "message": '',
  "data": []
}
```

#### 3.1.3. Response (Error)

**Code** : `400 BAD REQUEST`

**Content** :

```json
{
  "success": False,
  "message": 'Error message',
  "data": []
}
```

---

### 3.2. Edit User

Edit existing user information

#### 3.2.1. Request

**URL** : `/user`

**Method** : `PUT`

**Header Parameters**

| Name  | Required | Description        |
| ----- | -------- | ------------------ |
| token | yes      | valid access token |

**JSON Parameters**

| Name       | Required | Description                    |
| ---------- | -------- | ------------------------------ |
| user_id    | yes      |                                |
| username   | no       | Input only if the value is new |
| email      | no       | Input only if the value is new |
| password   | no       | Input only if the value is new |
| first_name | no       | Input only if the value is new |
| last_name  | no       | Input only if the value is new |

**Example**

```json
{
  "user_id": 1,
  "username": "your_new_username",
  "email": "your_email",
  "password": "your_new_password",
  "first_name": "your_new_first_name",
  "last_name": "your_new_last_name"
}
```

#### 3.2.2. Response (Success)

**Code** : `200 OK`

**Content** :

```json
{
  "success": True,
  "message": '',
  "data": []
}
```

#### 3.2.3. Response (Error)

**Code** : `400 BAD REQUEST`

**Content** :

```json
{
  "success": False,
  "message": 'Error message',
  "data": []
}
```

---

### 3.3. Remove User

Remove existing user

#### 3.3.1. Request

**URL** : `/user`

**Method** : `DELETE`

**Header Parameters**

| Name  | Required | Description        |
| ----- | -------- | ------------------ |
| token | yes      | valid access token |

**JSON Parameters**

| Name    | Required | Description |
| ------- | -------- | ----------- |
| user_id | yes      |             |

**Example**

```json
{
  "user_id": 1
}
```

#### 3.3.2. Response (Success)

**Code** : `200 OK`

**Content** :

```json
{
  "success": True,
  "message": '',
  "data": []
}
```

#### 3.3.3. Response (Error)

**Code** : `400 BAD REQUEST`

**Content** :

```json
{
  "success": False,
  "message": 'Error message',
  "data": []
}
```

---
