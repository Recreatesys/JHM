# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = "account.move"

    branch_type = fields.Selection(
        [('hong_kong', 'Hong Kong'),
         ('singapore', 'Singapore')],
        string="Branch"
    )
    show_update_fpos = fields.Boolean(
        string="Has Fiscal Position Changed", store=False)
