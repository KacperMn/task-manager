from functools import wraps
from django.shortcuts import get_object_or_404
from django.http import Http404
from .utils import get_desk_by_slug

def get_desk(view_func):
    """
    Decorator that retrieves a desk by slug and passes it to the view.
    Ensures the user has access to the desk.
    """
    @wraps(view_func)
    def _wrapped_view(request, desk_slug, *args, **kwargs):
        # Get the desk and verify access in one step
        desk = get_desk_by_slug(desk_slug, request.user)
        if not desk:
            raise Http404("Desk not found")
        # Pass the desk to the view function
        return view_func(request, desk, *args, **kwargs)
    return _wrapped_view