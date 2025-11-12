# -*- coding: utf-8 -*-
from odoo import models, fields

class CrmSourceLocation(models.Model):
    _name = 'crm.source.location'
    _description = 'Source Location'

    name = fields.Char(string="Location Name", required=True)