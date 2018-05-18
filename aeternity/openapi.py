import json
import os
import re
import requests
from collections import namedtuple


class OpenAPIArgsException(Exception):
    """Raised when there is an error in method arguments"""

    def __init__(self, message):
        self.message = message


class OpenAPIClientException(Exception):
    """Raised when there is an error executing requests"""

    def __init__(self, message):
        self.message = message


class OpenAPIException(Exception):
    """Raised when there is an error executing requests"""

    def __init__(self, message):
        self.message = message


class OpenAPICli(object):
    """
    Generates a Opena API client
    """
    # skip tags
    skip_tags = set(["obsolete", "internal", "debug", "internal"])
    # openapi versions
    open_api_versions = ["2.0"]

    def __init__(self, specs_path, host="127.0.0.1", port="3013", secured=False):
        if not os.path.exists(specs_path):
            raise FileNotFoundError(f"Open api specification file not found: {specs_path}")
        with open(specs_path) as fp:
            data = json.load(fp)
        # check open_api_version
        if data.get('swagger', 'x') not in self.open_api_versions:
            raise OpenAPIException(f"Unsupported Open API specification version {data.get('swagger')}")
        self.version = data.get('info', {}).get('version')

        # regexp to convert method signature to snakecase
        first_cap_re = re.compile('(.)([A-Z][a-z]+)')
        all_cap_re = re.compile('([a-z0-9])([A-Z])')

        def c2s(name):
            s1 = first_cap_re.sub(r'\1_\2', name)
            return all_cap_re.sub(r'\1_\2', s1).lower()

        # prepare the baseurl
        protocol = "https" if secured else "http"
        self.base_url = f"{protocol}://{host}:{port}{data.get('basePath','/')}"
        # parse the api
        Param = namedtuple("Param", ['name', 'required', 'pos', 'type', 'values', 'default', 'minimum', 'maximum'])
        Resp = namedtuple("Resp", ['schema', 'desc'])
        Api, self.api_methods = namedtuple('Api', ['name', 'doc', 'params', 'responses', 'query_path', 'http_method']), []
        for k, path in data.get('paths').items():
            for m, func in path.items():
                # exclude the paths/method tagged with skip_tags
                if not self.skip_tags.isdisjoint(func.get('tags')):
                    continue
                api = Api(
                    name=c2s(func['operationId']),
                    doc=func.get("description"),
                    params=[],
                    responses={},
                    query_path=k,
                    http_method=m
                )
                # collect the parameters
                for p in func.get('parameters', []):
                    api.params.append(Param(
                        name=p.get("name"),
                        required=p.get("required"),
                        pos=p.get("in"),
                        type=p.get("type"),
                        values=p.get("enum", []),
                        default=p.get("default"),
                        minimum=p.get("minimum"),
                        maximum=p.get("maximum"))
                    )
                # responses
                for code, r in func.get('responses', {}).items():
                    api.responses[int(code)] = Resp(
                        desc=r.get("description"),
                        schema=r.get("schema", {"$ref": "Success"}).get("$ref").replace("#/definitions/", "")
                    )
                # crete the method
                self._add_api_method(api)

    def _add_api_method(self, api):
        """add an api method to the client"""
        def api_method(*args, **kwargs):
            query_params = {}
            target_path = api.query_path
            for p in api.params:
                # TODO: check for unknown parameters
                # get the value or default
                val, ok = self._get_param_val(kwargs, p.name, p.default, p.required)
                if not ok:
                    raise OpenAPIArgsException(f"missing required paramter {p.name}")
                # if none continue
                if val is None:
                    continue
                # check the type
                if not p.type.startswith(type(val).__name__, 0, 3):
                    raise OpenAPIArgsException(f"type error for paramter {p.name}, expected: {p.type} got {type(val).__name__}", )
                # check the ranges
                if not self._is_valid_interval(val, p.minimum, p.maximum):
                    raise OpenAPIArgsException(f"value error for paramter {p.name}, expected: {p.minimum} =< {val} =< {p.maximum}", )
                # check allowed walues
                if len(p.values) > 0 and val not in p.values:
                    raise OpenAPIArgsException(f"Invalid value for param {p.name}, allowed values are {','.join(p.values)}")
                # if in path substute
                if p.pos == 'path':
                    target_path = target_path.replace('{%s}' % p.name, val)
                # if in query add to the query
                if p.pos == 'query':
                    query_params[p.name] = val
                # TODO: body param
            # make the request
            endpoint = f"{self.base_url}{target_path}"

            if api.http_method == 'get':
                http_reply = requests.get(endpoint, params=kwargs)
                # get response object
                api_response = api.responses.get(http_reply.status_code, None)
            else:
                raise OpenAPIException("not yet implemented")
            # unknow error
            if api_response is None:
                raise OpenAPIClientException(f"Unknown error {http_reply.status_code} - {http_reply.text}")
            # success
            if http_reply.status_code == 200:
                # parse the http_reply
                jr = http_reply.json()
                return namedtuple(api_response.schema, jr.keys())(**jr)
            # error
            raise OpenAPIClientException(f"Error: {api_response.desc}")
        # register the method
        api_method.__name__ = api.name
        api_method.__doc__ = api.doc
        setattr(self, api_method.__name__, api_method)
        self.api_methods.append(api)

    def _is_valid_interval(self, val, min_val, max_val):
        is_ok = True
        if not isinstance(val, int):
            return is_ok
        if min is not None and val < min:
            is_ok = False
        if max is not None and val > max:
            is_ok = False
        return is_ok

    def _get_param_val(self, params, name, default=None, required=False):
        """
        get the parameter "name" from the parmaters,
        raise an exception if the paramter is required and is None
        """
        val = params.get(name, default)
        val = val if val is not None else default
        # check required
        if required and val is None:
            return val, False
        return val, True

    def get_api_methods(self):
        """get the api methods registered by the client"""
        return self.api_methods

    def get_version(self):
        return self.version
