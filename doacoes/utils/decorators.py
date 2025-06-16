from django.http import HttpResponseForbidden

def user_is(tipo):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if hasattr(request.user, 'perfil') and request.user.perfil.tipo == tipo:
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("Acesso negado.")
        return _wrapped_view
    return decorator
