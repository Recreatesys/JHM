# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import is_html_empty
from odoo.http import request
from hashlib import sha256



class SignSendRequest(models.TransientModel):
    _inherit = 'sign.send.request'

    partner_company_id = fields.Many2one('res.partner', string="Company", domain=[('is_company', '=', True)])

    def generate_document_without_mail(self):
        request.session['no_email'] = True
        requests = self.with_context(no_sign_mail=True).create_request()
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

    def _send_completed_document(self):
        """ Send the completed document to signers and Contacts in copy with emails
        """
        self.ensure_one()
        if self.state != 'signed':
            raise UserError(_('The sign request has not been fully signed'))
        if not request.session.get('no_email'):
            self._check_senders_validity()

        if not self.completed_document:
            self._generate_completed_document()

        signers = [{'name': signer.partner_id.name, 'email': signer.signer_email, 'id': signer.partner_id.id} for signer in self.request_item_ids]
        request_edited = any(log.action == "update" for log in self.sign_log_ids)
        for sign_request_item in self.request_item_ids:
            if not request.session.get('no_email'):
                self._send_completed_document_mail(signers, request_edited, sign_request_item.partner_id, access_token=sign_request_item.sudo().access_token, with_message_cc=False, force_send=True)

        cc_partners_valid = self.cc_partner_ids.filtered(lambda p: p.email_formatted)
        for cc_partner in cc_partners_valid:
            if not request.session.get('no_email'):
                self._send_completed_document_mail(signers, request_edited, cc_partner)
        if cc_partners_valid:
            body = _("The mail has been sent to contacts in copy: ") + ', '.join(cc_partners_valid.mapped('name'))
            if not is_html_empty(self.message_cc):
                body += self.message_cc
            self.message_post(body=body, attachment_ids=self.attachment_ids.ids + self.completed_document_attachment_ids.ids)



class SignRequestItem(models.Model):
    _inherit = "sign.request.item"

    @api.constrains('signer_email')
    def _check_signer_email_validity(self):
        if not request.session.get('no_email'):
            super()._check_signer_email_validity()

    @api.depends('signer_email')
    def _compute_frame_hash(self):
        db_uuid = self.env['ir.config_parameter'].sudo().get_param('database.uuid')
        for sri in self:
            if not request.session.get('no_email'):
                if sri.partner_id:
                    sri.frame_hash = sha256((sri.signer_email + db_uuid).encode()).hexdigest()
                else:
                    sri.frame_hash = ''
            else:
                sri.frame_hash = ''
