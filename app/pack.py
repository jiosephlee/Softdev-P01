from app.models import Card
from random import sample

def get_pack(setName):
    n = [c for c in Card.query.filter_by(set_name=setName)]
    n = sample(n,10)
    return n
