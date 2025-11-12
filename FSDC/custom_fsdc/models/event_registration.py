from odoo import models, fields,_

class EventRegistrationInherit(models.Model):
    _inherit = 'event.registration'

    def action_create_partner_from_registrants(self):
        new_contacts_created = False
        for record in self:
            if not record.email:
                continue
            existing_partner = self.env['res.partner'].search([('email', '=', record.email)],limit=1)
            if not existing_partner:
                partner = self.env['res.partner'].create({
                    'name': record.name,
                    'email': record.email,
                    'phone': record.phone,
                    'is_company': False,
                })
                record.partner_id = partner.id
                new_contacts_created = True
            else:
                record.partner_id = existing_partner.id
                new_contacts_created = False
        message = (
            _("Registrants were successfully created.")
            if new_contacts_created else
            _("No new registrants found. All were already created.")
        )
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'message': message,
                'next': {'type': 'ir.actions.act_window_close'}
            }
        }
