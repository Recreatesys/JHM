# -*- coding: utf-8 -*-
from odoo import models, fields, api


class EventRegistration(models.Model):
    _inherit = "event.registration"

    job_title = fields.Char(string="Job Title")
    organization = fields.Char(string="Organization")
    registration_date = fields.Datetime(string="Registration Date")

    @api.model
    def _update_mail_schedulers(self):
        if self.env.context.get('event_skip_mail_schedulers'):
            return
        super()._update_mail_schedulers()
