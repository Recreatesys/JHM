# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import is_html_empty
from odoo.http import request
from datetime import date, datetime
from odoo.fields import Command
import json


class SignSendRequest(models.TransientModel):
    _inherit = 'sign.send.request'


    def _default_placeholder_mapped_ids(self):
        template = self.env['sign.template'].browse(self._context.get('active_id')).exists()
        if not template:
            return []
        type_ids = template.sign_item_ids.mapped('type_id').ids
        return [Command.create({'sign_item_type_id': type_id}) for type_id in type_ids]

    default_director_id = fields.Many2one('res.partner', string="Select Default Director")
    default_director_domain_ids = fields.Many2many('res.partner', compute='compute_default_director_domain')
    placeholder_mapped_ids = fields.One2many('customer.mapping', 'sign_send_request_id', string='Place Holder Mapping',default=_default_placeholder_mapped_ids)

    @api.onchange('partner_company_id')
    def onchange_partner_company_id(self):
        self.default_director_id = False
        self.placeholder_mapped_ids.director_id = False
        if self.partner_company_id:
            if self.signer_ids:
                self.signer_ids.partner_id = self.partner_company_id.id
            if self.signer_id:
                self.signer_id = self.partner_company_id.id

    @api.onchange('default_director_id')
    def onchange_default_director_id(self):
        if self.default_director_id:
            self.placeholder_mapped_ids.director_id = self.default_director_id.id
        else:
            self.placeholder_mapped_ids.director_id = False

    @api.depends('partner_company_id')
    def compute_default_director_domain(self):
        for record in self:
            if record.partner_company_id:
                partner_company_director_ids = record.partner_company_id.parent_company_ids.ids
                record.default_director_domain_ids = [(6, 0, partner_company_director_ids)]
            else:
                record.default_director_domain_ids = []

    def generate_document_without_mail(self):
        request.session['no_email'] = True
        requests = self.with_context(no_sign_mail=True).create_request()
        for sign_request in requests:
            placeholder_map = {}
            for mapping in self.placeholder_mapped_ids:
                sign_type = mapping.sign_item_type_id
                partner = mapping.director_id
                auto_field = sign_type.auto_field
                if sign_type and partner and auto_field:
                    value = getattr(partner, auto_field, "")
                    if isinstance(value, (date, datetime)):
                        value = value.isoformat()
                    placeholder_map[sign_type.name] = {
                        "auto_field": auto_field,
                        "value": value,
                    }
            sign_request.placeholder_director_map_json = json.dumps(placeholder_map)
        for signer in self.signer_ids:
            share_document = self.env['shares.document'].search([('partner_id', '=', self.partner_company_id.id),
                                                                 ('partner_share_id', '=', signer.partner_id.id)])
            if share_document:
                signer.partner_id.write({
                    'occupation': share_document.occupation,
                    'certificate_number_com': share_document.certificate_number_com,
                    'date_enter_member': share_document.date_enter_member,
                    'date_acquired_shares': share_document.date_acquired_shares,
                    'disc_number_share_from': share_document.disc_number_share_from,
                    'disc_number_share_to': share_document.disc_number_share_to,
                    'share_no': share_document.share_no,
                    'cons_paid_currency': share_document.cons_paid_currency.id,
                    'cons_paid_amount': share_document.cons_paid_amount,
                    'com_remarks': share_document.com_remarks,
                })
            else:
                signer.partner_id.write({
                    'occupation': False,
                    'certificate_number_com': False,
                    'date_enter_member': False,
                    'date_acquired_shares': False,
                    'disc_number_share_from': False,
                    'disc_number_share_to': False,
                    'share_no': False,
                    'cons_paid_currency': False,
                    'cons_paid_amount': False,
                    'com_remarks': False,
                })
        if self.activity_id:
            self._activity_done()
        if self._context.get('sign_all'):
            return requests.go_to_signable_document(requests.request_item_ids)
        return requests.go_to_signable_document()

    def sign_directly(self):
        request.session['no_email'] = False
        requests = self.with_context(no_sign_mail=False).create_request()
        for sign_request in requests:
            placeholder_map = {}
            for mapping in self.placeholder_mapped_ids:
                sign_type = mapping.sign_item_type_id
                partner = mapping.director_id
                auto_field = sign_type.auto_field
                if sign_type and partner and auto_field:
                    value = getattr(partner, auto_field, "")
                    if isinstance(value, (date, datetime)):
                        value = value.isoformat()
                    placeholder_map[sign_type.name] = {
                        "auto_field": auto_field,
                        "value": value,
                    }
            sign_request.placeholder_director_map_json = json.dumps(placeholder_map)
        for signer in self.signer_ids:
            share_document = self.env['shares.document'].search([('partner_id', '=', self.partner_company_id.id),
                                                                 ('partner_share_id', '=', signer.partner_id.id)])
            if share_document:
                signer.partner_id.write({
                    'occupation': share_document.occupation,
                    'certificate_number_com': share_document.certificate_number_com,
                    'date_enter_member': share_document.date_enter_member,
                    'date_acquired_shares': share_document.date_acquired_shares,
                    'disc_number_share_from': share_document.disc_number_share_from,
                    'disc_number_share_to': share_document.disc_number_share_to,
                    'share_no': share_document.share_no,
                    'cons_paid_currency': share_document.cons_paid_currency.id,
                    'cons_paid_amount': share_document.cons_paid_amount,
                    'com_remarks': share_document.com_remarks,
                })
            else:
                signer.partner_id.write({
                    'occupation': False,
                    'certificate_number_com': False,
                    'date_enter_member': False,
                    'date_acquired_shares': False,
                    'disc_number_share_from': False,
                    'disc_number_share_to': False,
                    'share_no': False,
                    'cons_paid_currency': False,
                    'cons_paid_amount': False,
                    'com_remarks': False,
                })
        if self.activity_id:
            self._activity_done()
        if self._context.get('sign_all'):
            return requests.go_to_signable_document(requests.request_item_ids)
        return requests.go_to_signable_document()


class SignRequest(models.Model):
    _inherit = "sign.request"

    placeholder_director_map_json = fields.Text('Placeholder-Director Map')

    def go_to_signable_document(self, request_items=None):
        """ go to the signable document as the signers for specified request_items or the current user"""
        self.ensure_one()
        if not request_items:
            request_items = self.request_item_ids.filtered(lambda r: not r.partner_id or (r.state == 'sent' and r.partner_id.id == self.env.user.partner_id.id))
        if not request_items:
            return
        return {
            'name': self.reference,
            'type': 'ir.actions.client',
            'tag': 'sign.SignableDocument',
            'context': {
                'id': self.id,
                'token': request_items[:1].sudo().access_token,
                'create_uid': self.create_uid.id,
                'state': self.state,
                'request_item_states': {item.id: item.is_mail_sent for item in self.request_item_ids},
                'template_editable': self.nb_closed == 0,
                'token_list': request_items[1:].sudo().mapped('access_token'),
                'name_list': [item.partner_id.name for item in request_items[1:]],
                'placeholder_director_map': json.loads(self.placeholder_director_map_json or '{}'),
            },
        }
