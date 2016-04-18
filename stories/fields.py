from rest_framework.serializers import Field, ValidationError
from hashids import Hashids

default_hashids = Hashids()


class HashidField(Field):
    def __init__(self, *args, **kwargs):
        self._hashids = kwargs.pop('hashids', default_hashids)
        super().__init__(*args, **kwargs)

    def to_representation(self, value):
        # from primary key to hash id
        return self._hashids.encode(value)

    def to_internal_value(self, data):
        # from hashid to primary key
        decoded_list = self._hashids.decode(data)
        if len(decoded_list) != 1:
            raise ValidationError
        return decoded_list[0]
