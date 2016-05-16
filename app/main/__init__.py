from flask import Blueprint

main = Blueprint('main', __name__)

from . import views, errors
from ..models import Perssion


@main.app_context_processor
def inject_perssions():
    return dict(Perssion=Perssion)
