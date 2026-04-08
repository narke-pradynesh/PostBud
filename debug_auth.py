# debug_auth.py
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

stored_hash = "$2b$12$iiWxL8vRGiAQNoxvV5xkjOwVE2KisDWA8jGyO82oQr.Zj4iMXlTuC"
password = "ruju0757"

print(pwd_context.verify(password, stored_hash))  # Should print True