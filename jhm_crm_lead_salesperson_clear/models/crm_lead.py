from odoo import api, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # Clear salesperson on all incoming leads from external channels.
            # type defaults to 'lead' when not explicitly set.
            # type='opportunity' is intentionally excluded — salesperson
            # assignment on opportunities is managed manually by the team.
            if vals.get('type', 'lead') == 'lead':
                vals['user_id'] = False
        return super().create(vals_list)
