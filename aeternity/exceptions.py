class AException(Exception):
    def __init__(self, *args, payload=None):
        super().__init__(*args)
        self.payload = payload

    def __str__(self):
        return super().__str__() + '\npayload\n' + str(self.payload)


class AENSException(AException):
    pass


class MissingPreclaim(AENSException):
    pass


class PreclaimFailed(AENSException):
    pass


class TooEarlyClaim(AENSException):
    pass


class ClaimFailed(AENSException):
    pass


class NameNotAvailable(AENSException):
    pass


class UpdateError(Exception):
    pass


class InsufficientFundsException(AException):
    pass


class TransactionNotFoundException(AException):
    pass


class TransactionHashMismatch(AException):
    """Raised when the computed transaction hash differs from the one retrieved by the chain"""
    pass
