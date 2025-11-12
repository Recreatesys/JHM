# -*- coding: utf-8 -*-
from odoo import models, fields

class CrmIndustryExperience(models.Model):
    _name = 'crm.industry.experience'
    _description = 'Years of Industry Experience'

    name = fields.Char(string="Experience (Years)", required=True)