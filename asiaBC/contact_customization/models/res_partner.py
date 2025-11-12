from datetime import date, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    mapped_partner_id = fields.Many2one('res.partner',string="Mapped Contact")
    mapped_partner_company_ids = fields.Many2many('res.partner', 'res_partner_company_rel', 'partner_id', 'email', string="Companies")
    registration_date = fields.Date(string="Registration Date")
    ptr_letter_date = fields.Date(string="PTR Letter Date")
    last_audit_report_ytd = fields.Date(string="Last Audit Report YTD")
    passport_exp_date = fields.Date(string="Passport Expiry Date")

    def write(self, vals):
        old_mapping = {}
        for partner in self:
            old_mapping[partner.id] = partner.mapped_partner_id.id if partner.mapped_partner_id else False
        res = super().write(vals)
        if 'mapped_partner_id' in vals:
            for rec in self:
                rec._update_partner_company_network(old_mapping.get(rec.id))
        return res

    @api.model
    def create(self, vals):
        partner = super().create(vals)
        if 'mapped_partner_id' in vals:
            partner._update_partner_company_network()
        return partner

    def unlink(self):
        for rec in self:
            mapped_contact = self.env['res.partner'].search([('mapped_partner_id', '=', rec.id)])
            mapped_contact.mapped_partner_company_ids = [(3, rec.parent_id.id)]
            return super().unlink()

    def _update_partner_company_network(self, old_mapped_partner_id=None):
        old_connected_partners_ids = set()
        all_old_partner_company_ids = set()

        if old_mapped_partner_id:
            old_partner = self.env['res.partner'].browse(old_mapped_partner_id)
            old_connected_partners_ids = set(partner.id for partner in self._collect_connected_partners(old_partner))

            for p in self._collect_connected_partners(old_partner):
                if p.parent_id:
                    all_old_partner_company_ids.add(p.parent_id.id)

        new_connected_partners_ids = set(partner.id for partner in self._collect_connected_partners(self))

        disconnected = old_connected_partners_ids - new_connected_partners_ids

        all_valid_company_ids = set()
        for p in self._collect_connected_partners(self):
            if p.parent_id:
                all_valid_company_ids.add(p.parent_id.id)
            all_valid_company_ids.update(p.mapped_partner_company_ids.ids)

        all_valid_company_ids -= all_old_partner_company_ids

        for partner in self.env['res.partner'].browse(list(disconnected)):
            to_remove = [cid for cid in partner.mapped_partner_company_ids.ids if cid not in all_valid_company_ids]
            for cid in to_remove:
                self.mapped_partner_company_ids = [(3, cid)]
            partner.mapped_partner_company_ids = [(3, self.parent_id.id)]

        for partner in self._collect_connected_partners(self):
            for cid in all_valid_company_ids:
                if cid not in partner.mapped_partner_company_ids.ids:
                    partner.mapped_partner_company_ids = [(4, cid)]

    def _collect_connected_partners(self, start):
        visited = set()
        to_visit = [start]
        while to_visit:
            current = to_visit.pop()
            if current.id in visited:
                continue
            visited.add(current.id)
            if current.mapped_partner_id and current.mapped_partner_id.id not in visited:
                to_visit.append(current.mapped_partner_id)
            reverse = self.env['res.partner'].search([('mapped_partner_id', '=', current.id)])
            for rev in reverse:
                if rev.id not in visited:
                    to_visit.append(rev)
        return self.env['res.partner'].browse(list(visited))
    
    @api.onchange('mapped_partner_id')
    def onchange_mapped_partner(self):
        for rec in self:
            if rec.mapped_partner_id and not rec.create_uid:
                rec.name = rec.mapped_partner_id.name
                rec.email = rec.mapped_partner_id.email
                rec.phone = rec.mapped_partner_id.phone
                rec.mobile = rec.mapped_partner_id.mobile
                rec.function = rec.mapped_partner_id.function
                rec.title = rec.mapped_partner_id.title

    def _cron_send_reminders(self):
        today = date.today()
        companies = self.search([])
        default_user = self.env['res.users'].search([('login', '=', 'admin')], limit=1)
        for rec in companies:
            user = rec.user_id or default_user
            if not user:
                continue
            if rec.registration_date:
                reminder_date = (rec.registration_date.replace(day=1) - timedelta(days=30))
                if reminder_date == today:
                    rec._create_reminder_activity(
                    'Registration Renewal Reminder',
                    user,
                    'contact_customization.email_template_registration_reminder'
                )
            if rec.ptr_letter_date:
                reminder_date = rec.ptr_letter_date + timedelta(days=30)
                if reminder_date == today:
                    rec._create_reminder_activity(
                        'PTR Letter Follow-up',
                        user,
                        'contact_customization.email_template_ptr_reminder'
                    )
            if rec.last_audit_report_ytd:
                reminder_date = rec.last_audit_report_ytd + timedelta(days=11 * 30)
                if reminder_date == today:
                    rec._create_reminder_activity(
                        'Audit Report Reminder',
                        user,
                        'contact_customization.email_template_audit_reminder'
                    )
            if rec.passport_exp_date:
                reminder_date = rec.passport_exp_date - timedelta(days=30)
                if reminder_date == today:
                    rec._create_reminder_activity(
                        'Passport Expiry Reminder',
                        user,
                        'contact_customization.email_template_passport_reminder'
                    )

    def _create_reminder_activity(self, summary, user, template_xml_id):
        """Creates activity + sends email + system notification"""
        activity_type = self.env.ref('mail.mail_activity_data_todo')
        self.env['mail.activity'].create({
            'activity_type_id': activity_type.id,
            'res_id': self.id,
            'res_model_id': self.env['ir.model']._get(self._name).id,
            'user_id': user.id,
            'summary': summary,
            'note': f'{summary} for {self.name}',
            'date_deadline': fields.Date.today(),
        })

        template = self.env.ref(template_xml_id, raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)
