from odoo import models, fields

class CrmBrowser(models.Model):
    _name = 'crm.browser'
    _description = 'Browser'

    name = fields.Char(string="Browser Name", required=True)