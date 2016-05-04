from rest_framework import filters


def query_params_filter(param_name, field_name=None):
    """
    Filters objects by the given query param

    :type param_name: str
    :type field_name: str | None
    :param param_name: The name of the query parameter.
    :param field_name: The name of the field to filter by. This defaults to the param_name if not given.
    :return: filters.BaseFilterBackend
    """
    if field_name is None:
        field_name = param_name

    class QueryParamsFilterBackend(filters.BaseFilterBackend):

        def filter_queryset(self, request, queryset, view):
            value = request.query_params.get(param_name)
            if value is not None:
                kwargs = {field_name: value}
                queryset = queryset.filter(**kwargs)
            return queryset

    return QueryParamsFilterBackend
