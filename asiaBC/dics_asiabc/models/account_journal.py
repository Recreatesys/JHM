# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountJournal(models.Model):
    _inherit = "account.journal"

    logo = fields.Binary(
        string="Logo"
    )
    street = fields.Char()
    street2 = fields.Char()
    city = fields.Char()
    state_id = fields.Many2one(
        "res.country.state",
        string='State',
        domain="[('country_id', '=?', country_id)]"
    )
    zip = fields.Char(
        change_default=True
    )
    country_id = fields.Many2one(
        'res.country',
        string='Country',
    )
    phone = fields.Char(
        string='Phone'
    )
    mobile = fields.Char(
        string='Mobile'
    )
    email = fields.Char(
        string='Email'
    )
    fax = fields.Char(
        string='Fax'
    )
    branch_type = fields.Selection(
        [('hong_kong', 'Hong Kong'),
         ('singapore', 'Singapore')],
        string="Branch"
    )
    qr_payme = fields.Binary(
        string='Payme'
    )
    qr_alipay = fields.Binary(
        string='Alipay'
    )
