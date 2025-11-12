from collections import defaultdict
from odoo.exceptions import ValidationError
from odoo import _, fields, models
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.tools import date_utils
import json
import logging

_logger = logging.getLogger(__name__)

class MPReportWizard(models.TransientModel):
    _name = "event.mp.report.wizard"
    _description = "MP Report Wizard"
    
    start_date = fields.Date(string='Start Date', default=lambda self: self._get_default_date(), store=True, required=True)
    end_date = fields.Date(string='End Date', default=datetime.today(), store=True, required=True)
    mode = fields.Selection(string="Mode", selection=[
        ('View', 'View'),
        ("Print", 'Print')
    ], default='View')
    tag_ids = fields.Many2many('event.tag', string="Tags")


    def _get_default_date(self):
        return (datetime.today() - relativedelta(years=1)).date()


    def generate_mp_report(self):
        if self.tag_ids.ids:
            events = self.env['event.event'].search([('date_begin', '>=', self.start_date), ('date_begin', '<=', self.end_date), ('tag_ids', 'in', self.tag_ids.ids)], order='date_begin asc')
        else:
            events = self.env['event.event'].search([('date_begin', '>=', self.start_date), ('date_begin', '<=', self.end_date)], order='date_begin asc')

        vals = {'name': [], 'chinese_name': [], 'year': [], 'Type': [], 'Count_QA': [], 'Count_Lego': [], 'location': [], 'location_chinese': [], 'organising_district': [], 'organising_district_chinese': [], 'target_audience': [], 'date': []}
        for event in events:
            vals['name'].append(event.name)
            vals['chinese_name'].append(event.event_chinese_name)
            vals['date'].append(event.date_begin.strftime('%Y-%m-%d'))
            vals['year'].append(event.year)
            vals['Type'].append(event.event_type)
            vals['Count_QA'].append(event.count_in_qa_paper)
            vals['Count_Lego'].append(event.count_in_lego_questions)
            vals['location'].append(event.event_location)
            vals['location_chinese'].append(event.event_chinese_location)
            vals['organising_district'].append(event.organising_district)
            vals['organising_district_chinese'].append(event.organising_district_chinese)
            vals['target_audience'].append(event.target_audience)  
        data = {
            'model_id': self.id,
            'vals': vals,
            'type': 'MP',
        }
        return {
            'type': 'ir.actions.report',
            'data': {
                'model': 'event.event',
                'options': json.dumps(data, default=date_utils.json_default),   
                'output_format': 'xlsx',
                'report_name': 'MP Team Event Report',
            },
            'report_type': 'xlsx',
        }
    

    def action_display_records(self):
        if self.tag_ids.ids:
            events = self.env['event.event'].search([('date_begin', '>=', self.start_date), ('date_begin', '<=', self.end_date), ('tag_ids', 'in', self.tag_ids.ids)], order='date_begin asc')
        else:
            events = self.env['event.event'].search([('date_begin', '>=', self.start_date), ('date_begin', '<=', self.end_date)], order='date_begin asc')
            
        mp_list_view = self.env.ref('custom_fsdc.view_event_event_mp_list')
        mp_form_view = self.env.ref('event.view_event_form')
        return {
            'name': "MP Event Records",
            'type': 'ir.actions.act_window',
            'res_model': 'event.event',
           'views': [
            (mp_list_view.id, 'list'),
            (mp_form_view.id, 'form'),
           ],
            'domain': [('id', 'in', events.ids)],
            'context': {'create': False},
        }
    

    def action_button(self):
        if self.mode == 'View':
            return self.action_display_records()
        return self.generate_mp_report()