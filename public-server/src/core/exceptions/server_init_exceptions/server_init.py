'''
Base Class for all runtime exceptions that may occur during 
Initialization of the microservice
Such exceptions shall be thrown on server startup
 and server must not be started without fixing them.
'''
class ServerInitException(Exception):
    def __init__(self, *args):
        super().__init__(*args)