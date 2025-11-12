from odoo import models, fields

class CrmBusinessType(models.Model):
    _name = 'crm.business.type'
    _description = 'Business Type'

    name = fields.Char(string="Business Type Name", required=True)