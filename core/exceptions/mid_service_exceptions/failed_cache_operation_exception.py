from src.core.exceptions.mid_service_exceptions.mid_service_exceptions import MidServiceExceptions
'''Failing to write/read from cache after multiple retries,
 read directly from DB in such cases'''

class FailedCacheOperationException(MidServiceExceptions):
    def __init__(self, *args):
        super().__init__(*args)