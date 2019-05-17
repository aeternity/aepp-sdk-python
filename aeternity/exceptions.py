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


class NameTooEarlyClaim(Exception):
    pass


class NameCommitmentIdMismatch(Exception):
    """ Raised when a commitment id cannot be verified """
    pass


class ClaimFailed(AENSException):
    pass


class NameNotAvailable(AENSException):
    pass


class NameUpdateError(Exception):
    pass


class InsufficientFundsException(AException):
    pass


class TransactionNotFoundException(AException):
    pass


class TransactionHashMismatch(AException):
    """Raised when the computed transaction hash differs from the one retrieved by the chain"""
    pass


class TransactionWaitTimeoutExpired(AException):
    """Raised when a transaction hasn't been found after waiting for an amount of time"""

    def __init__(self, tx_hash, reason):
        self.tx_hash = tx_hash
        self.reason = reason


class BlockWaitTimeoutExpired(Exception):
    """Raised when a block height hasn't been reached after waiting for an amount of time"""
    pass


class UnsupportedNodeVersion(Exception):
    """Raised when the node target runs an unsupported version"""


class ConfigException(Exception):
    """Raised in case of configuration errors"""
    pass


class UnsupportedTransactionType(Exception):
    """Raised for unknow transaction tag"""
    pass


class TransactionFeeTooLow(Exception):
    """Raised for transaction fee with too low value"""
    pass
