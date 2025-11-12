from odoo import models, fields, api
from datetime import datetime, date, timedelta
import xlsxwriter
import io
import logging

_logger = logging.getLogger(__name__)


class EventEventInherit(models.Model):
    _inherit = 'event.event'

    is_free_event = fields.Boolean(string="Is Free Event", compute="_compute_is_free_event", store=True)
    is_post_event_mail_sent = fields.Boolean(string="Is Post Event Mail Sent", default=False)
    one_pager_image_link = fields.Char(string="One Pager (JPG Image Link from Website)")
    research_paper_link = fields.Char(string="Online PDF Link from Website")
    webinar_recording_link = fields.Char(string="Webinar Recording (Youtube Link)")
    event_type = fields.Selection(string='Event Type', selection=[
        ('MP', 'MP'),
        ('Duty Visit', 'Duty Visit')
    ], store=True)
    count_in_qa_paper = fields.Selection(string='Count in Q&A paper', selection=[
        ('Y', 'Y'),
        ('N', 'N')
    ], store=True)
    count_in_lego_questions = fields.Selection(string="Count in Lego Question", selection=[
        ('Y', 'Y'),
        ('Y - Duty Visit', 'Y - Duty Visit'),
        ('N - Same Duty Visit', 'N - Same Duty Visit')
    ], store=True)
    target_audience = fields.Selection(string="Target Audience", selection=[
        ('Local Audience', 'Local Audience'),
        ('Mainland or International Audience', 'Mainland or International Audience')
    ], store=True)

    event_chinese_name = fields.Char(string="Event Name (Chinese)", store=True)
    event_location = fields.Char(string="Location", store=True)
    event_chinese_location = fields.Char(string="Location (Chinese)", store=True)
    organising_district = fields.Char(string="Organising Disctrict", store=True)
    organising_district_chinese = fields.Char(string="Organising Disctrict (Chinese)", store=True)

    year = fields.Char(string="Year", store=True)

    event_representatives = fields.Char(string="FSDC Representatives", store=True)
    new_relationships = fields.Selection(string='New Relationships', selection=[
        ('Y', 'Y'),
        ('N', 'N')
    ], store=True)
    existing_relationship = fields.Selection(string="Existing Relationships", selection=[
        ('Y', 'Y'),
        ('N', 'N')
    ], store=True)
    regulatory = fields.Selection(string="Govt & Regulatory (Y)", selection=[
        ('Y', 'Y'),
        ('N', 'N')
    ], store=True)
    teams = fields.Many2many(comodel_name="event.teams", string="Teams", store=True)
    zoom_meeting_link = fields.Char(string="Zoom Meeting Link")


    @api.onchange('date_begin')
    def _compute_year(self):
        for event in self:
            if event.date_begin:
                year, month = event.date_begin.year, event.date_begin.month
                if month < 3:
                    event.year = f'{year-1}/{year}'
                else:
                    event.year = f'{year}/{year+1}'


    @api.depends('event_ticket_ids')
    def _compute_is_free_event(self):
        for event in self:
            event.is_free_event = not any (ticket.price > 0.0 for ticket in event.event_ticket_ids)

    def _cron_send_daily_free_event_mails(self):
        today = fields.Date.today()
        domain = [('is_free_event', '=', True),
                  ('date_end', '>=', fields.Datetime.now())]
        free_events = self.search(domain)
        if not free_events:
            return
        event_details = []
        for event in free_events:
            total_registrations = self.env['event.registration'].search_count([('event_id', '=', event.id)])
            today_total_registrations = self.env['event.registration'].search_count([('event_id', '=', event.id),
                                        ('create_date', '>=', datetime.combine(today, datetime.min.time())),
                                        ('create_date','<=', datetime.combine(today, datetime.max.time()))
                                        ])
            event_details.append({
                'name': event.name,
                'total_registrations': total_registrations,
                'today_total_registrations': today_total_registrations,
            })
        template = self.env.ref('custom_fsdc.email_template_daily_free_events')
        ctx = {
            'default_event_data': event_details,
            'default_today_date': today.strftime('%Y-%m-%d'),
        }
        template.with_context(ctx).send_mail(self.env.user.id, force_send=True)

    def send_total_registration_email(self):
        today = datetime.now().date()
        start = datetime.combine(today, datetime.min.time())
        end = datetime.combine(today, datetime.max.time())

        domain = [('is_free_event', '=', False),
                  ('date_end', '>=', fields.Datetime.now())]
        events = self.search(domain)
        template = self.env.ref('custom_fsdc.email_template_event_summary')

        for event in events:
            new_regs = self.env['event.registration'].search_count([
                ('event_id', '=', event.id),
                ('create_date', '>=', start),
                ('create_date', '<=', end)
            ])
            total_regs = self.env['event.registration'].search_count([
                ('event_id', '=', event.id)
            ])
            ctx = {
                'name': event.name,
                'new_regs': new_regs,
                'total_regs': total_regs,
            }
            template.with_context(ctx).send_mail(self.env.user.id, force_send=True)

    def _cron_send_absentees_mails(self):
        domain = [('date_end', '<=', fields.Datetime.now()),('is_post_event_mail_sent', '=', False)]
        past_events = self.search(domain)
        zoom_emails = self.env['zoom.attendance'].search([
            ('event_id', 'in', past_events.ids)
        ]).mapped('email')
        absentees_template = self.env.ref('custom_fsdc.email_template_absentees_mail')
        thankyou_template = self.env.ref('custom_fsdc.email_template_thankyou_mail')
        for event in past_events:
            for reg in event.registration_ids:
                if reg.state == 'cancel':
                    # Cancelled → absentee
                    if absentees_template:
                        absentees_template.send_mail(reg.id, force_send=True)

                elif reg.state == 'done' or reg.email in zoom_emails:
                    # Attended (either manually marked or Zoom attendance) → thank you
                    if thankyou_template:
                        thankyou_template.send_mail(reg.id, force_send=True)

                elif reg.state == 'open' and reg.email not in zoom_emails:
                    # Registered but didn’t attend → absentee
                    if absentees_template:
                        absentees_template.send_mail(reg.id, force_send=True)

                event.is_post_event_mail_sent = True

    def _cron_send_pre_event_reminder(self):
        now = fields.Datetime.now()
        target_time = now + timedelta(hours=1)

        window_start = target_time - timedelta(minutes=1)
        window_end = target_time + timedelta(minutes=1)
        event_reminder_template = self.env.ref('custom_fsdc.mail_template_pre_event_reminder')
        domain = [
            ('date_begin', '>=', window_start),
            ('date_begin', '<=', window_end),
        ]
        events = self.search(domain)
        for event in events:
            for reg in event.registration_ids:
                event_reminder_template.send_mail(reg.id, force_send=True)

    def _cron_send_pre_event_reminder_2_days(self):
        now = fields.Datetime.now()
        target_date = (now + timedelta(days=2)).date()

        day_start = fields.Datetime.to_datetime(str(target_date) + " 00:00:00")
        day_end = fields.Datetime.to_datetime(str(target_date) + " 23:59:59")
        event_reminder_template = self.env.ref('custom_fsdc.mail_template_pre_event_reminder_2_days')
        domain = [
            ('date_begin', '>=', day_start),
            ('date_begin', '<=', day_end),
        ]
        events = self.search(domain)
        for event in events:
            for reg in event.registration_ids:
                event_reminder_template.send_mail(reg.id, force_send=True)

   
    def get_xlsx_report(self, data, response):

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()

        only_border = workbook.add_format({"border": 1})

        if data['type'] == 'MP':
            # Header for the report
            sheet.write('A1', 'Year', only_border)
            sheet.write('B1', 'Date', only_border)
            sheet.write('C1', 'Type', only_border)
            sheet.write('D1', 'Count in Q&A paper - operations', only_border)
            sheet.write('E1', 'Count in Lego Questions', only_border)
            sheet.write('F1', 'Event/Activities', only_border)
            sheet.write('G1', '活動', only_border)
            sheet.write('H1', 'Location', only_border)
            sheet.write('I1', '地區', only_border)
            sheet.write('J1', 'Organising District', only_border)
            sheet.write('K1', '舉辦地', only_border)
            sheet.write('L1', 'Target audience', only_border)

            col_length = [10, 10, 10, 31, 23, 16, 10, 8, 10, 20, 10, 15]
            row = 2
            for index in range(len(data['vals']['name'])):
                sheet.write(f'A{row}', data['vals']['year'][index] or '', only_border)
                sheet.write(f'B{row}', data['vals']['date'][index] or '', only_border)
                sheet.write(f'C{row}', data['vals']['Type'][index] or '', only_border)
                sheet.write(f'D{row}', data['vals']['Count_QA'][index] or '', only_border)
                sheet.write(f'E{row}', data['vals']['Count_Lego'][index] or '', only_border)
                sheet.write(f'F{row}', data['vals']['name'][index] or '', only_border)
                sheet.write(f'G{row}', data['vals']['chinese_name'][index] or '', only_border)
                sheet.write(f'H{row}', data['vals']['location'][index] or '', only_border)
                sheet.write(f'I{row}', data['vals']['location_chinese'][index] or '', only_border)
                sheet.write(f'J{row}', data['vals']['organising_district'][index] or '', only_border)
                sheet.write(f'K{row}', data['vals']['organising_district_chinese'][index] or '', only_border)
                sheet.write(f'L{row}', data['vals']['target_audience'][index] or '', only_border)

                col_length[0] = max(col_length[0], len(data['vals']['year'][index] or ''))
                col_length[1] = max(col_length[1], len(data['vals']['date'][index] or ''))
                col_length[2] = max(col_length[2], len(data['vals']['Type'][index] or ''))
                col_length[3] = max(col_length[3], len(data['vals']['Count_QA'][index] or ''))
                col_length[4] = max(col_length[4], len(data['vals']['Count_Lego'][index] or ''))
                col_length[5] = max(col_length[5], len(data['vals']['name'][index] or ''))
                col_length[6] = max(col_length[6], len(data['vals']['chinese_name'][index] or ''))
                col_length[7] = max(col_length[7], len(data['vals']['location'][index] or ''))
                col_length[8] = max(col_length[8], len(data['vals']['location_chinese'][index] or ''))
                col_length[9] = max(col_length[9], len(data['vals']['organising_district'][index] or ''))
                col_length[10] = max(col_length[10], len(data['vals']['organising_district_chinese'][index] or ''))
                col_length[11] = max(col_length[11], len(data['vals']['target_audience'][index] or ''))

                row += 1

            for col in range(12):
                sheet.set_column(f'{chr(65 + col)}:{chr(65 + col)}', col_length[col])
        
        else:

            
            merge_format = workbook.add_format(
                {
                    "align": "center",
                    "valign": "vcenter",
                    "border": 1
                }
            )
            date_range_format = workbook.add_format(
                {
                    "bold": 1,
                    "font_color":"#0070c0",
                    "font_size": 13
                }
            )

            title_format = workbook.add_format(
                {
                    "bold": 1,
                    "font_size": 20,
                    "border": 1
                }
            )
            bold = workbook.add_format({"bold": True, "border": 1})

            sheet.write('A1', 'Industry Outreach and Engagement Meetings', title_format)
            sheet.write('A2', f"{data['vals']['start_date']} - {data['vals']['end_date']}", date_range_format)

            sheet.merge_range('G2:I2', "Industry Engagement", merge_format)
            sheet.write('A3', 'Meetings', bold)
            sheet.write('B3', 'Date', bold)
            sheet.write('C3', 'Company', bold)
            sheet.write('D3', 'Location', bold)
            sheet.write('E3', 'FSDC Representatives', bold)
            sheet.write('F3', 'Teams', bold)
            sheet.write('G3', 'New relationships', bold)
            sheet.write('H3', 'Existing relationships, New ideas', bold)
            sheet.write('I3', 'Govt & Regulatory (Y)', bold)

            col_length = [20, 20, 20, 20, 20, 20, 20, 40, 20]
            row = 4
            for index in range(len(data['vals']['name'])):
                sheet.write(f'A{row}', data['vals']['name'][index] or '', only_border)
                sheet.write(f'B{row}', data['vals']['date'][index] or '', only_border)
                sheet.write(f'C{row}', data['vals']['organizer'][index] or '', only_border)
                sheet.write(f'D{row}', data['vals']['location'][index] or '', only_border)
                sheet.write(f'E{row}', data['vals']['fsdc_representatives'][index] or '', only_border)
                sheet.write(f'F{row}', data['vals']['teams'][index] or '', only_border)
                sheet.write(f'G{row}', data['vals']['new_relationships'][index] or '', only_border)
                sheet.write(f'H{row}', data['vals']['existing_relationships'][index] or '', only_border)
                sheet.write(f'I{row}', data['vals']['regulatory'][index] or '', only_border)

                col_length[0] = max(col_length[0], len(data['vals']['name'][index] or ''))
                col_length[1] = max(col_length[1], len(data['vals']['date'][index] or ''))
                col_length[2] = max(col_length[2], len(data['vals']['organizer'][index] or ''))
                col_length[3] = max(col_length[3], len(data['vals']['location'][index] or ''))
                col_length[4] = max(col_length[4], len(data['vals']['fsdc_representatives'][index] or ''))
                col_length[5] = max(col_length[5], len(data['vals']['teams'][index] or ''))
                col_length[6] = max(col_length[6], len(data['vals']['new_relationships'][index] or ''))
                col_length[7] = max(col_length[7], len(data['vals']['existing_relationships'][index] or ''))
                col_length[8] = max(col_length[8], len(data['vals']['regulatory'][index] or ''))

                row += 1
            
            for col in range(9):
                sheet.set_column(f'{chr(65 + col)}:{chr(65 + col)}', col_length[col])

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
        