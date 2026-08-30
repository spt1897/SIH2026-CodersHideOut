from src.core.exceptions.server_init_exceptions.server_init import ServerInitException

'''
If eureka server connection cannot be established on startup after multiple retries.
'''
class EurekaConnectionException(ServerInitException):
    def __init__(self, *args):
        super().__init__(*args)