from passlib.context import CryptContext

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PasswordController:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return password_context.verify(plain_password, hashed_password)

    @staticmethod
    def generate_hashed_password(password: str) -> str:
        return password_context.hash(password)