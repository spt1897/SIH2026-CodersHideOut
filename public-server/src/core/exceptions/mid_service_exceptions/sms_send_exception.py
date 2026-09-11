from src.core.exceptions.mid_service_exceptions.mid_service_exceptions import MidServiceExceptions
'''If we are unable to send an sms after multiple retries,
server handles that knwoledge accordingly'''
class SmsSendException(MidServiceExceptions):
    def __int__(self):
        pass