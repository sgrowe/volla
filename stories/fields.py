from django.db import models
from hashids import Hashids

default_hashids = Hashids()


class HashidAutoField(models.AutoField):
    def __init__(self, *args, **kwargs):
        self.hashids = kwargs.pop('hashid', default_hashids)
        super().__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection, context):
        int_id = super().from_db_value(value, expression, connection, context)
        return self.hashids.encode(int_id)

    def get_prep_value(self, value):
        decoded = self.hashids.decode(value)
        if len(decoded) != 1:
            raise ValueError('The hashid {!r} did not decode to a single int, but instead to {!r}'.format(value, decoded))
        int_id = decoded[0]
        return super().get_prep_value(int_id)
