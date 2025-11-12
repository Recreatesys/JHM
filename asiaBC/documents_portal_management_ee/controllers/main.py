# -*- coding: utf-8 -*-

from odoo.addons.sign.controllers.main import Sign
from odoo import http
from odoo.http import request



class SignNoEmail(Sign):

    @http.route([
        '/sign/sign/<int:sign_request_id>/<token>',
        '/sign/sign/<int:sign_request_id>/<token>/<sms_token>'
    ], type='json', auth='public')
    def sign(self, sign_request_id, token, sms_token=False, signature=None, **kwargs):
        request.session['no_email'] = kwargs.get('no_email', False)
        result = super().sign(sign_request_id, token, sms_token=sms_token, signature=signature, **kwargs)
        return result

