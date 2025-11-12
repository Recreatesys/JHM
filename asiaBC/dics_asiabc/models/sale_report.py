# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class SaleReport(models.Model):
    _inherit = "sale.report"

    group_id = fields.Many2one('res.partner.group', string='Group', store=True)

    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res['group_id'] = "partner.group_id"
        return res

    def _group_by_sale(self):
        res = super()._group_by_sale()
        res += """,
               partner.group_id"""
        return res

