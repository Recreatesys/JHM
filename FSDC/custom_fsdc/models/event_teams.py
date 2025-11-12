from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class EventTeams(models.Model):
    _name = 'event.teams'
    _description = 'Teams used for Event module'

    name = fields.Char(string="name", required=True)
    
