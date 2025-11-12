from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResIndustry(models.Model):
    _name = 'res.industry'
    _description = 'Industry model for partners'

    name = fields.Char(string="name", required=True)
    
