from .services import log_action


class AuditLogMiddleware:
   
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.audit = lambda action, **kw: log_action(request, action, **kw)
        return self.get_response(request)