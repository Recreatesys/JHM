from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
class AccountPaymentSend(models.TransientModel):
    _name = 'account.payment.send'
    _description = 'Send Payment Receipt Wizard'

    company_id = fields.Many2one('res.company', invisible=True)
    payment_ids = fields.Many2many('account.payment', string="Payments")
    mode = fields.Selection([('single', 'Single'), ('multi', 'Multiple')], default='single', invisible=True)
    enable_download = fields.Boolean(default=True, invisible=True)
    enable_send_mail = fields.Boolean(default=True, invisible=True)
    send_mail_readonly = fields.Boolean(default=False, invisible=True)
    send_mail_warning_message = fields.Html(invisible=True)
    display_mail_composer = fields.Boolean(default=True, invisible=True)
    mail_lang = fields.Char(invisible=True)
    checkbox_download = fields.Boolean("Download", default=True)
    checkbox_send_mail = fields.Boolean("Send Email", default=True)

    mail_partner_ids = fields.Many2many('res.partner', string="Recipients")
    mail_subject = fields.Char(string="Subject")
    mail_body = fields.Html(string="Body")
    mail_template_id = fields.Many2one('mail.template', string="Mail Template")
    mail_attachment_ids = fields.Many2many('ir.attachment', string="Attachments")

    notify_user_id = fields.Many2one('res.users', string="Notify User")
    activity_type_id = fields.Many2one('mail.activity.type', string="Activity Type")
    activity_deadline = fields.Date(string="Activity Deadline")

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_ids = self._context.get('active_ids', [])
        if 'payment_ids' in fields_list and active_ids:
            res['payment_ids'] = [(6, 0, active_ids)]
        return res

    def action_send_and_print(self):
        """Send email, print payment receipt, send internal notification, and schedule activity"""
        if not self.payment_ids:
            raise UserError(_("No payments selected"))

        report = self.env.ref('account.action_report_payment_receipt', raise_if_not_found=False)
        if not report:
            raise UserError(_("Payment receipt report not found. Please check the XML ID."))

        if self.checkbox_send_mail and not self.mail_template_id:
            raise UserError(_("Mail template is not set."))

        for payment in self.payment_ids:
            if not payment.exists():
                raise UserError(_("Payment %s does not exist or has been deleted") % payment.id)

            if self.checkbox_send_mail and self.mail_template_id:
                self.mail_template_id.send_mail(payment.id, force_send=True)

            if self.checkbox_download:
                pdf_content, _ = self.env['ir.actions.report']._render_qweb_pdf(
                    'account.action_report_payment_receipt', [payment.id]
                )
                filename = f'Payment_Receipt_{payment.name}.pdf'

                attachment = self.env['ir.attachment'].create({
                    'name': filename,
                    'type': 'binary',
                    'datas': base64.b64encode(pdf_content),
                    'res_model': 'account.payment',
                    'res_id': payment.id,
                    'mimetype': 'application/pdf'
                })
                if attachment:
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'download_and_close_wizard',
                        'params': {
                            'url': f'/web/content/{attachment.id}?download=true',
                        }
                    }
        return {'type': 'ir.actions.act_window_close'}


