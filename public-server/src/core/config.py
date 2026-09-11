class Config:
    '''configuration object that stores static config variables used by the microservice.
    Loaded from environment variables on startup.'''
    def __init__(self):
        #API keys
        self.bhasini_api_key: str = None
        #DB credentials
        self.db_url:str = None
        #Redis credentials
        self.redis_url:str = None
        #Eureka server credentials
        self.eureka_server_url:str = None
        #server settings
        self.service_name:str =None
        self.max_retry:int =None
        self.retry_delay_init:float = None
        self.timeout:float = None
        self.min_db_conn:int =None
        self.max_db_conn:int =None
        self.instance_port:int = None
        self.process_pool_size:int =None
        #hashing algos and keys for JWT verification
        self.jwt_hash_algo:str = None
        self.jwt_key :str = None
        #twilio
        self.twilio_phone_no :str = None
        self.twilio_account_sid:str=None
        self.twilio_auth_token:str=None
        self.twilio_whatsapp_no:str = None
        #smtp
        self.smtp_host:str=None
        self.smtp_port:str =None
        self.smtp_username:str =None
        self.smtp_password:str=None
        self.smtp_address_from:str = None
        