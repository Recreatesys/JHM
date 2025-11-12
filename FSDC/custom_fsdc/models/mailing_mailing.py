from odoo import models, fields

from datetime import timedelta

class MailingMailingInherit(models.Model):
    _inherit = 'mailing.mailing'

    def _cron_check_sent_not_opened(self):
        mail_template = self.env.ref(
            'custom_fsdc.mail_template_pre_event_reminder_7_days', raise_if_not_found=False
        )
        if not mail_template:
            return
        now = fields.Datetime.now()
        target_date = (now - timedelta(days=7)).date()

        day_start = fields.Datetime.to_datetime(str(target_date) + " 00:00:00")
        day_end = fields.Datetime.to_datetime(str(target_date) + " 23:59:59")

        sent_traces = self.env['mailing.trace'].search([
            ('trace_status', '=', 'sent'),
            ('sent_datetime', '>=', day_start),
            ('sent_datetime', '<=', day_end),
        ])

        for trace in sent_traces:
            already_opened = self.env['mailing.trace'].search_count([
                ('res_id', '=', trace.res_id),
                ('mass_mailing_id', '=', trace.mass_mailing_id.id),
                ('trace_status', '=', 'open'),
            ])
            if already_opened:
                continue
            registration = self.env['event.registration'].browse(trace.res_id)
            if registration.exists():
                mail_template.send_mail(registration.id, force_send=True)

