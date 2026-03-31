from odoo import api, fields, models

PROBABILITY_SELECTION = [
    ('10', '10%'),
    ('30', '30%'),
    ('50', '50%'),
    ('70', '70%'),
    ('90', '90%'),
    ('100', '100%'),
]


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    probability_select = fields.Selection(
        PROBABILITY_SELECTION,
        string='Probability',
    )

    # ── Probability sync ──────────────────────────────────────────────────────

    @api.onchange('probability_select')
    def _onchange_probability_select(self):
        self.probability = float(self.probability_select) if self.probability_select else 0.0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('probability_select'):
                vals['probability'] = float(vals['probability_select'])
        return super().create(vals_list)

    def write(self, vals):
        if 'probability_select' in vals:
            vals['probability'] = float(vals['probability_select']) if vals['probability_select'] else 0.0
        return super().write(vals)

    # ── Contact sync ──────────────────────────────────────────────────────────

    def action_sync_to_contact(self):
        self.ensure_one()
        if not self.partner_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'No Contact Linked',
                    'message': 'Please link a customer to this opportunity before syncing.',
                    'type': 'warning',
                    'sticky': False,
                },
            }

        partner = self.partner_id
        vals = {}

        # ── Same field name, compatible types ─────────────────────────────────
        if self.x_studio_gender:
            vals['x_studio_gender'] = self.x_studio_gender
        if self.x_studio_occupation:
            vals['x_studio_occupation'] = self.x_studio_occupation
        if self.x_studio_line_id:
            vals['x_studio_line_id'] = self.x_studio_line_id
        if self.x_studio_spouse_mobile:
            vals['x_studio_spouse_mobile'] = self.x_studio_spouse_mobile

        # ── Different field names, compatible types ───────────────────────────
        # Migration budget (Monetary → Monetary)
        if self.x_studio_migration_budget:
            vals['x_studio_migration_budget_1'] = self.x_studio_migration_budget
        # Spouse email
        if self.x_studio_spouse_email:
            vals['x_studio_email_spouse'] = self.x_studio_spouse_email
        # Visa program → new visa_program field on partner (same selection values)
        if self.x_studio_visa_program:
            vals['visa_program'] = self.x_studio_visa_program

        # ── Type mismatches: Selection → Char (write value as text) ──────────
        if self.x_studio_immigration_country:
            vals['x_studio_immigration_country'] = self.x_studio_immigration_country
        if self.x_studio_communication_channel:
            vals['x_studio_communication_channel'] = self.x_studio_communication_channel

        # ── New fields added to Contact by this module ────────────────────────
        if self.x_studio_background:
            vals['background'] = self.x_studio_background
        if self.x_studio_business_owner_or_management_grade:
            vals['business_owner_or_management_grade'] = self.x_studio_business_owner_or_management_grade
        if self.x_studio_b2b_engagement:
            vals['b2b_engagement'] = self.x_studio_b2b_engagement
        if self.x_studio_previous_visa_program:
            vals['previous_visa_program'] = self.x_studio_previous_visa_program
        if self.x_studio_higher_diploma_or_above:
            vals['higher_diploma_or_above'] = self.x_studio_higher_diploma_or_above

        # ── Many2one: Industry → industry_id (both → res.partner.industry) ───
        if self.x_studio_industry:
            vals['industry_id'] = self.x_studio_industry.id

        if vals:
            partner.write(vals)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Synced Successfully',
                'message': f'Data synced to contact: {partner.name}',
                'type': 'success',
                'sticky': False,
            },
        }
