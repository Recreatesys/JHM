from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResSectors(models.Model):
    _name = 'res.sectors'
    _description = 'Sectors model for partners'

    name = fields.Char(string="name", required=True)
    
