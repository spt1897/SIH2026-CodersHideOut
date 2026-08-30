from src.core.exceptions.mid_service_exceptions.mid_service_exceptions import MidServiceExceptions
'''If we are unable to send a whatsapp msg after multiple retries,
server handles that knwoledge accordingly'''
class WhatsappSendException(MidServiceExceptions):
    def __int__(self):
        pass