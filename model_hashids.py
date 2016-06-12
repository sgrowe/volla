from django.http import Http404
from django.shortcuts import get_object_or_404
from hashids import Hashids


class HashidsMixin:
    hashids = Hashids()

    @property
    def hashid(self):
        return self.hashids.encode(self.id)

    @classmethod
    def decode_hashid_or_404(cls, hashid):
        try:
            decoded, = cls.hashids.decode(hashid)
            return decoded
        except ValueError:
            raise Http404

    @classmethod
    def get_by_hashid_or_404(cls, hashid, queryset=None):
        pk = cls.decode_hashid_or_404(hashid)
        queryset = cls if queryset is None else queryset
        return get_object_or_404(queryset, pk=pk)
