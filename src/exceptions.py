class IllegalPiecePosError(Exception):
    pass


class IllegalCardSelection(Exception):
    pass

class IllegalPlayerActionError(Exception):
    pass

class NetworkError(Exception):
    def __init__(self, msg=''):
        super().__init__()
        self.msg = msg