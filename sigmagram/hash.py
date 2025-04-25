import bcrypt
import hmac
import hashlib
import json

with open('data/sigma.json', 'r') as file:
    key_data = json.load(file)
SECRET_KEY = key_data.get("secret_key", "default_secret_key").encode('utf-8')

def generate_hash(login, password):
    login += key_data['secret_key']
    password += key_data['secret_key']
    login_bytes = login.encode('utf-8')
    password_bytes = password.encode('utf-8')
    hmac_login = hmac.new(SECRET_KEY, login_bytes, hashlib.sha256).digest()
    hmac_password = hmac.new(SECRET_KEY, password_bytes, hashlib.sha256).digest()
    salt = bcrypt.gensalt()
    hashed_login = bcrypt.hashpw(hmac_login, salt)
    hashed_password = bcrypt.hashpw(hmac_password, salt)
    return hashed_login.decode('utf-8'), hashed_password.decode('utf-8')

def check_password(password, hashed_password_true):
    password += key_data['secret_key']
    password_bytes = password.encode('utf-8')
    hmac_password = hmac.new(SECRET_KEY, password_bytes, hashlib.sha256).digest()
    hashed_password_true_bytes = hashed_password_true.encode('utf-8')
    return bcrypt.checkpw(hmac_password, hashed_password_true_bytes)

def check_login(login, hashed_login_true):
    login += key_data['secret_key']
    login_bytes = login.encode('utf-8')
    hmac_login = hmac.new(SECRET_KEY, login_bytes, hashlib.sha256).digest()
    hashed_login_true_bytes = hashed_login_true.encode('utf-8')
    return bcrypt.checkpw(hmac_login, hashed_login_true_bytes)

if __name__ == "__main__":
    login = "user123"
    password = "my_secure_password"
    hashed_login, hashed_password = generate_hash(login, password)
    print("Хешированный логин:", hashed_login)
    print("Хешированный пароль:", hashed_password)
    is_password_valid = check_password(password, hashed_password)
    print("Пароль верный:", is_password_valid)
    is_login_valid = check_login(login, hashed_login)
    print("Логин верный:", is_login_valid)