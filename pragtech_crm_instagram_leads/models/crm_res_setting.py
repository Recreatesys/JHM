from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    insta_leads_create_as_opportunity = fields.Boolean(
        string="Create Leads as Opportunities for Instagram",
        config_parameter='crm.insta_leads_create_as_opportunity'
    )
