from src.core.exceptions.mid_service_exceptions.mid_service_exceptions import MidServiceExceptions
'''Failing to write/read to DB after multiple retries, just say the client ,
failed to load data. try again later.'''

class FailedDBOperationException(MidServiceExceptions):
    def __init__(self, *args):
        super().__init__(*args)