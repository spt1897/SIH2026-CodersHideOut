import os

class Config:
    '''configuration object that stores static config variables used by the microservice.
    Loaded from environment variables on startup.'''
    def __init__(self):
        # API keys
        # self.bhasini_api_key: str = os.getenv("BHASINI_API_KEY", "")
        
        # DB credentials
        # self.db_url: str = os.getenv("DB_URL", "")
        
        # Redis credentials
        # self.redis_url: str = os.getenv("REDIS_URL", "")
        
        # Eureka server credentials
        self.eureka_server_url: str = os.getenv("EUREKA_SERVER_URL", "http://localhost:8761/eureka")
        
        # Server settings
        self.service_name: str = os.getenv("SERVICE_NAME", "alert-service")
        self.max_retry: int = int(os.getenv("MAX_RETRY", "3"))
        self.retry_delay_init: float = float(os.getenv("RETRY_DELAY_INIT", "1"))
        self.timeout: float = float(os.getenv("TIMEOUT", "3"))
        self.min_db_conn: int = int(os.getenv("MIN_DB_CONN", "2"))
        self.max_db_conn: int = int(os.getenv("MAX_DB_CONN", "10"))
        self.instance_port: int = int(os.getenv("INSTANCE_PORT", "8001"))
        self.process_pool_size: int = int(os.getenv("PROCESS_POOL_SIZE", "0"))
        
        # Hashing algos and keys for JWT verification
        # self.jwt_hash_algo: str = os.getenv("JWT_HASH_ALGO", "HS256")
        # self.jwt_key: str = os.getenv("JWT_KEY", "")
        
        # Twilio
        self.twilio_phone_no: str = os.getenv("TWILIO_PHONE_NO", "")
        self.twilio_account_sid: str = os.getenv("TWILIO_ACCOUNT_SID", "")
        self.twilio_auth_token: str = os.getenv("TWILIO_AUTH_TOKEN", "")
        # self.twilio_whatsapp_no: str = os.getenv("TWILIO_WHATSAPP_NO", "")
        
        # SMTP
        # self.smtp_host: str = os.getenv("SMTP_HOST", "")
        # self.smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
        # self.smtp_username: str = os.getenv("SMTP_USERNAME", "")
        # self.smtp_password: str = os.getenv("SMTP_PASSWORD", "")
        # self.smtp_address_from: str = os.getenv("SMTP_ADDRESS_FROM", "")