# -*- coding: utf-8 -*-
from odoo import api, models, fields


class SharesDocument(models.Model):
    _inherit = 'shares.document'

    @api.model
    def create(self, vals):
        res = super(SharesDocument, self).create(vals)
        try:
            res.partner_share_id.write({
                'occupation': res.occupation,
                'certificate_number_com': res.certificate_number_com,
                'date_enter_member': res.date_enter_member,
                'date_acquired_shares': res.date_acquired_shares,
                'disc_number_share_from': res.disc_number_share_from,
                'disc_number_share_to': res.disc_number_share_to,
                'share_no': res.share_no,
                'cons_paid_currency': res.cons_paid_currency.id,
                'cons_paid_amount': res.cons_paid_amount,
                'com_remarks': res.com_remarks,
            })
        except Exception as e:
            print(e)
        return res

    @api.model
    def write(self, vals):
        res = super(SharesDocument, self).write(vals)
        try:
            self.partner_share_id.write({
                'occupation': self.occupation,
                'certificate_number_com': self.certificate_number_com,
                'date_enter_member': self.date_enter_member,
                'date_acquired_shares': self.date_acquired_shares,
                'disc_number_share_from': self.disc_number_share_from,
                'disc_number_share_to': self.disc_number_share_to,
                'share_no': self.share_no,
                'cons_paid_currency': self.cons_paid_currency.id,
                'cons_paid_amount': self.cons_paid_amount,
                'com_remarks': self.com_remarks,
            })
        except Exception as e:
            print(e)
        return res
