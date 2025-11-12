# -*- coding: utf-8 -*-
from odoo import api, models, fields


class SharesDocument(models.Model):
    _name = 'shares.document'
    _description = 'Shares Document'

    partner_id = fields.Many2one('res.partner', string='Partner')
    partner_share_id = fields.Many2one('res.partner', string='Partner')
    partner_contact_ids = fields.Many2many('res.partner', string='Partner',
                                         compute='_compute_partner_contact_ids', store=True)
    occupation = fields.Char(string="Occupation")
    date_enter_member = fields.Date(string="Date Entered as a Member")
    date_acquired_shares = fields.Date(string="Date of Acquired Shares")
    certificate_number_com = fields.Char(string="Certificate Number")
    disc_number_share_from = fields.Integer(string="Distinctive nos.of Shares from")
    disc_number_share_to = fields.Integer(string="Distinctive nos.of Shares to")
    share_no = fields.Char(string="No of Shares", compute='_compute_share_no', store=True)
    cons_paid_currency = fields.Many2one('res.currency',string="Consideration Paid Currency")
    cons_paid_amount = fields.Float(string="Consideration Paid Amount",digits=(12, 2))
    com_remarks = fields.Text(string="Com Sec Remarks")


    @api.depends('disc_number_share_from', 'disc_number_share_to')
    def _compute_share_no(self):
        for record in self:
            record.share_no = str(record.disc_number_share_to - record.disc_number_share_from+ 1)

    @api.depends('partner_id')
    def _compute_partner_contact_ids(self):
        for rec in self:
            partner_share_ids = rec.partner_id.shares_ids.mapped('partner_share_id').ids
            parent_companies = [i for i in rec.partner_id.parent_company_ids.ids if i not in partner_share_ids]
            rec.partner_contact_ids = parent_companies
