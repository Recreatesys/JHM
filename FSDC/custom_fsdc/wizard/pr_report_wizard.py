from collections import defaultdict
from odoo.exceptions import ValidationError
from odoo import _, fields, models
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.tools import date_utils
import json
import logging

_logger = logging.getLogger(__name__)


class PRReportWizard(models.TransientModel):
    _name = "event.pr.report.wizard"
    _description = "PR Report Wizard"
    
    start_date = fields.Date(string='Start Date', default=lambda self: self._get_default_date(), store=True, required=True)
    end_date = fields.Date(string='End Date', default=datetime.today(), store=True, required=True)
    mode = fields.Selection(string='Mode', selection=[
        ('View', 'View'),
        ('Print', 'Print')
    ], default="View")
    tag_ids = fields.Many2many('event.tag', string="Tags")

    def _get_default_date(self):
        return (datetime.today() - relativedelta(years=1)).date()

    def generate_pr_report(self):
        if self.tag_ids.ids:
            events = self.env['event.event'].search([('date_begin', '>=', self.start_date), ('date_begin', '<=', self.end_date), ('tag_ids', 'in', self.tag_ids.ids)], order='date_begin asc')
        else:
            events = self.env['event.event'].search([('date_begin', '>=', self.start_date), ('date_begin', '<=', self.end_date)], order='date_begin asc')
        
        vals = {'name': [], 'date': [], 'organizer': [], 'location': [], 'fsdc_representatives': [], 'teams': [], 'new_relationships': [], 'existing_relationships': [], 'regulatory': [], 'start_date': False, 'end_date': False}

        for event in events:
            vals['name'].append(event.name)
            date_with_weekday = event.date_begin.strftime('%Y-%m-%d %A')
            vals['date'].append(date_with_weekday)
            vals['organizer'].append(event.organizer_id.name)
            vals['location'].append(event.event_location)
            vals['fsdc_representatives'].append(event.event_representatives)
            team_names = [team.name for team in event.teams]
            vals['teams'].append(' + '.join(team_names))
            vals['new_relationships'].append(event.new_relationships)
            vals['existing_relationships'].append(event.existing_relationship)
            vals['regulatory'].append(event.regulatory)
            vals['start_date'] = self.start_date
            vals['end_date'] = self.end_date
         
        data = {
            'model_id': self.id,
            'vals': vals,
            'type': 'PR',
        }
        
        return {
            'type': 'ir.actions.report',
            'data': {
                'model': 'event.event',
                'options': json.dumps(data, default=date_utils.json_default),
                'output_format': 'xlsx',
                'report_name': 'PR Team Event Report',
            },
            'report_type': 'xlsx',
        }
    

    def action_display_records(self):
        if self.tag_ids.ids:
            events = self.env['event.event'].search([('date_begin', '>=', self.start_date), ('date_begin', '<=', self.end_date), ('tag_ids', 'in', self.tag_ids.ids)], order='date_begin asc')
        else:
            events = self.env['event.event'].search([('date_begin', '>=', self.start_date), ('date_begin', '<=', self.end_date)], order='date_begin asc')

        pr_list_view = self.env.ref('custom_fsdc.view_event_event_pr_list')
        pr_form_view = self.env.ref('event.view_event_form')
        return {
            'name': "PR Event Records",
            'type': 'ir.actions.act_window',
            'res_model': 'event.event',
           'views': [
            (pr_list_view.id, 'list'),
            (pr_form_view.id, 'form'),
           ],
            'domain': [('id', 'in', events.ids)],
            'context': {'create': False},
        }
        

    def action_button(self):
        if self.mode == 'View':
            return self.action_display_records()
        return self.generate_pr_report()