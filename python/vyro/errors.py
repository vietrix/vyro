class VapiError(Exception):
    pass


class RouteDefinitionError(VapiError):
    pass


class HandlerSignatureError(VapiError):
    pass
