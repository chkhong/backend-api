CREATE TABLE roles(
  role_id int(3) PRIMARY KEY AUTO_INCREMENT,
  name varchar(255),
  expiry_delta int(11) NOT NULL
);

CREATE TABLE token_log(
  log_id int(11) PRIMARY KEY AUTO_INCREMENT,
  user_id int(11),
  jwt_token varchar(2048) NOT NULL,
  created_datetime datetime DEFAULT CURRENT_TIMESTAMP
  --FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE users(
  user_id int(11) PRIMARY KEY AUTO_INCREMENT,
  username varchar(255) NOT NULL,
  password varchar(255) NOT NULL,
  first_name varchar(45),
  last_name varchar(45),
  email varchar(255) NOT NULL,
  role_id int(11) NOT NULL DEFAULT 2,
  last_log_id int(11), --stores id of last jwt token the user is holding
  is_active tinyint(1) DEFAULT 1,
  created_datetime datetime DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (role_id) REFERENCES roles(role_id),
  FOREIGN KEY (last_log_id) REFERENCES token_log(log_id)
);

ALTER TABLE token_log ADD FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE;