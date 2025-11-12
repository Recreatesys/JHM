from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    occupation_ids = fields.Many2many('res.partner.occupation',
                                      'res_partner_occupation_rel', 'partner_id', 'occupation_id', string="Past Occupations")
    chinese_name = fields.Char(string="Chinese Name", store=True)
    first_name = fields.Char(string="First Name", store=True)
    middle_name = fields.Char(string="Middle Name", store=True)
    last_name = fields.Char(string="Last Name", store=True)
    fax = fields.Char(string="Fax", store=True)
    best_reached_by = fields.Char(string='Best Reached By', store=True)
    name = fields.Char(index=True, default_export_compatible=True, compute='_compute_name', inverse='_inverse_name', store=True)
    area_of_study = fields.Char(string="Area of Study", store=True)
    continent = fields.Selection(string="Continent", selection=[
        ("South America", "South America"),
        ("Europe", "Europe"),
        ("SEA", "SEA"),
        ("APAC", "APAC"),
        ("Asia", "Asia"),
        ("North America", "North America"),
        ("Central America", "Central America"),
        ("Africa", "Africa"),
        ("Middle East", "Middle East")
    ], store=True)
    linkedin_id = fields.Char(string="Linkedin ID", store=True)
    direct_line_number = fields.Char(string='Direct Line No.', store=True)
    job_function = fields.Char(string="Job Function", store=True)
    job_seniority = fields.Char(string="Job Seniority", store=True)
    best_reached_by = fields.Char(string="Best Reached By", store=True)
    sectors = fields.Many2many(comodel_name='res.sectors', string='Sectors', store=True)
    committee_name_text = fields.Char(string="Name", store=True)
    committee_role_text = fields.Text(string="Role", store=True)
    board = fields.Char(string="Board", store=True)
    working_group_text = fields.Char(string="Working Group", store=True)
    contact_soure_text = fields.Char(string="Contact Source", store=True)
    marketing_consent = fields.Boolean(string="Marketing Consent", store=True)

    alternative_contact_point_email1 = fields.Char(string="Email (AC1)", store=True)
    alternative_contact_point_full_name1 = fields.Char(string="Full Name (AC1)", store=True)
    alternative_contact_point_job_title1 = fields.Char(string="Job Title (AC1)", store=True)
    alternative_contact_point_phone1 = fields.Char(string="Phone (AC1)", store=True)

    alternative_contact_point_email2 = fields.Char(string="Email (AC2)", store=True)
    alternative_contact_point_full_name2 = fields.Char(string="Full Name (AC2)", store=True)
    alternative_contact_point_job_title2 = fields.Char(string="Job Title (AC2)", store=True)
    alternative_contact_point_phone2 = fields.Char(string="Phone (AC2)", store=True)

    alternative_contact_email_address = fields.Char(string="Alternative Email Address", store=True)
    language = fields.Char(string="Preferred Language", store=True)

    fsdc_industry = fields.Many2many(comodel_name='res.industry', string='Industry', store=True)

    contact_type = fields.Selection(string="Contact Type", selection=[
        ("Business", "Business"),
        ("Student", "Student")
    ], store=True)


    @api.depends('first_name', 'last_name', 'middle_name')
    def _compute_name(self):
        for record in self:
            if record.is_company:
                record.name = ''
            else:
                record.name = f"{record.first_name or ''} {record.middle_name or ''} {record.last_name or ''}".strip()
    

    def _inverse_name(self):
        for record in self:
            if not record.is_company:
                names = record.name.split()
                if len(names) == 3:
                    record.first_name = names[0] if names else ''
                    record.last_name = names[-1] if len(names) > 1 else ''
                    record.middle_name = names[1] if names[1] else ''
                else:
                    record.first_name = names[0] if names else ''
                    record.last_name = names[-1] if len(names) > 1 else ''


    @api.model
    def create(self, vals):
        if vals.get('email'):
            self._check_unique_email(vals['email'])
        return super(ResPartnerInherit, self).create(vals)

    def write(self, vals):
        if vals.get('email'):
            for rec in self:
                rec._check_unique_email(vals['email'])
        return super(ResPartnerInherit, self).write(vals)

    def _check_unique_email(self, email):
        existing_record = self.env['res.partner'].search([
            ('email', '=', email),
            ('id', '!=', self.id)
        ],limit=1)
        if existing_record:
            raise ValidationError(_("A Partner with this email already exists: %s") % email)