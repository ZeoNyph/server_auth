from enum import Enum
import random, string, hashlib

class SecurityLevel(Enum):
    UNCLASSIFIED = 1
    SECRET = 2
    TOP_SECRET = 3
    ADMIN = 4

class User(object):

    password = "" # stored as SHA256 hash

    def __init__(self, username: str, email: str, secLevel: SecurityLevel, password = ""):
        self.username = username
        self.email = email
        self.secLevel = secLevel
        self.password = password

    def create_pw(self) -> str:
        if len(self.password) != 0:
            return None
        pass_str = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(15))
        self.password = hashlib.sha256(pass_str.encode()).hexdigest()
        return pass_str
    
    def get_name(self) -> str:
        return self.username
    
    def get_email(self) -> str:
        return self.email
    
    def get_secLevel(self) -> int:
        return self.secLevel
    
    def get_pw_hash(self) -> str:
        return self.password
    
