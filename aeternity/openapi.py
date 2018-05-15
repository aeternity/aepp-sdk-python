import json
import os
import re
import requests
from collections import namedtuple


class OpenAPICli(object):
    def __init__(self, specs_path, host="127.0.0.1", port="3013", secured=False):
        if not os.path.exists(specs_path):
            raise FileNotFoundError(f"Open api specification file not found: {specs_path}")
        with open(specs_path) as fp:
            data = json.load(fp)

        # regexp to convert method signature to snakecase
        first_cap_re = re.compile('(.)([A-Z][a-z]+)')
        all_cap_re = re.compile('([a-z0-9])([A-Z])')

        def c2s(name):
            s1 = first_cap_re.sub(r'\1_\2', name)
            return all_cap_re.sub(r'\1_\2', s1).lower()
        # prepare the baseurl
        protocol = "http"
        if secured:
            protocol = "https"
        # base api url
        self.base_url = f"{protocol}://{host}:{port}{data.get('basePath','/')}"
        # skip tags
        skip_tags = set(["obsolete", "internal", "debug", "dev", "internal"])
        # print(self.base_url)
        for k, path in data.get('paths').items():
            for m, func in path.items():
                if not skip_tags.isdisjoint(func.get('tags')):
                    continue
                desc = func.get("description")
                name = c2s(func['operationId'])

                # print(f"path {k}")
                # print(f"method {m}, op: {c2s(func['operationId'])}")

                def add_api_method(name, doc, method, path, params, responses):
                    def api_method(*args, **kwargs):
                        query_params = {}
                        target_path = path
                        for p in params:
                            val = kwargs.get(p.name)
                            # check required
                            if p.required and val is None:
                                m = f"missing required paramter {p.name}"
                                raise Exception(m)
                            # if none continue
                            if val is None:
                                continue
                            # if in path substute
                            if p.type == 'path':
                                target_path = target_path.replace('{%s}' % p.name, val)
                            # if in query add to the query
                            if p.type == 'query':
                                query_params[p.name] = val
                            # TODO: body param
                        # make the request
                        endpoint = f"{self.base_url}{target_path}"
                        reply = requests.get(endpoint, params=kwargs)
                        # get response object
                        resp = responses.get(reply.status_code)
                        # unknow error
                        if resp is None:
                            raise Exception("Unknown error %s" % resp)
                        # parse the reply
                        jr = reply.json()
                        # success
                        if reply.status_code == 200:
                            return namedtuple(resp.schema, jr.keys())(**jr)
                        # error
                        raise Exception(jr['reason'])

                    api_method.__name__ = name
                    api_method.__doc__ = doc

                    setattr(self, api_method.__name__, api_method)
                # collect the parameters
                Param, params = namedtuple("Param", ['name', 'required', 'type']), []
                for p in func.get('parameters', []):
                    params.append(Param(
                        name=p.get("name"),
                        required=p.get("required"),
                        type=p.get("in"))
                    )
                # responses
                Resp, resps = namedtuple("Resp", ['schema', 'desc']), {}
                for code, r in func.get('responses', {}).items():
                    print(r)
                    resps[int(code)] = Resp(
                        desc=r.get("description"),
                        schema=r.get("schema", {"$ref": "Success"}).get("$ref").replace("#/definitions/", "")
                    )
                # crete the method
                add_api_method(name, desc, m, k, params, resps)


if __name__ == '__main__':
    pub_key = os.environ.get('WALLET_PUB')
    priv_key = os.environ.get('WALLET_PRIV')
    node_url = os.environ.get('TEST_URL')
    oac = OpenAPICli("../assets/swagger/0.13.0.json", host=node_url.replace("https://", ""), secured=True, port=443)
    m = [method_name for method_name in dir(oac) if callable(getattr(oac, method_name))]
    for x in m:
        print(x)

    print(oac.get_account_balance(account_pubkey=pub_key, height=1000))
    print(oac.get_account_transactions(account_pubkey=pub_key, tx_encoding="rest"))
    oac.get_block_by_hash()
    oac.get_block_by_hash_deprecated()
    oac.get_block_by_height()
    oac.get_block_by_height_deprecated()
    oac.get_block_genesis()
    oac.get_block_latest()
    oac.get_block_pending()
    oac.get_header_by_hash()
    oac.get_header_by_height()
    oac.get_name()
    oac.get_peer_key()
    oac.get_top()
    oac.get_tx()
    oac.get_txs()
    oac.post_block()
    oac.post_tx()
    print(res)
