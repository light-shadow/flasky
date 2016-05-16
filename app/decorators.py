from functools import wraps
from flask import abort
from flask.ext.login import current_user
from .models import Perssion


def perssion_required(perssion):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(perssion):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    return perssion_required(Perssion.ADMINISTER)(f)
