# -*- coding: utf-8 -*-
from odoo import models, fields


class JobCode(models.Model):
    _name = 'job.code'
    _description = 'Job Code'

    name = fields.Char(string='Job Code')
