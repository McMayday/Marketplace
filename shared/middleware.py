from django.db.models import signals


def curry(_curried_func, *args, **kwargs):
    def _curried(*moreargs, **morekwargs):
        return _curried_func(*(args + moreargs), **dict(kwargs, **morekwargs))

    return _curried


class WhodidMiddleware(object):
    """
    Маркировка объекта изменившим пользователем.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method not in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            if hasattr(request, 'user') and request.user.is_authenticated:
                user = request.user
            else:
                user = None

            mark_whodid = curry(self.mark_whodid, user)
            signals.pre_save.connect(
                mark_whodid,
                dispatch_uid=(self.__class__, request),
                weak=False)

        response = self.get_response(request)

        signals.pre_save.disconnect(dispatch_uid=(self.__class__, request,))

        return response

    def mark_whodid(self, user, sender, instance, **kwargs):
        if not getattr(instance, 'created_by_id', None):
            instance.created_by = user
        if hasattr(instance, 'modified_by_id'):
            instance.modified_by = user
