import asyncio
import logging
import json
from enum import Enum
from queue import Queue

import namedtupled
import websockets

from aeternity import defaults

logger = logging.getLogger(__name__)


class Channel(object):
    """
    Create a state channel
    """

    PING_INTERVAL = 10
    PING_TIMEOUT = 5

    def __init__(self, channel_options):
        """
        Initialize the Channel object

        Args:
            channel_options: dict containing channel options

            channel_options contains/can contain following keys:

            channel_options.url (str) - Channel url (for example: "ws://localhost:3001")
            channel_options.role (str) - Participant role ("initiator" or "responder")
            channel_options.initiator_id (str) - Initiator's public key
            channel_options.responder_id (str) - Responder's public key
            channel_options.push_amount (int) - Initial deposit in favor of the responder by the initiator
            channel_options.initiator_amount (int) - Amount of tokens the initiator has committed to the channel
            channel_options.responder_amount (int) - Amount of tokens the responder has committed to the channel
            channel_options.channel_reserve (int) - The minimum amount both peers need to maintain
            [channel_options.ttl] (int) - Minimum block height to include the channel_create_tx
            channel_options.host (str) - Host of the responder's node
            channel_options.port (int) - The port of the responders node
            channel_options.lock_period (int) - Amount of blocks for disputing a solo close
            [channel_options.existing_channel_id] (str) - Existing channel id (required if reestablishing a channel)
            [channel_options.offchain_tx] (str) - Offchain transaction (required if reestablishing a channel)
            [channel_options.timeout_idle] (int) - The time waiting for a new event to be initiated (default: 600000)
            [channel_options.timeout_funding_create] (int) - The time waiting for the initiator to produce
            the create channel transaction after the noise session had been established (default: 120000)
            [channel_options.timeout_funding_sign] (int) - The time frame the other client has to sign an off-chain update
                                                            after our client had initiated and signed it. This applies only
                                                            for double signed on-chain intended updates: channel create transaction,
                                                            deposit, withdrawal and etc. (default: 120000)
            [channel_options.timeout_funding_lock] (int) - The time frame the other client has to confirm an on-chain transaction
                                                            reaching maturity (passing minimum depth) after the local node has detected this.
                                                            This applies only for double signed on-chain intended updates:
                                                            channel create transaction, deposit, withdrawal and etc. (default: 360000)
            [channel_options.timeout_sign] (int) - The time frame the client has to return a signed off-chain update or to decline it.
                                                    This applies for all off-chain updates (default: 500000)
            [channel_options.timeout_accept] (int) - The time frame the other client has to react to an event.
                                                    This applies for all off-chain updates that are not meant to land on-chain,
                                                    as well as some special cases: opening a noise connection, mutual closing acknowledgment and
                                                    reestablishing an existing channel (default: 120000)
            [channel_options.timeout_initialized] (int) - the time frame the responder has to accept an incoming noise session.
                                                        Applicable only for initiator (default: timeout_accept value)
            [channel_options.timeout_awaiting_open] (int) - The time frame the initiator has to start an outgoing noise session to the responder's node.
                                                            Applicable only for responder (default: timeout_idle's value)
            channel_options.sign (function) - Function which verifies and signs transactions
            channel_options.offchain_message_handler (function) - Callback method to receive off-chain messages.
                                                                  If not provided, all the incoming messages will be ignored.
            channel_options.error_handler (function) - Callback method to receive error messages.
                                                        If not provided, all error messages will be ignored.
        """
        options_keys = {'sign', 'endpoint', 'url', 'offchain_message_handler', 'error_handler'}
        endpoint = channel_options.get('endpoint', defaults.CHANNEL_ENDPOINT)
        wsUrl = channel_options.get('url', defaults.CHANNEL_URL)
        self.sign = channel_options.get('sign', None)
        self.offchain_message_handler = channel_options.get('offchain_message_handler', None)
        self.error_handler = channel_options.get('error_handler', None)
        self.params = {k: channel_options[k] for k in channel_options.keys() if k not in options_keys}
        self.url = self.__channel_url(wsUrl, self.params, endpoint)
        self.params = namedtupled.map(self.params)
        self.status = None
        self.id = None
        self.is_locked = False
        self.round = 0
        self.action_queue = Queue()

    def create(self):
        """
        Invoke to establish the websocket connection and initialize the state channel
        """
        self.status = ChannelState.CHANNEL_OPEN
        asyncio.ensure_future(self.__start_ws())

    async def __start_ws(self):
        """
        Set up websocket and attach the message handler
        """
        async with websockets.connect(self.url, ping_interval=self.PING_INTERVAL, ping_timeout=self.PING_TIMEOUT) as websocket:
            self.ws = websocket
            await self.__message_handler()

    async def __message_handler(self):
        """
        Message handler for incoming messages
        """
        async for message in self.ws:
            logger.debug(f'Incoming: {message}')
            msg = json.loads(message)
            if 'error' in msg and self.error_handler is not None:
                self.error_handler(msg)
            elif 'method' in msg:
                if msg['method'] == 'channels.info':
                    self.status = ChannelState(msg['params']['data']['event'])
                    if self.status == ChannelState.OPEN:
                        self.id = msg['params']['channel_id']
                if msg['method'] == 'channels.message' and self.offchain_message_handler is not None:
                    self.offchain_message_handler(msg)
                if msg['method'].startswith('channels.sign'):
                    tx = msg['params']['data']['tx']
                    if msg['method'] == f'channels.sign.{self.params.role}_sign':
                        self.__sign_channel_tx(f'channels.{self.params.role}_sign', tx)
                    else:
                        self.__sign_channel_tx(msg['method'].replace('sign.', ''), tx)

    def __channel_url(self, url, params, endpoint):
        """
        construct channel url using the given channel options
        """
        param_string = '&'.join('{!s}={!r}'.format(key, val) for (key, val) in params.items())
        return f'{url}/{endpoint}?{param_string}'.replace("'", "")

    def __channel_call(self, method, params):
        """
        Construct and send channel messages over the websocket
        """
        message = {
            'jsonrpc': '2.0',
            'method': method,
            'params': params
        }
        logger.debug(f'Sending: { json.dumps(message) }')
        asyncio.ensure_future(self.ws.send(json.dumps(message)))
        if not self.action_queue.empty() and not self.is_locked:
            self.__process_queue()

    def balances(self, accounts=None):
        """
        Get balances

        Args:
            accounts: a list of addresses to fetch the balances of.
                    Those can be either account balances or a contract ones,
                    encoded as an account addresses.
                    If a certain account address had not being found in the state tree
                    - it is simply skipped in the response.

                    default: [initiator_id, responder_id]
        """
        accounts = accounts if accounts else [self.params.initiator_id, self.params.responder_id]
        self.__channel_call('channels.get.balances', {'accounts': accounts})

    def send_message(self, message, recipient):
        """
        Send generic message

        If message is an object it will be serialized into JSON string
        before sending.

        If there is ongoing update that has not yet been finished the message
        will be sent after that update is finalized.
        """
        if type(message) is dict:
            message = json.dumps(message)

        self.__enqueue_action({
            'method': 'channels.message',
            'params': {
                'info': message,
                'to': recipient
            }
        })

    def __sign_channel_tx(self, method, tx):
        """
        Sign the transactions received over channel by the provided sign method
        """
        signedTx = self.sign(tx)
        self.__enqueue_action({
            'method': method,
            'params': {
                'tx': signedTx.tx
            }
        })

    def leave(self):
        """
        Leave Channel
        """
        self.__enqueue_action({
            'method': 'channels.leave',
            'params': {}
        })

    def shutdown(self):
        """
        Trigger mutual close
        """
        self.__enqueue_action({
            'method': 'channels.shutdown',
            'params': {}
        })

    def state(self):
        """
        Get current offchain state
        """
        self.__channel_call('channels.get.offchain_state', {})

    def deposit(self, amount):
        """
        Deposit tokens into the channel

        After the channel had been opened any of the participants can initiate a deposit.
        The process closely resembles the update. The most notable difference is that the
        transaction has been co-signed: it is channel_deposit_tx and after the procedure
        is finished - it is being posted on-chain.

        Any of the participants can initiate a deposit. The only requirements are:

            - Channel is already opened
            - No off-chain update/deposit/withdrawal is currently being performed
            - Channel is not being closed or in a solo closing state
            - The deposit amount must be equal to or greater than zero, and cannot exceed
              the available balance on the channel (minus the channel_reserve)
        """
        self.__enqueue_action({
            'method': 'channels.deposit',
            'params': {
                'amount': amount
            }
        })

    def withdraw(self, amount):
        """
        Withdraw tokens from the channel

        After the channel had been opened any of the participants can initiate a withdrawal.
        The process closely resembles the update. The most notable difference is that the
        transaction has been co-signed: it is channel_withdraw_tx and after the procedure
        is finished - it is being posted on-chain.

        Any of the participants can initiate a withdrawal. The only requirements are:

            - Channel is already opened
            - No off-chain update/deposit/withdrawal is currently being performed
            - Channel is not being closed or in a solo closing state
            - The withdrawal amount must be equal to or greater than zero, and cannot exceed
              the available balance on the channel (minus the channel_reserve)
        """
        self.__enqueue_action({
            'method': 'channels.withdraw',
            'params': {
                'amount': amount
            }
        })

    def get_id(self):
        """
        Get Channel id if set else None
        """
        return self.id

    def __process_queue(self):
        if not self.action_queue.empty() and not self.is_locked:
            task = self.action_queue.get()
            self.is_locked = True
            self.__channel_call(task["method"], task["params"])
            self.action_queue.task_done()
            self.is_locked = False

    def __enqueue_action(self, task=None):
        if task is not None:
            self.action_queue.put(task)
            self.__process_queue()


class ChannelState(Enum):
    """
    Enum for state channel messages/state
    """
    CHANNEL_OPEN = 'channel_open'
    CHANNEL_CLOSED = 'channel_closed'
    CHANNEL_ACCEPT = 'channel_accept'
    DIED = 'died'
    FUNDING_CREATED = 'funding_created'
    FUNDING_SIGNED = 'funding_signed'
    FUNDING_LOCKED = 'funding_locked'
    OWN_FUNDING_LOCKED = 'own_funding_locked'
    REESTABLISH = 'channel_reestablish'
    LEAVE = 'leave'
    SHUTDOWN = 'shutdown'
    OPEN = 'open'
    DEPOSIT_CREATED = 'deposit_created'
    OWN_DEPOSIT_LOCKED = 'own_deposit_locked'
    DEPOSIT_LOCKED = 'deposit_locked'
    WITHDRAW_CREATED = 'withdraw_created'
    OWN_WITHDRAW_LOCKED = 'own_withdraw_locked'
    WITHDRAW_LOCKED = 'withdraw_locked'
