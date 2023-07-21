from odoo import models, fields, api
import secrets
from datetime import timedelta, datetime


class APIToken(models.Model):
    _name = 'api.token'

    token = fields.Char('Token', required=True, index=True)
    user_id = fields.Many2one('res.users', 'User', required=True)
    expiration_time = fields.Datetime('Expiration Time', required=True)

    @api.model
    def create_token(self, user_id):
        token = secrets.token_urlsafe(64)
        expiration_time = datetime.now() + timedelta(days=3)
        self.create({
            'token': token,
            'user_id': user_id,
            'expiration_time': expiration_time,
        })
        return token
