from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

TOKEN_SALT = "task-manager-auth"
TOKEN_MAX_AGE_SECONDS = 60 * 60 * 24


def create_token(user_id: int, secret_key: str) -> str:
    serializer = URLSafeTimedSerializer(secret_key, salt=TOKEN_SALT)
    return serializer.dumps({"user_id": user_id})


def verify_token(token: str, secret_key: str, max_age: int = TOKEN_MAX_AGE_SECONDS):
    serializer = URLSafeTimedSerializer(secret_key, salt=TOKEN_SALT)
    try:
        payload = serializer.loads(token, max_age=max_age)
    except (BadSignature, SignatureExpired):
        return None
    return payload if isinstance(payload, dict) and "user_id" in payload else None
