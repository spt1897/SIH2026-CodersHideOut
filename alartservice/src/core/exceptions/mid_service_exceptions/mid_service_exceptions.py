'''
These are exceptions which may occur while service is running, such as
failing to read/write to a DB or cache after multiple tries or related to a
client or service. Such exceptions need not require to service to shutdown but
rather inform the client that their request failed due to some issue and 
that they must try again later. Let the user handle them.
'''
class MidServiceExceptions(Exception):
    def __init__(self, *args):
        super().__init__(*args)