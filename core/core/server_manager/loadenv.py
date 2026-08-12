import os
from dotenv import load_dotenv
from fastapi import FastAPI
from src.core.config import Config

def loadenv(app: FastAPI):
    '''Loads env variables to configure server'''
    load_dotenv(dotenv_path="./.env")
    config: Config= app.state.config
    #API keys
    config.bhasini_api_key= str(os.getenv("BHASINI_API_KEY"))
    #DB
    config.db_url = str(os.getenv("DB_URL"))
    #redis
    config.redis_url = str(os.getenv("REDIS_URL"))
    #Eureka
    config.eureka_server_url = str(os.getenv("EUREKA_SERVER_URL"))
    #server settings
    config.max_retry = int(os.getenv("MAX_RETRY","5"))
    config.timeout = float(os.getenv("TIMEOUT","3"))
    config.retry_delay_init = float(os.getenv("RETRY_DELAY_INIT","1"))
    config.min_db_conn = int(os.getenv("MIN_DB_CONN","2"))
    config.max_db_conn = int(os.getenv("MAX_DB_CONN","10"))
    config.instance_port = int(os.getenv("INSTANCE_PORT","8000"))
    config.service_name = str(os.getenv("SERVICE_NAME"))
    #JWT keys and hash algos
    config.jwt_hash_algo =str(os.getenv("JWT_HASH_ALGO"))
    config.jwt_key = str(os.getenv("JWT_KEY"))