from odoo import http
from odoo.http import request
from werkzeug.exceptions import Unauthorized, NotFound
from .cors import cors
from datetime import datetime

class CorsControllerBase(http.Controller):
    @cors('*')
    def dispatch(self, *args, **kwargs):
        if request.httprequest.path != '/api/login':
            token_str = request.httprequest.headers.get('Authorization').split(' ')[1]
            token = request.env['api.token'].sudo().search([('token', '=', token_str)], limit=1)
            if not token or datetime.now() > token.expiration_time:
                raise Unauthorized('Invalid or expired token.')
            request.uid = token.user_id.id
        return super().dispatch(*args, **kwargs)

class MyAPIController(CorsControllerBase):

    @http.route('/api/login', methods=['POST'], type='json', auth="none")
    def login(self, **kwargs):
        params = request.jsonrequest
        login, password = params.get('login'), params.get('password')
        if not request.session.db or not login or not password:
            raise Unauthorized('Invalid credentials')
        print("request session dtbasese %s" % request.session.db)
        uid = request.session.authenticate(request.session.db, login, password)
        if uid is not False:
            token = request.env['api.token'].sudo().create_token(uid)
            return {
                'status': 'Login success',
                'token': token,
                'uid': uid,
            }
        raise Unauthorized('Invalid credentials')

    @http.route('/api/logout', auth="none")
    def logout(self, **kwargs):
        token_str = request.httprequest.headers.get('Authorization').split(' ')[1]
        token = request.env['api.token'].sudo().search([('token', '=', token_str)], limit=1)
        if token:
            token.unlink()
            request.session.logout(keep_db=True)
        else:
            raise Unauthorized('Invalid token.')
        return {'status': 'logged out'}

    @http.route('/api/<string:model_name>', methods=['GET'], auth="none")
    def get_records(self, model_name, page=1, per_page=20, **kwargs):
        domain = kwargs.get('domain', [])
        order = kwargs.get('order', 'id desc')
        print("request uid",request.uid)
        fields = []
        records = request.env[model_name].sudo().search_read(domain,fields, limit=per_page, offset=(page-1)*per_page, order=order)
        return records

    @http.route('/api/<string:model_name>', methods=['POST'], type='json', auth="none", csrf=False)
    def create_record(self, model_name, **kwargs):
        data = request.jsonrequest
        record_id = request.env[model_name].sudo(request.uid).create(data).id
        return {**{'id': record_id},**data}

    @http.route('/api/<string:model_name>/<int:id>', methods=['PUT'], type='json', auth="none", csrf=False)
    def update_or_create_record(self, model_name, id, **kwargs):
        data = request.jsonrequest
        record = request.env[model_name].sudo(request.uid).search([('id', '=', id)])
        if record:
            record.write(data)
        else:
            record = request.env[model_name].sudo(request.uid).create(data)
        return {**{'id': record.id},**data}

    @http.route('/api/<string:model_name>/<int:id>', methods=['DELETE'], auth="none")
    def delete_record(self, model_name, id, **kwargs):
        record = request.env[model_name].sudo(request.uid).search([('id', '=', id)])
        if record:
            record.unlink()
        else:
            raise NotFound('No record found with the given id.')
        return {'status': 'deleted'}
