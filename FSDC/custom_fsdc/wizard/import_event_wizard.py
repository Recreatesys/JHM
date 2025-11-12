import base64
import logging
import openpyxl
import pytz


from odoo import models, fields, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from io import BytesIO

_logger = logging.getLogger(__name__)

class ImportEventWizard(models.TransientModel):
    _name = "import.event.wizard"
    _description = "Import Event Wizard"

    file = fields.Binary(string="Excel File")
    filename = fields.Char(string="File Name")

    def localize_datetime(self,dt_naive, tz_name):
        if not dt_naive or not tz_name:
            return dt_naive
        try:
            local_tz = pytz.timezone(tz_name)
        except Exception:
            raise ValidationError(f"Invalid Timezone: {tz_name}")
        local_dt = local_tz.localize(dt_naive)
        return local_dt.astimezone(pytz.UTC).replace(tzinfo=None)

    def action_import_events(self):
        if not self.file:
            raise UserError("Please Upload a File.")
        try:
            workbook = openpyxl.load_workbook(BytesIO(base64.b64decode(self.file)))
            sheet = workbook.active
            STATE_MAP = {
                'Unconfirmed': 'draft',
                'Registered': 'open',
                'Attended': 'done',
                'Cancelled': 'cancel'
            }
            current_event = None
            for index, row in enumerate(sheet.iter_rows(min_row=2), start=2):
                if all(cell.value is None or str(cell.value).strip() == '' for cell in row):
                    continue
                event_name = row[0].value
                responsible = self.env['res.users'].search([('name', '=', row[4].value)], limit=1)
                stage = self.env['event.stage'].search([('name', '=', row[5].value)], limit=1)
                venue = self.env['res.partner'].search([('name', '=',row[6].value)], limit=1)

                if event_name:
                    date_begin = self.localize_datetime(row[1].value, row[3].value)
                    date_end = self.localize_datetime(row[2].value, row[3].value)
                    current_event_vals = {
                        'name': row[0].value,
                        'date_begin': date_begin,
                        'date_end': date_end,
                        'date_tz': row[3].value,
                        'user_id': responsible.id,
                        'stage_id': stage.id,
                        'address_id': venue.id,
                    }
                    current_event = self.env['event.event'].create(current_event_vals)

                # Attendee data (always required)
                attendee_name = str(row[7].value).strip()
                email = str(row[8].value).strip()
                phone = str(row[9].value).strip()
                job_title = str(row[10].value).strip()
                organization = str(row[11].value).strip()
                status = str(row[12].value).strip()
                create_date = self.localize_datetime(row[13].value, row[3].value) if row[13].value else None
                attended_date = self.localize_datetime(row[14].value, row[3].value) if row[14].value else None

                internal_status = STATE_MAP.get(status, 'open')
                if attendee_name:
                    partner = self.env['res.partner'].search([('email', '=', email)],limit=1)
                    if not partner:
                        partner = self.env['res.partner'].create({
                            'name': attendee_name,
                            'email': email,
                            'is_company': False,
                        })
                    self.env['event.registration'].create({
                        'name': attendee_name,
                        'email': email,
                        'phone': phone,
                        'job_title': job_title,
                        'organization': organization,
                        'state': internal_status,
                        'partner_id': partner.id,
                        'event_id': current_event.id,
                        'create_date': create_date,
                        'date_closed': attended_date
                    })

                utm_source_name = row[15].value if row[15].value else None
                tracking_link = row[16].value if row[16].value else None
                registrations = row[17].value if row[17].value else None
                visitors = row[18].value if row[18].value else None
                if utm_source_name:
                    utm_source = self.env['utm.source'].sudo().search(
                        [('name', '=', utm_source_name)], limit=1)
                    if not utm_source:
                        utm_source = self.env['utm.source'].sudo().create({
                            'name': utm_source_name
                        })
                    self.env['event.source.tracking'].create({
                        'event_id': current_event.id,
                        'utm_source_id': utm_source.id,
                        'tracking_link': tracking_link,
                        'registration_count': int(registrations) if registrations else 0,
                        'visitor_count': int(visitors) if visitors else 0,
                    })
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'success',
                    'title': _("Import Records"),
                    'message': "Records Imported Successfully",
                    'next': {
                        'type': 'ir.actions.act_window_close'
                    },
                }
            }

        except Exception as e:
            raise ValidationError(f"Import failed: {str(e)}")

