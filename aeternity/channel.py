import asyncio
import json

import namedtupled
import websockets

from aeternity import defaults


class Channel(object):
    """
    Create a state channel
    """

    def __init__(self, channel_options):
        """
        Initialize the Channel object

        Args:
            channel_options: dict containing chaneel options.

            channel_options contains/can contain following keys:

            channel_options.url (str) - Channel url (for example: "ws://localhost:3001")
            channel_options.role (str) - Participant role ("initiator" or "responder")
            channel_options.initiator_id (str) - Initiator's public key
            channel_options.responder_id (str) - Responder's public key
            channel_options.push_amount (int) - Initial deposit in favour of the responder by the initiator
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
                                                    as well as some special cases: opening a noise connection, mutual closing acknowledgement and
                                                    reestablishing an existing channel (default: 120000)
            [channel_options.timeout_initialized] (int) - the time frame the responder has to accept an incoming noise session.
                                                        Applicable only for initiator (default: timeout_accept's value)
            [channel_options.timeout_awaiting_open] (int) - The time frame the initiator has to start an outgoing noise session to the responder's node.
                                                            Applicable only for responder (default: timeout_idle's value)
            channel_options.sign (function) - Function which verifies and signs transactions
        """
        options_keys = {'sign', 'endpoint', 'url'}
        endpoint = channel_options.get('endpoint', defaults.CHANNEL_ENDPOINT)
        wsUrl = channel_options.get('url', defaults.CHANNEL_URL)
        self.sign = channel_options.get('sign', None)
        self.params = {k: channel_options[k] for k in channel_options.keys() if k not in options_keys}
        self.url = self.__channel_url(wsUrl, self.params, endpoint)
        self.params = namedtupled.map(self.params)

    def create(self):
        """
        Invoke to establish the websocket connection and initialize the state channel
        """
        asyncio.ensure_future(self.__start_ws())

    async def __start_ws(self):
        """
        Set up websocket and attach the message handler
        """
        async with websockets.connect(self.url) as websocket:
            self.ws = websocket
            await self.__message_handler()

    async def __message_handler(self):
        """
        Message handler for incoming messages
        """
        async for message in self.ws:
            print(message)
            msg = namedtupled.map(json.loads(message))
            if msg.method == f"channels.sign.{self.params.role}_sign":
                await self.__sign_channel_tx(msg.params.data.tx)

    def __channel_url(self, url, params, endpoint):
        """
        construct channel url using the given channel options
        """
        param_string = '&'.join('{!s}={!r}'.format(key, val) for (key, val) in params.items())
        return f"{url}/{endpoint}?{param_string}".replace("'", "")

    async def __channel_call(self, method, params):
        """
        Construct and send channel messages over the websocket
        """
        message = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params
        }
        await self.ws.send(json.dumps(message))

    def __trigger_channel_call(self, method, params):
        """
        Fire and forget channel call
        """
        asyncio.ensure_future(self.__channel_call(method, params))

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
        self.__trigger_channel_call('channels.get.balances', {'accounts': accounts})

    async def __sign_channel_tx(self, tx):
        """
        Sign the transactions received over channel by the provided sign method
        """
        signedTx = self.sign(tx)
        await self.__channel_call(f'channels.{self.params.role}_sign', {'tx': signedTx.tx})
