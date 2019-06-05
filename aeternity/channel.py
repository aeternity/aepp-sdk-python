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

    def __init__(self, **kwargs):
        """
        Initialize the Channel object

        :param url (str): Channel url (for example: "ws://localhost:3001")
        :param role (str): Participant role ("initiator" or "responder")
        :param initiator_id (str): Initiator's public key
        :param responder_id (str): Responder's public key
        :param push_amount (int): Initial deposit in favor of the responder by the initiator
        :param initiator_amount (int): Amount of tokens the initiator has committed to the channel
        :param responder_amount (int): Amount of tokens the responder has committed to the channel
        :param channel_reserve (int): The minimum amount both peers need to maintain
        :param ttl (int): Minimum block height to include the channel_create_tx
        :param host (str): Host of the responder's node
        :param port (int): The port of the responders node
        :param lock_period (int): Amount of blocks for disputing a solo close
        :param existing_channel_id (str): Existing channel id (required if reestablishing a channel)
        :param offchain_tx (str): Offchain transaction (required if reestablishing a channel)
        :param timeout_idle (int): The time waiting for a new event to be initiated (default: 600000)
        :param timeout_funding_create (int): The time waiting for the initiator to produce
        :param the create channel transaction after the noise session had been established (default: 120000)
        :param timeout_funding_sign (int): The time frame the other client has to sign an off-chain update
                                                        after our client had initiated and signed it. This applies only
                                                        for double signed on-chain intended updates: channel create transaction,
                                                        deposit, withdrawal and etc. (default: 120000)
        :param timeout_funding_lock (int): The time frame the other client has to confirm an on-chain transaction
                                                        reaching maturity (passing minimum depth) after the local node has detected this.
                                                        This applies only for double signed on-chain intended updates:
                                                        channel create transaction, deposit, withdrawal and etc. (default: 360000)
        :param timeout_sign (int): The time frame the client has to return a signed off-chain update or to decline it.
                                                This applies for all off-chain updates (default: 500000)
        :param timeout_accept (int): The time frame the other client has to react to an event.
                                                This applies for all off-chain updates that are not meant to land on-chain,
                                                as well as some special cases: opening a noise connection, mutual closing acknowledgment and
                                                reestablishing an existing channel (default: 120000)
        :param timeout_initialized (int): the time frame the responder has to accept an incoming noise session.
                                                    Applicable only for initiator (default: timeout_accept value)
        :param timeout_awaiting_open (int): The time frame the initiator has to start an outgoing noise session to the responder's node.
                                                        Applicable only for responder (default: timeout_idle's value)
        :param sign (function): Function which verifies and signs transactions
        :param offchain_message_handler (function): Callback method to receive off-chain messages.
                                                                If not provided, all the incoming messages will be ignored.
        :param error_handler (function): Callback method to receive error messages.
                                                    If not provided, all error messages will be ignored.
        """
        options_keys = {'sign', 'endpoint', 'url'}
        endpoint = kwargs.get('endpoint', defaults.CHANNEL_ENDPOINT)
        wsUrl = kwargs.get('url', defaults.CHANNEL_URL)
        self.sign = kwargs.get('sign', None)
        self.params = {k: kwargs[k] for k in kwargs.keys() if k not in options_keys}
        self.url = self.__channel_url(wsUrl, self.params, endpoint)
        self.params = namedtupled.map(self.params)
        self.status = None
        self.id = None
        self.is_locked = False
        self.action_queue = Queue()
        self.handlers = {}

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
            if 'error' in msg and ChannelState.ERROR in self.handlers:
                self.handlers[ChannelState.ERROR](msg)
            elif 'method' in msg:
                if msg['method'] == 'channels.info':
                    self.status = ChannelState(msg['params']['data']['event'])
                    if self.status in self.handlers:
                        self.handlers[self.status](msg)
                    if self.status == ChannelState.OPEN:
                        self.id = msg['params']['channel_id']
                if msg['method'] == 'channels.message' and ChannelState.MESSAGE in self.handlers:
                    self.handlers[ChannelState.MESSAGE](msg)
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

        :param accounts: a list of addresses to fetch the balances of.
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

        :param message: Message to be sent
        :param recipient: Address of the recipient
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

        :param amount: Amount of tokens to deposit
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

        :param amount: Amount of tokens to withdraw
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

    def update(self, from_addr, to_addr, amount):
        """
        Trigger a transfer update

        The transfer update is moving tokens from one channel account to another.
        The update is a change to be applied on top of the latest state.

        Sender and receiver are the channel parties. Both the initiator and responder
        can take those roles. Any public key outside of the channel is considered invalid.

        :param from_addr: Sender's public address
        :param to_addr: Receiver's public address
        :param amount: Transaction amount
        """
        self.__enqueue_action({
            'method': 'channels.update.new',
            'params': {
                'amount': amount,
                'from': from_addr,
                'to': to_addr
            }
        })

    def create_contract(self, code, call_data, deposit, vm_version, abi_version):
        """
        Trigger create contract update

        The create contract update is creating a contract inside the channel's internal state tree.
        The update is a change to be applied on top of the latest state.

        This creates a contract with the poster being the owner of it.
        Poster commits initially a deposit amount of tokens to the new contract.

        :param code: Api encoded compiled AEVM byte code
        :param call_data: Api encoded compiled AEVM call data for the code
        :param deposit: Initial amount the owner of the contract commits to it
        :param vm_version: Version of the AEVM
        :param abi_version: Version of the ABI
        """
        self.__enqueue_action({
            'method': 'channels.update.new_contract',
            'params': {
                'code': code,
                'call_data': call_data,
                'deposit': deposit,
                'vm_version': vm_version,
                'abi_version': abi_version
            }
        })

    def contract_from_onchain(self, call_data, contract_id, deposit):
        """
        Trigger create contract from on-chain contract

        The new_contract_from_onchain update is creating a contract inside the channel's internal state tree
        using on-chain contract as a reference.
        The update is a change to be applied on top of the latest state.

        This creates a contract with the poster being the owner of it.
        Poster commits initially a deposit amount of tokens to the new contract.

        :param call_data: Api encoded compiled AEVM call data for the code
        :param contract_id: Contract id of the on-chain contract
        :param deposit: Initial amount the owner of the contract commits to it
        """
        self.__enqueue_action({
            'method': 'channels.update.new_contract_from_onchain',
            'params': {
                'call_data': call_data,
                'contract': contract_id,
                'deposit': deposit
            }
        })

    def call_contract(self, amount, call_data, contract_id, abi_version):
        """
        Trigger call a contract update

        The call contract update is calling a preexisting contract inside the channel's
        internal state tree. The update is a change to be applied on top of the latest state.

        That would call a contract with the poster being the caller of it. Poster commits
        an amount of tokens to the contract.

        The call would also create a call object inside the channel state tree. It contains
        the result of the contract call.

        It is worth mentioning that the gas is not consumed, because this is an off-chain
        contract call. It would be consumed if it were a on-chain one. This could happen
        if a call with a similar computation amount is to be forced on-chain.

        :param amount: Amount the caller of the contract commits to it
        :param call_data: Api encoded compiled AEVM call data
        :param contract_id: Address of the contract to call
        :param abi_version: Version of the ABI
        """
        self.__enqueue_action({
            'method': 'channels.update.call_contract',
            'params': {
                'amount': amount,
                'call_data': call_data,
                'contract': contract_id,
                'abi_version': abi_version
            }
        })

    def call_contract_static(self, amount, call_data, contract_id, abi_version):
        """
        Call contract using dry-run

        In order to get the result of a potential contract call, one might need to
        dry-run a contract call. It takes the exact same arguments as a call would
        and returns the call object.

        The call is executed in the channel's state but it does not impact the state
        whatsoever. It uses as an environment the latest channel's state and the current
        top of the blockchain as seen by the node.

        :param amount: Amount the caller of the contract commits to it
        :param call_data: Api encoded compiled AEVM call data
        :param contract_id: Address of the contract to call
        :param abi_version: Version of the ABI
        """
        self.__enqueue_action({
            'method': 'channels.dry_run.call_contract',
            'params': {
                'amount': amount,
                'call_data': call_data,
                'contract': contract_id,
                'abi_version': abi_version
            }
        })

    def get_contract_call(self, caller, contract_id, exec_round):
        """
        Get contract call result

        The combination of a caller, contract and a round of execution determines the
        contract call. Providing an incorrect set of those results in an error response.

        :param caller: Address of contract caller
        :param contract_id: Address of the contract to call
        :param exec_round: Round when contract was called.
        """
        self.__channel_call('channels.get.contract_call', {
            'caller': caller,
            'contract': contract_id,
            'round': exec_round
        })

    def get_contract_state(self, contract_id):
        """
        Get contract latest state

        :param contract_id: Address of the contract
        """
        self.__channel_call('channels.get.contract', {
            'pubkey': contract_id
        })

    def clean_contract_calls(self):
        """
        Clean up all locally stored contract calls

        Contract calls are kept locally in order for the participant to be able to look them up.
        They consume memory and in order for the participant to free it - one can prune all messages.
        This cleans up all locally stored contract calls and those will no longer be available for
        fetching and inspection.
        """
        self.__enqueue_action({
            'method': 'channels.clean_contract_calls',
            'params': {}
        })

    def poi(self, accounts, contracts):
        """
         Get proof of inclusion

        If a certain address of an account or a contract is not found
        in the state tree - the response is an error.

        :param accounts: List of account addresses to include in poi
        :param contracts: List of contract addresses to include in poi
        """
        self.__channel_call('channels.get.poi', {
            'accounts': accounts,
            'contracts': contracts
        })

    def on(self, event, handler=None):
        """
        Register an event handler for state-channel events

        :param event: The event name. It can be any event registered in ChannelState.
                      Apart from events you can also add handlers for `message` and `error`.
        :param handler: The function that should be invoked to handle the
                        event. When this parameter is not given, the method
                        acts as a decorator for the handler function.
                        The handler should accept 1 positional param which will be the
                        JSON-RPC 2.0 message corresponding to the event.
        """
        def set_handler(handler):
            self.handlers[ChannelState(event)] = handler
            return handler

        if handler is None:
            return set_handler
        set_handler(handler)

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
    UPDATE = 'update'

    # For handling message and errors
    MESSAGE = 'message'
    ERROR = 'error'
