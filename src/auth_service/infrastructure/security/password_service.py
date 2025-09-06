import bcrypt

from auth_service.domain.services.password_service import AbstractPasswordService


class BCryptPasswordService(AbstractPasswordService):
    def hash_password(self, password: str) -> str:
        salt: bytes = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt).decode()

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
