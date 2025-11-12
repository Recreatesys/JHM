from odoo import models, fields, api, _


class ResPartnerGroup(models.Model):
    _name = 'res.partner.group'
    _description = 'Contact Group'

    name = fields.Char('Group Name', required=True)
    contact_ids = fields.One2many('res.partner', 'group_id', string='Contacts')
    contact_count = fields.Integer(string="Contact Count", compute='_compute_contact_count')

    @api.depends('contact_ids')
    def _compute_contact_count(self):
        for group in self:
            group.contact_count = len(group.contact_ids)

    def action_view_contacts(self):
        self.ensure_one()
        return {
            'name': 'Contacts in Group',
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'view_mode': 'list,form',
            'domain': [('group_id', '=', self.id)],
            'context': {'default_group_id': self.id},
            'target': 'current',
        }