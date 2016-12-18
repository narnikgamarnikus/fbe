# coding: utf-8
from datetime import datetime
from .base import *


class Operation(Base):
    name = db.Column(db.String(50), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __repr__(self):
        return '<Operations %s>' % self.name
