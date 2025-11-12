import re

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ResPartnerOccupation(models.Model):
    _name = 'res.partner.occupation'
    _description = 'Past Occupation Records'
    _rec_name = 'occupation'

    def year_selection(self):
        return [(str(year), str(year)) for year in range(1980, 2031)]

    occupation = fields.Char(string="Occupation")
    year_start = fields.Selection(selection= year_selection, string="Start Year", help="Start Date for period")
    year_end = fields.Selection(selection= year_selection, string="End Year", help="End Date for period")
    period = fields.Char(string="Period", compute="_compute_period", store=True)
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company)
    partner_company_id = fields.Many2one('res.partner', string="Partner Company", domain="[('is_company', '=',True)]")
    email = fields.Char(string="Email")
    phone = fields.Char(string="Phone")
    pa_name = fields.Char(string="PA's Name")
    pa_email = fields.Char(string="PA's Email")
    pa_phone = fields.Char(string="PA's Phone Number")
    pa_name_2 = fields.Char(string="PA's Name 2")
    pa_email_2 = fields.Char(string="PA's Email 2")
    pa_phone_2 = fields.Char(string="PA's Phone 2")

    @api.constrains('email', 'pa_email', 'pa_email_2')
    def _check_email_format(self):
        email_regex = r"[^@]+@[^@]+\.[^@]+"
        for record in self:
            if record.email and not re.match(email_regex, record.email):
                raise ValidationError("Please enter a valid Email address.")
            if record.pa_email and not re.match(email_regex, record.pa_email):
                raise ValidationError("Please enter a valid PA Email address.")
            if record.pa_email_2 and not re.match(email_regex, record.pa_email_2):
                raise ValidationError("Please Enter a valid PA Email Address.")

            if record.email:
                duplicates = self.search([
                    ('email', '=', record.email.strip()),
                    ('id', '!=', record.id)
                ])
                if duplicates:
                    raise ValidationError(f"The Email '{record.email}' is already used in another record.")

            if record.pa_email:
                duplicates = self.search([
                    ('pa_email', '=', record.pa_email.strip()),
                    ('id', '!=', record.id)
                ])
                if duplicates:
                    raise ValidationError(f"The PA's Email '{record.pa_email}' is already used in another record.")
            if record.pa_email_2:
                duplicates = self.search([
                    ('pa_email_2', '=', record.pa_email_2.strip()),
                    ('id', '!=', record.id)
                ])
                if duplicates:
                    raise ValidationError(f"The PA's Email '{record.pa_email_2}' is already used in another record.")


    @api.depends('year_start', 'year_end')
    def _compute_period(self):
        for rec in self:
            if rec.year_start and rec.year_end:
                rec.period = f"{rec.year_start} - {rec.year_end}"
            else:
                rec.period = ''

    @api.constrains('year_start', 'year_end')
    def _check_year_range(self):
        for rec in self:
            if rec.year_start and rec.year_end:
                if int(rec.year_end) < int(rec.year_start):
                    raise ValidationError("End Year must be greater than or equal to Start Year.")

    @api.constrains('phone','pa_phone','pa_phone_2')
    def check_phone_number(self):
        phone_regex = '^\+?[0-9\s\-\(\)]{7,20}$'
        for record in self:
            if record.phone and not re.match(phone_regex, record.phone):
                raise ValidationError("Please Enter a Valid Phone Number")
            if record.pa_phone and not re.match(phone_regex, record.pa_phone):
                raise ValidationError("Please Enter a Valid PA's  Phone Number")
            if record.pa_phone_2 and not re.match(phone_regex, record.pa_phone_2):
                raise ValidationError("Please Enter a Valid PA's Phone Number")


