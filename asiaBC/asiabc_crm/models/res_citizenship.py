from odoo import models, fields

class ResCitizenship(models.Model):
    _name = 'res.citizenship'
    _description = 'Citizenship'

    name = fields.Char(string="Citizenship", required=True)
    country_id = fields.Many2one('res.country', string="Related Country")
