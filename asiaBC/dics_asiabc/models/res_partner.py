from datetime import date

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    parent_company_ids = fields.Many2many(
        'res.partner',
        'res_partner_parent_company_rel',
        'partner_id',
        'parent_id',
        string="Child Individual(As a Director)"
    )
    director_ids = fields.Many2many(
        'res.partner',
        'res_partner_director_rel',
        'company_id',
        'director_id',
        string="Directors",
        domain=[('is_company', '=', False)],
    )
    group_id = fields.Many2one('res.partner.group', string='Group')
    first_name = fields.Char(string="First Name")
    last_name = fields.Char(string="Last Name")
    director_name = fields.Char(string="Director Name")
    director_eff_date = fields.Date(string="Director effective date")
    nationality = fields.Char(string="Nationality")
    passport_exp_date = fields.Date(string="Passport Expiry Date")
    passport_no = fields.Char(string="Passport no.")
    is_director = fields.Boolean(string="Is he a director")
    instant_messaging = fields.Char(string="Instant Messaging")
    email2 = fields.Char(string="Email 2")
    asiaBC_hotline = fields.Char(string="AsiaBC Hotline")
    jurisdiction = fields.Char(string="Jurisdiction")
    agent = fields.Char(string="Agent")
    is_service_office = fields.Boolean(string="Serviced office")
    is_ird = fields.Boolean(string="IRD (Tax)")
    is_comsec = fields.Boolean(string="Comsec (CR+BR)")
    is_doc_scan = fields.Boolean(string="Scan Documents")
    is_bank_account = fields.Boolean(string="Bank Account")
    is_company_chop = fields.Boolean(string="Company Chop")
    chop_details = fields.Char(string="Chop Details")
    certificate_number = fields.Char(string="Certificate Number")
    CI = fields.Char(string="CI")
    BR = fields.Char(string="BR")
    contact_code= fields.Char(string="Contact Code")
    Registration_date = fields.Date(string="Registration Date")
    early_renewal_reminder = fields.Date(string="Early reminder for renewal")
    renewal_date = fields.Date(string="Renewal Date")
    other = fields.Char(string="Other")
    # name = fields.Char(string="Name",  store=True)
    director_company_count = fields.Integer(
        string='Company Count',
        compute='_compute_director_company_count',
        store=False
    )

    available_parent_ids = fields.Many2many(
        'res.partner',
        compute="_compute_available_parent_ids",
        store=False
    )

    shares_ids = fields.One2many('shares.document', 'partner_id',
                                      string='Shares Document')
    occupation = fields.Char(string="Occupation")
    certificate_number_com = fields.Char(string="Certificate Number")
    date_enter_member = fields.Date(string="Date Entered as a Member")
    date_acquired_shares = fields.Date(string="Date of Acquired Shares")
    disc_number_share_from = fields.Integer(string="Distinctive nos.of Shares from")
    disc_number_share_to = fields.Integer(string="Distinctive nos.of Shares to")
    share_no = fields.Char(string="No of Shares")
    cons_paid_currency = fields.Many2one('res.currency', string="Consideration Paid Currency")
    cons_paid_amount = fields.Float(string="Consideration Paid Amount", digits=(12, 2))
    com_remarks = fields.Text(string="Com Sec Remarks")
    cr_personal_login = fields.Text(string="CR Personal Login")
    password = fields.Text(string="Password")
    chinese_name = fields.Char(string='Chinese Name', store=True)
    group_status = fields.Selection(string="Group Status", selection=[
        ("Active", "Active"),
        ("Exprired", "Expired")
    ], store=True)




    @api.depends('parent_company_ids')
    def _compute_available_parent_ids(self):
        for rec in self:
            rec.available_parent_ids = rec.parent_company_ids

    @api.depends('director_ids')
    def _compute_director_company_count(self):
        for record in self:
            record.director_company_count = self.env['res.partner'].search_count([
                ('director_ids', 'in', record.id),
                ('is_company', '=', True)
            ])



    @api.onchange('name','first_name', 'last_name')
    def _onchange_first_name_last_name(self):
        if self.is_company:
            self.first_name = ''
            self.last_name = ''
        
        if self.first_name or self.last_name:
            self.name = f"{self.first_name or ''} {self.last_name or ''}".strip()

                

    @api.constrains('passport_exp_date', 'early_renewal_reminder', 'renewal_date')
    def _check_dates(self):
        for record in self:
            today = date.today()
            if record.passport_exp_date and record.passport_exp_date < today:
                raise ValidationError("Passport expiry date cannot be in the past.")
            if record.early_renewal_reminder and record.early_renewal_reminder < today:
                raise ValidationError("Early renewal reminder cannot be in the past.")
            if record.renewal_date and record.renewal_date < today:
                raise ValidationError("Renewal date cannot be in the past.")
