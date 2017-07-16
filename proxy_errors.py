class EmptyProxyList(IndexError):
    """The proxy list is empty
    Attributes:
        message -- There are no proxies in the proxy list
    """
    def __init__(self, message):

        super().__init__(message)