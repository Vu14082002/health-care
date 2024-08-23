from passlib.context import CryptContext


class PasswordHandler:
    pwd_context = CryptContext(
        schemes=["bcrypt"],
        deprecated="auto",
    )

    @staticmethod
    def hash(password: str):
        """
         Hashes a password using the password context. It is recommended to use : func : ` pwd_context. hash ` instead of this function to avoid collisions between different password contexts.
         
         @param password - The password to hash. This should be a string that can be parsed by : func : ` pwd_to_string `.
         
         @return A 32 - byte string containing the hash of the password. The hash is guaranteed to be unique within the context
        """
        return PasswordHandler.pwd_context.hash(password)

    @staticmethod
    def verify(hashed_password, plain_password):
        """
         Verify a password. This is a wrapper around the : py : func : ` pwd_context. verify ` method of the
         
         @param hashed_password - The hash to verify.
         @param plain_password - The plain password to verify. It must be the same as the hashed password.
         
         @return True if the password is correct False otherwise. >>> from pywin32 import PasswordHandler >>> password = PasswordHandler. verify ('abcdefghijklmnopqrstuvwxyz'' abcdefghijklmnopqrstuvwxyz '
        """
        return PasswordHandler.pwd_context.verify(plain_password, hashed_password)
