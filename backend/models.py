import uuid as _uuid
import time
import os
from datetime import datetime
from flask_login import UserMixin
from backend.extensions import db


def _gen_uuid7():
    """
    Generate a UUID v7 (time-ordered UUID, RFC 9562).
    Layout (128 bits):
      [0-47]   unix_ts_ms  — 48-bit millisecond timestamp
      [48-51]  ver         — 4-bit version = 7
      [52-63]  rand_a      — 12-bit random
      [64-65]  var         — 2-bit variant = 0b10
      [66-127] rand_b      — 62-bit random
    """
    ms = int(time.time() * 1000)
    rand_a = int.from_bytes(os.urandom(2), 'big') & 0x0FFF
    rand_b = int.from_bytes(os.urandom(8), 'big') & 0x3FFFFFFFFFFFFFFF
    uuid_int = (
        (ms << 80) |
        (0x7 << 76) |
        (rand_a << 64) |
        (0b10 << 62) |
        rand_b
    )
    return str(_uuid.UUID(int=uuid_int))


class Admin(UserMixin, db.Model):
    __tablename__ = 'admin'

    id           = db.Column(db.String(36), primary_key=True, default=_gen_uuid7)
    full_name    = db.Column(db.String(150), nullable=False)
    email        = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    opportunities = db.relationship('Opportunity', backref='admin', lazy=True)


class Opportunity(db.Model):
    __tablename__ = 'opportunity'

    id                  = db.Column(db.String(36), primary_key=True, default=_gen_uuid7)
    admin_id            = db.Column(db.String(36), db.ForeignKey('admin.id'), nullable=False)
    name                = db.Column(db.String(200), nullable=False)
    duration            = db.Column(db.String(100), nullable=False)
    start_date          = db.Column(db.String(50),  nullable=False)
    description         = db.Column(db.Text,        nullable=False)
    skills              = db.Column(db.Text,        nullable=False)
    category            = db.Column(db.String(50),  nullable=False)
    future_opportunities = db.Column(db.Text,       nullable=False)
    max_applicants      = db.Column(db.Integer,     nullable=True)
    created_at          = db.Column(db.DateTime,    default=datetime.utcnow)


class PasswordResetToken(db.Model):
    __tablename__ = 'password_reset_token'

    id         = db.Column(db.String(36), primary_key=True, default=_gen_uuid7)
    admin_id   = db.Column(db.String(36), db.ForeignKey('admin.id'), nullable=False)
    token      = db.Column(db.String(256), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used       = db.Column(db.Boolean, default=False)
