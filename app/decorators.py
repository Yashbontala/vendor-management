# vendor_api/decorators.py

from django.http import HttpResponseForbidden

def superuser_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_superuser:
            return HttpResponseForbidden("You don't have permission to access this resource.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view
