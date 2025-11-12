# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    job_code_id = fields.Many2one('job.code', string='Job Code',)
    group_id = fields.Many2one('res.partner.group', string='Group',)
    contact_count = fields.Integer(string="Contacts in Group", compute='_compute_contact_count',store=True  )

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """ Fill group based on selected customer """
        if self.partner_id and self.partner_id.group_id:
            self.group_id = self.partner_id.group_id
        else:
            self.group_id = False

    @api.depends('group_id')
    def _compute_contact_count(self):
        for order in self:
            if order.group_id:
                order.contact_count = len(order.group_id.contact_ids)
            else:
                order.contact_count = 0

    def action_view_contacts_in_group(self):
        """ Open a list view of the contacts in the selected group """
        self.ensure_one()
        if not self.group_id:
            return False

        return {
            'name': 'Contacts in Group',
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'view_mode': 'list,form',
            'domain': [('group_id', '=', self.group_id.id)],
            'context': {'default_group_id': self.group_id.id},
            'target': 'current',
        }




# class SaleReport(models.Model):
#     _inherit = 'sale.report'
#
#     group_id = fields.Many2one('res.partner.group', string='Group', store=True)

