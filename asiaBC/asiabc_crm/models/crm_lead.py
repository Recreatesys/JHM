# -*- coding: utf-8 -*-
import html
from odoo import models, fields, api, _
import re
from html import unescape


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    whatsapp_no = fields.Text(string="Whatsapp Number")
    interested_in = fields.Text(string="Interested In")
    citizen_record_id = fields.Many2one(
        'res.citizenship',
        string="Citizenship",
    )
    citizenship_id = fields.Many2one(
        'res.country',
        string="Citizenship",
    )
    source_location_id = fields.Many2one(
        'crm.source.location',
        string="Source Location"
    )

    browser_id = fields.Many2one(
        'crm.browser',
        string="Browser",
    )

    business_type_id = fields.Many2one(
        'crm.business.type',
        string="Business Type",
    )

    ip_of_user = fields.Text(string="IP of the user")
    campaign_term = fields.Text(string="Campaign Term")
    campaign_content = fields.Text(string="Campaign Content")
    gclid = fields.Text(string="GCLID")

    annual_turnover_expected = fields.Text(
        string="Expected Annual Turnover(US$)",
    )
    years_of_experience_id = fields.Many2one(
        'crm.industry.experience',
        string="Years of Industry Experience",
    )
    nationality = fields.Char(string="Nationality")

    budget_expected = fields.Text(
        string="Expected Budget in Bank Account Opening(US$)",
    )

    @staticmethod
    def clean_html(html_text):
        """Remove HTML tags and replace <br> with new lines."""
        text = re.sub(r'<br\s*/?>', '\n', html_text)
        text = re.sub(r'<[^>]+>', '', text)
        return text.strip()

    @staticmethod
    def extract_same_line(text, keyword):
        """Extract the content from the same line after a specific keyword."""
        pattern = rf"{re.escape(keyword)}\s*(.*)"
        text = text.replace('&nbsp;', '')
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else ''

    @staticmethod
    def extract_next_line(text, keyword):
        """Extract the content from the same line or the next non-empty line after a keyword."""
        pattern = rf"{re.escape(keyword)}\s*(.*)"
        text = text.replace('&nbsp;', '')
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else ''


    @staticmethod
    def extract_ip_country(text):
        """Extract 'Country' from 'IP of the user' section if 'Location' is empty."""
        pattern = r"IP of the user:.*?\n.*?Country:\s*(.+)"
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else ''

    @api.model
    def message_new(self, msg_dict, custom_values=None):

        self = self.with_context(default_user_id=False)
        email_from = msg_dict.get('from')
        if custom_values is None:
            custom_values = {}
        defaults = {
            'name': msg_dict.get('subject') or _("No Subject"),
            'email_from': msg_dict.get('from'),
            'partner_id': msg_dict.get('author_id', False),
        }

        if msg_dict.get('priority') in dict(self.env['crm.lead']._fields['priority'].selection):
            defaults['priority'] = msg_dict.get('priority')

        raw_body = msg_dict.get('body', '')
        body = self.clean_html(raw_body)

        def extract_value(pattern, text):
            text = unescape(text.replace('&nbsp;', ' ')).strip()
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                result = match.group(1).strip()
                return result
            return ''


        if "=== Message (Optional): ===" in body:
            contact_name_pattern = r"=== From: ===\s*(.*?)\s*=== Email: ==="
            contact_name = extract_value(contact_name_pattern, body)

            email_pattern = r"=== Email: ===\s*(.*?)\s*=== WhatsApp number: ==="
            email_from = extract_value(email_pattern, body)

            whatsapp_pattern = r"=== WhatsApp number: ===\s*(.*?)\s*=== Interested in: ==="
            whatsapp_no = extract_value(whatsapp_pattern, body)

            interested_in_pattern = r"=== Interested in: ===\s*(.*?)\s*=== Existing company \(Optional\): ==="
            interested_in = extract_value(interested_in_pattern, body)
            if not interested_in:
                interested_in_pattern = r"=== Interested in: ===\s*(.*?)\s*=== Message \(Optional\): ==="
                interested_in = extract_value(interested_in_pattern, body)

            existing_company_pattern = r"=== Existing company \(Optional\): ===\s*(.*?)\s*=== Citizenship \(Optional\): ==="
            existing_company = extract_value(existing_company_pattern, body)

            citizenship_pattern = r"=== Citizenship \(Optional\): ===\s*(.*?)\s*=== Message \(Optional\): ==="
            citizenship = extract_value(citizenship_pattern, body)

            location_pattern = r"Location:\s*(.*?)\s*Browser:"
            location = extract_value(location_pattern, body)

            browser_pattern = r"Browser:\s*(.*?)\s*--"
            browser = extract_value(browser_pattern, body)

            ip_pattern = r"IP of the user:\s*(.*?)\s*Country:"
            ip_of_user = extract_value(ip_pattern, body)

            country_pattern = r"Country:\s*(.*?)\s*State or region:"
            country = extract_value(country_pattern, body)

            state_pattern = r"State or region:\s*(.*?)\s*City:"
            state = extract_value(state_pattern, body)

            city_pattern = r"City:\s*(.*?)\s*--"
            city = extract_value(city_pattern, body)

            campaign_name_pattern = r"Campaign Name:\s*(.*?)\s*(?=Campaign Source:)"
            campaign_name = extract_value(campaign_name_pattern, body)

            campaign_source_pattern = r"Campaign Source:\s*(.*?)\s*Campaign Medium:"
            campaign_source = extract_value(campaign_source_pattern, body)

            campaign_medium_pattern = r"Campaign Medium:\s*(.*?)\s*Campaign Term:"
            campaign_medium = extract_value(campaign_medium_pattern, body)

            campaign_term_pattern = r"Campaign Term:\s*(.*?)\s*Campaign Content:"
            campaign_term = extract_value(campaign_term_pattern, body)

            campaign_content_pattern = r"Campaign Content:\s*(.*?)\s*Gclid:"
            campaign_content = extract_value(campaign_content_pattern, body)
            gclid = self.extract_same_line(body, "Gclid:")

            message_start = body.find("=== Message (Optional): ===")
            if message_start != -1:
                message = body[message_start + len("=== Message (Optional): ==="):].strip()
                message = message.split('--')[1].strip()
                message = re.sub(r'<[^>]+>', '', message)
                message = unescape(message)
            else:
                message = ''

            browser_id = False
            campaign_id = False
            source_id = False
            medium_id = False


            if browser:
                browser_id = self.env['crm.browser'].sudo().search([('name', '=', browser)], limit=1)
                if not browser_id:
                    browser_id = self.env['crm.browser'].sudo().create({'name': browser})

            if campaign_name:
                campaign_id = self.env['utm.campaign'].sudo().search([('name', '=', campaign_name)], limit=1)
                if not campaign_id:
                    campaign_id = self.env['utm.campaign'].sudo().create({'name': campaign_name,
                                                                          'user_id': self.env.ref("base.user_admin").id})
            if campaign_source:
                source_id = self.env['utm.source'].sudo().search([('name', '=', campaign_source)], limit=1)
                if not source_id:
                        source_id = self.env['utm.source'].sudo().create({'name': campaign_source})
            if campaign_medium:
                medium_id = self.env['utm.medium'].sudo().search([('name', '=', campaign_medium)], limit=1)
                if not medium_id:
                    medium_id = self.env['utm.medium'].sudo().create({'name': campaign_medium})

            if citizenship:
                citizenship_record = self.env['res.citizenship'].sudo().search([('name', '=', citizenship)],
                                                                               limit=1)
                if not citizenship_record:
                    citizenship_record = self.env['res.citizenship'].sudo().create({'name': citizenship})
            else:
                citizenship_record = False

            country_id = self.env['res.country'].search([('name', '=', country)], limit=1)


            state_id = self.env['res.country.state'].search([('name', '=', state), ('country_id', '=', country_id.id)],
                                                            limit=1)

            if not state_id and country_id:
                state_id = self.env['res.country.state'].create({
                    'name': state,
                    'country_id': country_id.id,
                    'code': state
                })

            custom_values.update({
                'contact_name': contact_name,
                'email_from': email_from,
                'city': city,
                'state_id': state_id.id if state_id else False,
                'country_id': country_id.id if country_id else False,
                'partner_name': existing_company,
                'whatsapp_no': whatsapp_no,
                'interested_in': interested_in,
                'source_location_id': self.get_source_location_id(location) if location else False,
                'ip_of_user': ip_of_user,
                'browser_id': browser_id.id if browser_id else False,
                'campaign_id': campaign_id.id if campaign_id else False,
                'source_id': source_id.id if source_id else False,
                'medium_id': medium_id.id if medium_id else False,
                'citizen_record_id': citizenship_record.id if citizenship_record else False,
                'campaign_term': campaign_term,
                'campaign_content': campaign_content,
                'gclid': gclid,
            })

        elif "Message Box" in body:

            contact_name_pattern = r"Full Name\s*\(&amp;? Company Name If Any\)(.*?)\s*Business Type"
            contact_name_match = re.search(contact_name_pattern, body)
            contact_name = contact_name_match.group(1) if contact_name_match else ""

            business_type_pattern = r"Business Type(.*?)\s*Expected Annual Turnover"
            business_type_match = re.search(business_type_pattern, body)
            business_type = html.unescape(business_type_match.group(1).strip()) if business_type_match else ""

            annual_turnover_pattern = r"Expected Annual Turnover \(US\$\)\s*(.*?)\s*Years of Industry Experience"
            annual_turnover_match = re.search(annual_turnover_pattern, body)
            annual_turnover = annual_turnover_match.group(1) if annual_turnover_match else 0
            if annual_turnover:
                annual_turnover = annual_turnover.replace(',', '').replace('+', '')

            industry_experience_pattern = r"Years of Industry Experience(.*?)\s*Nationality"
            industry_experience_match = re.search(industry_experience_pattern, body)
            industry_experience = html.unescape(industry_experience_match.group(1).strip()) if industry_experience_match else ""

            nationality_pattern = r"Nationality(.*?)\s*Contact Email"
            nationality_match = re.search(nationality_pattern, body)
            nationality = nationality_match.group(1).strip() if nationality_match else ""

            email_from_pattern = r"Contact Email(.*?)\s*Mobile Number"
            email_from_match = re.search(email_from_pattern, body)
            email_from = email_from_match.group(1).strip() if email_from_match else ""

            mobile_number_pattern = r'Mobile Number[\s:]*([+\d\s]+)'
            mobile_match = re.search(mobile_number_pattern, body, re.IGNORECASE)

            mobile_number = ''
            if mobile_match:
                mobile_number = mobile_match.group(1).strip()
            remaining_text = body.replace(mobile_match.group(0), '').strip()

            budget_pattern = r'Estimated Budget in Bank Account Opening \(US\$\)\s*([\d,\.]+)'
            budget_match = re.search(budget_pattern, remaining_text)
            budget = ''
            if budget_match:
                budget = budget_match.group(1)
            if budget:
                budget = budget.replace(',', '').replace('+', '')

            success_rate_pattern = r'Predicted Success Rate\s*(\d+)'
            success_rate_match = re.search(success_rate_pattern, remaining_text)
            success_rate = ''
            if success_rate_match:
                success_rate = success_rate_match.group(1)
            gclid_pattern = r"GCLID(.*?)\s*Your trust and confidence in us are sincerely appreciated"
            gclid__match = re.search(gclid_pattern, body)
            gclid = gclid__match.group(1).strip() if gclid__match else ""

            message_start = body.find("Message Box")
            if message_start != -1:
                message_content = body[message_start + len("Message Box"):].strip()
                message_content = re.sub(r'<[^>]+>', '', message_content)
                message_content = unescape(message_content)
                message = message_content.split('GCLID')[0].strip()
            else:
                message = ''
            business_type_id = False
            years_of_experience_id = False

            if business_type:
                business_type_id = self.env['crm.business.type'].sudo().search([('name', '=', business_type)], limit=1)
                if not business_type_id:
                    business_type_id = self.env['crm.business.type'].sudo().create({'name': business_type})
            if industry_experience:
                years_of_experience_id = self.env['crm.industry.experience'].sudo().search([('name', '=', industry_experience)], limit=1)
                if not years_of_experience_id:
                    years_of_experience_id = self.env['crm.industry.experience'].sudo().create({'name': industry_experience})

            custom_values.update({
                'contact_name': contact_name,
                'business_type_id': business_type_id.id if business_type_id else False,
                'annual_turnover_expected': annual_turnover if annual_turnover else 0.0,
                'years_of_experience_id': years_of_experience_id.id if years_of_experience_id else False,
                'nationality': nationality,
                'email_from': email_from,
                'mobile': mobile_number,
                'budget_expected': budget if budget else 0.0,
                'probability': success_rate,
                'gclid': gclid,
            })

        defaults.update(custom_values)

        lead = super(CrmLead, self).message_new(msg_dict, defaults)
        if lead:
            lead.write({'email_from': email_from})
        if message:
            lead.message_post(body=message, subtype_xmlid='mail.mt_comment')
        return lead

    def get_source_location_id(self, location_name):
        """Fetch or create Source Location record."""
        source = self.env['crm.source.location'].search([('name', 'ilike', location_name)], limit=1)
        if not source:
            source = self.env['crm.source.location'].create({'name': location_name})
        return source.id if source else False
