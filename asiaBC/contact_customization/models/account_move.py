import base64
from datetime import date, timedelta
from odoo import models, fields, _
from odoo.exceptions import ValidationError

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_payment_sent(self):
        self.ensure_one()
        invoice_ref = self.ref or self.name
        payments = self.env['account.payment'].search([('ref', '=', invoice_ref)])

        if not payments:
            raise ValidationError(_("No payment linked to this invoice."))

        template = self.env.ref('contact_customization.email_template_payment_receipt_custom', raise_if_not_found=False)
        mail_partner_ids = [self.partner_id.id] if self.partner_id else []
        mail_subject = ''
        mail_body = ''
        attachment_ids = []
        if template:
            payment = payments[0]
            mail_subject = template._render_template(
                template.subject, 'account.payment', [payment.id]
            )[payment.id]
            mail_body = template._render_field(
                'body_html', [payment.id]
            )[payment.id]

        pdf_content, _ = self.env['ir.actions.report']._render_qweb_pdf(
            'account.action_report_payment_receipt', [payment.id]
        )

        if pdf_content:
            attachment = self.env['ir.attachment'].create({
                'name': f'Payment_Receipt_{payment.name}.pdf',
                'type': 'binary',
                'datas': base64.b64encode(pdf_content),
                'res_model': 'account.payment',
                'res_id': payment.id,
                'mimetype': 'application/pdf',
            })
            attachment_ids = [attachment.id]

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'account.payment.send',
            'target': 'new',
            'context': {
                'active_ids': payments.ids,
                'default_payment_ids': [(6, 0, payments.ids)],
                'default_mail_template_id': template.id if template else False,
                'default_mail_partner_ids': [(6, 0, mail_partner_ids)],
                'default_mail_subject': mail_subject,
                'default_mail_body': mail_body or '',
                'default_mail_attachment_ids': [(6, 0, attachment_ids)],
            },
        }


    def _cron_send_payment_due_reminders(self):
        """Send payment due reminders 14 days after invoice issue date"""
        today = date.today()

        invoices = self.search([
            ('move_type', '=', 'out_invoice'),
            ('invoice_date', '!=', False),
        ])

        for inv in invoices:
            reminder_date = inv.invoice_date + timedelta(days=14)
            if reminder_date == today:
                inv._create_payment_due_reminder()

    def _create_payment_due_reminder(self):
        """Create activity + email + chatter notification"""
        user = self.user_id or self.env.user

        activity_type = self.env.ref('mail.mail_activity_data_todo')
        self.env['mail.activity'].create({
            'activity_type_id': activity_type.id,
            'res_id': self.id,
            'res_model_id': self.env['ir.model']._get(self._name).id,
            'user_id': user.id,
            'summary': 'Payment Due Reminder',
            'note': f'Payment is due for Invoice <b>{self.name}</b> — Amount: {self.amount_residual} {self.currency_id.name}',
            'date_deadline': fields.Date.today(),
        })
        template = self.env.ref('contact_customization.email_template_payment_due_reminder', raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)

