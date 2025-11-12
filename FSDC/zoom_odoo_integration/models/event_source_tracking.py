# -*- coding: utf-8 -*-
from odoo import models , fields




class EventSourceTracking(models.Model):
    _name = 'event.source.tracking'
    _description = 'Zoom Source Tracking for Event'

    event_id = fields.Many2one('event.event', string="Event", required=True, ondelete='cascade')
    utm_source_id = fields.Many2one('utm.source', string="UTM Source")
    tracking_link = fields.Char("Tracking Link")
    registration_count = fields.Integer("Registrations")
    visitor_count = fields.Integer("Visitors")
