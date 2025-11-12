# -*- coding: utf-8 -*-
from odoo import models , fields, api




class ZoomAttendance(models.Model):
    _name = 'zoom.attendance'
    _description = 'Zoom Webinar Attendance'

    name = fields.Char()
    email = fields.Char()
    join_time = fields.Datetime()
    leave_time = fields.Datetime()
    duration = fields.Integer()
    event_id = fields.Many2one('event.event', string="Event", related='registration_id.event_id', store=True)
    registration_id = fields.Many2one('event.registration')
    status = fields.Char(string="Zoom Status")
    company_name = fields.Char(
        string='Company Name', compute='_compute_company_name', readonly=False, store=True)

    @api.depends('registration_id')
    def _compute_company_name(self):
        for rec in self:
            rec.company_name = rec.registration_id.organization if rec.registration_id else False
