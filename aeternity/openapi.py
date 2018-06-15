import re
import requests
import keyword
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
    skip_tags = set(["obsolete", "debug"])
    # openapi versions
    open_api_versions = ["2.0"]
    # type mapping
    oa2py_type = {
        "string": "str",
        "integer": "int",
        "boolean": "bool",
    }

    def __init__(self, url, url_internal=None):
        # load the openapi json file from the node
        self.api_def = requests.get(f"{url}/api").json()

        # check open_api_version
        if self.api_def.get('swagger', 'x') not in self.open_api_versions:
            raise OpenAPIException(f"Unsupported Open API specification version {self.api_def.get('swagger')}")
        self.version = self.api_def.get('info', {}).get('version')

        # regexp to convert method signature to snakecase
        first_cap_re = re.compile('(.)([A-Z][a-z]+)')
        all_cap_re = re.compile('([a-z0-9])([A-Z])')

        def p2s(name):
            s1 = first_cap_re.sub(r'\1_\2', name)
            return all_cap_re.sub(r'\1_\2', s1).lower()

        # prepare the baseurl
        base_path = self.api_def.get('basePath', '/')
        self.base_url = f"{url}{base_path}"
        if url_internal is None:
            # do not build internal endpoints
            self.skip_tags.append("internal")
        else:
            self.base_url_internal = f"{url_internal}{base_path}"

        # parse the api
        # definition of a field
        FieldDef = namedtuple("FieldDef", ["required", "type", "values", "minimum", "maximum", "default"])
        Param = namedtuple("Param", ["name", "raw", "pos", "field"])
        Resp = namedtuple("Resp", ["schema", "desc"])
        Api, self.api_methods = namedtuple("Api", ["name", "doc", "params", "responses", "endpoint", "http_method"]), []

        for query_path, path in self.api_def.get("paths").items():
            for m, func in path.items():
                # exclude the paths/method tagged with skip_tags
                if not self.skip_tags.isdisjoint(func.get("tags")):
                    continue
                # get if is an internal or external endpoint
                endpoint_url = self.base_url_internal if "internal" in func.get("tags", []) else self.base_url
                api = Api(
                    name=p2s(func['operationId']),
                    doc=func.get("description"),
                    params=[],
                    responses={},
                    endpoint=f"{endpoint_url}{query_path}",
                    http_method=m,

                )
                # collect the parameters
                for p in func.get('parameters', []):

                    param_name = p.get("name")
                    param_pos = p.get("in")
                    # check if the param name is a reserved keyword
                    if keyword.iskeyword(param_name):
                        if param_pos == 'path':
                            api.query_path = api.query_path.replace("{%s}" % param_name, "{_%s}" % param_name)
                        param_name = f"_{param_name}"

                    param = Param(
                        name=param_name,
                        raw=p.get("name"),
                        pos=param_pos,
                        field=FieldDef(
                            required=p.get("required"),
                            type=p.get("type", p.get("schema", {}).get("$ref")),
                            values=p.get("enum", []),
                            default=p.get("default"),
                            minimum=p.get("minimum"),
                            maximum=p.get("maximum"))
                    )
                    api.params.append(param)

                # responses
                for code, r in func.get('responses', {}).items():
                    api.responses[int(code)] = Resp(
                        desc=r.get("description"),
                        schema=r.get("schema", {"$ref": ""}).get("$ref",).replace("#/definitions/", "")
                    )
                # crete the method
                self._add_api_method(api)

    def _add_api_method(self, api):
        """add an api method to the client"""
        def api_method(*args, **kwargs):
            query_params = {}
            post_body = {}
            target_endpoint = api.endpoint
            for p in api.params:
                # get the value or default
                val, ok = self._get_param_val(kwargs, p)
                if not ok:
                    raise OpenAPIArgsException(f"missing required paramter {p.name}")
                # if none continue
                if val is None:
                    continue
                # check the type
                if p.field.type.startswith("#/definitions/"):
                    # TODO: validate the model
                    pass
                elif not self._is_valid_type(val, p.field):
                    raise OpenAPIArgsException(f"type error for paramter {p.name}, expected: {p.field.type} got {type(val).__name__}", )
                # check the ranges
                if not self._is_valid_interval(val, p.field):
                    raise OpenAPIArgsException(f"value error for paramter {p.name}, expected: {p.minimum} =< {val} =< {p.maximum}", )
                # check allowed walues
                if len(p.field.values) > 0 and val not in p.field.values:
                    raise OpenAPIArgsException(f"Invalid value for param {p.name}, allowed values are {','.join(p.values)}")
                # if in path substute
                if p.pos == 'path':
                    target_endpoint = target_endpoint.replace('{%s}' % p.name, str(val))
                # if in query add to the query
                if p.pos == 'query':
                    query_params[p.raw] = val
                if p.pos == 'body':
                    post_body = val
            # make the request
            if api.http_method == 'get':
                http_reply = requests.get(target_endpoint, params=query_params)
                api_response = api.responses.get(http_reply.status_code, None)
            else:
                http_reply = requests.post(target_endpoint, params=query_params, json=post_body)
                api_response = api.responses.get(http_reply.status_code, None)
                # TODO: only for debug
                # print(f">>>>method {target_endpoint} >> reply >> {http_reply.text}", )
            # unknown error
            if api_response is None:
                raise OpenAPIClientException(f"Unknown error {http_reply.status_code} - {http_reply.text}")
            # success
            if http_reply.status_code == 200:
                # parse the http_reply
                if len(api_response.schema) == 0:
                    return {}
                jr = http_reply.json()
                return namedtuple(api_response.schema, jr.keys())(**jr)
            # error
            raise OpenAPIClientException(f"Error: {api_response.desc}")
        # register the method
        api_method.__name__ = api.name
        api_method.__doc__ = api.doc
        setattr(self, api_method.__name__, api_method)
        self.api_methods.append(api)

    def _is_valid_interval(self, val, field):
        is_ok = True
        if not isinstance(val, int):
            return is_ok
        if field.minimum is not None and val < field.minimum:
            is_ok = False
        if field.maximum is not None and val > field.maximum:
            is_ok = False
        return is_ok

    def _is_valid_type(self, val, field):
        py_type = self.oa2py_type.get(field.type, "unknown")
        if py_type != type(val).__name__:
            return False
        return True

    def _get_param_val(self, params, param):
        """
        get the parameter "name" from the parmaters,
        raise an exception if the paramter is required and is None
        """
        val = params.get(param.name, param.field.default)
        val = val if val is not None else param.field.default
        # check required
        if param.field.required and val is None:
            return val, False
        return val, True

    def get_api_methods(self):
        """get the api methods registered by the client"""
        return self.api_methods

    def get_version(self):
        return self.version
