import bcrypt


def hash_password(password: str) -> str:
    password = password.encode("utf-8")
    password = bcrypt.hashpw(password, bcrypt.gensalt())
    return password.decode("utf-8")

def check_password(user_password: str, hashed_password_db: str) -> bool:
    user_password = user_password.encode("utf-8")
    hashed_password_db = hashed_password_db.encode("utf-8")
    return bcrypt.checkpw(user_password, hashed_password_db)