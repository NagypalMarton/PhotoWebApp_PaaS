CREATE TABLE IF NOT EXISTS users (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  username VARCHAR(50) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_users_username (username)
);

CREATE TABLE IF NOT EXISTS photos (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  owner_user_id BIGINT UNSIGNED NOT NULL,
  name VARCHAR(40) NOT NULL,
  upload_datetime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  file_path_or_url VARCHAR(255) NOT NULL,
  PRIMARY KEY (id),
  KEY idx_photos_name (name),
  KEY idx_photos_upload_datetime (upload_datetime),
  CONSTRAINT fk_photos_owner FOREIGN KEY (owner_user_id) REFERENCES users(id) ON DELETE CASCADE
);
