class Config:
    '''configuration object that stores static config variables used by the microservice.
    Loaded from environment variables on startup.'''
    def __init__(self):
        #API keys
        self.bhasini_api_key: str = ""
        #DB credentials
        self.db_url:str = ""
        #Redis credentials
        self.redis_url:str = ""
        #Eureka server credentials
        self.eureka_server_url:str = ""
        #server settings
        self.service_name:str =""
        self.max_retry:int =None
        self.retry_delay_init:float = None
        self.timeout:float = None
        self.min_db_conn:int =None
        self.max_db_conn:int =None
        self.instance_port:int = None
        #hashing algos and keys for JWT verification
        self.jwt_hash_algo:str = None
        self.jwt_key :str = None
        