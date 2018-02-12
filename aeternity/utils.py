class ValidateClassMixin:
    validate_attr_not_none = None

    def assure_attr_not_none(self, attrname):
        if not hasattr(self, attrname) or getattr(self, attrname, None) is None:
            raise ValueError(f'You must specify `{attrname}` on {self.__class__}')

    def __init__(self):
        if self.__class__.validate_attr_not_none is not None:
            for attr in self.__class__.validate_attr_not_none:
                self.assure_attr_not_none(attr)
