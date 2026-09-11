from src.core.exceptions.server_init_exceptions.server_init import ServerInitException
'''
If connection cannot be established to Redis on startup after multiple tries
'''
class RedisConnectionException(ServerInitException):
    def __int__(self):
        pass