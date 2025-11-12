# -*- coding: utf-8 -*-
import urllib
from datetime import datetime, timedelta
import pytz
from odoo import models, fields, api, _
import requests

from odoo.exceptions import UserError


class EventEvent(models.Model):
    _inherit = "event.event"

    zoom_tracking_source_ids = fields.One2many(
        'event.source.tracking',
        'event_id',
        string="Zoom Tracking Sources"
    )
    zoom_webinar_id = fields.Char(string="Zoom Webinar ID")
    actual_attendee_count = fields.Integer(
        string="Attendees",
        compute="_compute_actual_attendee_count"
    )

    @api.depends('registration_ids.state')
    def _compute_actual_attendee_count(self):
        for event in self:
            done_regs = event.registration_ids.filtered(lambda r: r.state == 'done')
            event.actual_attendee_count = len(done_regs)


    def run_zoom_integration(self):
        try:
            access_token = self.env['zoom.token.manager']._get_zoom_access_token()
        except Exception as e:
            raise UserError(
                _('Invalid Zoom credentials or failed to fetch access token. Please check the configuration.'))

        headers = {"Authorization": f"Bearer {access_token}"}
        user_id = 'me'
        webinars_url = f"https://api.zoom.us/v2/users/{user_id}/webinars"

        #  Pagination logic
        webinars = []
        next_page_token = ''
        while True:
            url = webinars_url + (f"?next_page_token={next_page_token}" if next_page_token else "")
            raw_response = requests.get(url, headers=headers)
            if raw_response.status_code != 200:
                break
            data = raw_response.json()
            page_webinars = data.get('webinars', [])
            webinars += page_webinars
            next_page_token = data.get('next_page_token')
            if not next_page_token:
                break

        for webinar in webinars:
            webinar_id = webinar['id']
            webinar_uuid = urllib.parse.quote(webinar['uuid'], safe='')
            title = webinar.get('topic')
            timezone = webinar.get('timezone')
            start_time = webinar.get('start_time')

            start_date_utc = False
            if start_time:
                start_time = start_time.replace("T", " ").replace("Z", "")
                start_date_utc = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')

            duration = webinar.get('duration', 0)
            date_end_utc = start_date_utc + timedelta(minutes=duration) if start_date_utc else False

            event = self.env['event.event'].sudo().search([('zoom_webinar_id', '=', webinar_id)], limit=1)
            if not event:
                event = self.env['event.event'].sudo().create({
                    'name': title,
                    'date_begin': start_date_utc,
                    'date_end': date_end_utc,
                    'zoom_webinar_id': webinar_id,
                    'date_tz': timezone,
                })
            else:
                event.write({
                    'date_begin': start_date_utc,
                    'date_end': date_end_utc,
                    'date_tz': timezone,
                })

            # Step 2: Registrants
            reg_url = f"https://api.zoom.us/v2/webinars/{webinar_id}/registrants"
            next_page_token = ''
            while True:
                url = reg_url + (f"?next_page_token={next_page_token}" if next_page_token else "")
                response = requests.get(url, headers=headers).json()
                registrants = response.get('registrants', [])

                for reg in registrants:
                    email = reg.get('email')
                    existing_reg = self.env['event.registration'].sudo().search([
                        ('event_id', '=', event.id),
                        ('email', '=', email)
                    ], limit=1)

                    source_name = reg.get('tracking_source')
                    utm_source = self.env['utm.source'].sudo().search([('name', '=', source_name)], limit=1)
                    if not utm_source and source_name:
                        utm_source = self.env['utm.source'].sudo().create({'name': source_name})

                    registration_date = False
                    create_time_str = reg.get('create_time')
                    if create_time_str:
                        registration_date_str = create_time_str.replace('T', ' ').replace('Z', '')
                        registration_date = datetime.strptime(registration_date_str, '%Y-%m-%d %H:%M:%S')

                    values = {
                        'event_id': event.id,
                        'name': f"{reg.get('first_name', '')} {reg.get('last_name', '')}",
                        'email': email,
                        'phone': reg.get('phone'),
                        'job_title': reg.get('job_title'),
                        'organization': reg.get('org'),
                        'registration_date': registration_date,
                        'utm_source_id': utm_source.id if utm_source else False
                    }

                    if not existing_reg:
                        self.env['event.registration'].sudo().with_context(event_skip_mail_schedulers=True).create(
                            values)
                    else:
                        existing_reg.with_context(event_skip_mail_schedulers=True).write(values)

                next_page_token = response.get('next_page_token')
                if not next_page_token:
                    break

            # Step 3: Tracking Sources
            track_url = f"https://api.zoom.us/v2/webinars/{webinar_id}/tracking_sources"
            try:
                response = requests.get(track_url, headers=headers, timeout=15)
                response.raise_for_status()
                tracking_sources = response.json().get('tracking_sources', [])
            except requests.exceptions.RequestException as e:
                tracking_sources = []

            for track in tracking_sources:
                source_name = track.get('source_name')
                utm_source = self.env['utm.source'].sudo().search([('name', '=', source_name)], limit=1)
                if not utm_source:
                    utm_source = self.env['utm.source'].sudo().create({'name': source_name})

                existing = self.env['event.source.tracking'].search([
                    ('event_id', '=', event.id),
                    ('utm_source_id', '=', utm_source.id),
                ], limit=1)

                values = {
                    'event_id': event.id,
                    'utm_source_id': utm_source.id,
                    'tracking_link': track.get('tracking_url'),
                    'registration_count': track.get('registrationr_count'),
                    'visitor_count': track.get('visitor_count'),
                }

                if existing:
                    existing.write(values)
                else:
                    self.env['event.source.tracking'].create(values)

            # Step 4: Attendance
            attendance_url = f"https://api.zoom.us/v2/past_webinars/{webinar_id}/participants"
            next_page_token = ''
            participants_count = 0
            while True:
                url = attendance_url + (f"?next_page_token={next_page_token}" if next_page_token else "")
                response = requests.get(url, headers=headers).json()
                participants = response.get('participants', [])
                participants_count += len(participants)

                for part in participants:
                    join_time = part.get('join_time')
                    leave_time = part.get('leave_time')

                    if join_time:
                        join_time = datetime.strptime(join_time.replace("T", " ").replace("Z", ""), '%Y-%m-%d %H:%M:%S')
                    if leave_time:
                        leave_time = datetime.strptime(leave_time.replace("T", " ").replace("Z", ""),
                                                       '%Y-%m-%d %H:%M:%S')
                    else:
                        leave_time = fields.Datetime.now()

                    reg = self.env['event.registration'].sudo().search([
                        ('event_id', '=', event.id),
                        ('email', '=', part.get('user_email'))
                    ], limit=1)

                    if reg and reg.state != 'done':
                        reg.write({'state': 'done'})

                    existing_attendance = self.env['zoom.attendance'].sudo().search([
                        ('registration_id', '=', reg.id),
                        ('email', '=', part.get('user_email')),
                        ('join_time', '=', join_time)
                    ], limit=1)

                    if not existing_attendance:
                        self.env['zoom.attendance'].sudo().create({
                            'registration_id': reg.id,
                            'event_id': reg.event_id.id,
                            'name': part.get('name'),
                            'join_time': join_time,
                            'leave_time': leave_time,
                            'duration': round(part.get('duration', 0) / 60, 2),
                            'email': part.get('user_email'),
                            'company_name': reg.organization or '',
                        })
                    else:
                        if reg and (not existing_attendance.company_name or not existing_attendance.event_id):
                            existing_attendance.write({
                                'company_name': reg.organization,
                                'event_id': reg.event_id.id,
                            })

                next_page_token = response.get('next_page_token')
                if not next_page_token:
                    break

            # Deduplication
            att_model = self.env['zoom.attendance'].sudo()
            attendances = att_model.search([('event_id', '=', event.id)])
            seen = {}

            for att in attendances:
                key = (att.email.strip().lower(), att.event_id.id)
                if key in seen:
                    existing = seen[key]
                    if att.duration > existing.duration:
                        existing.unlink()
                        seen[key] = att
                    else:
                        att.unlink()
                else:
                    seen[key] = att

    def write(self, vals):
        if 'date_begin' in vals or 'date_end' in vals:
            for event in self:
                new_date_end_str = vals.get('date_end')
                new_date_end = (
                    fields.Datetime.from_string(new_date_end_str)
                    if new_date_end_str else event.date_end
                )
                now = fields.Datetime.now()

                if new_date_end > now:
                    if event.stage_id.name == 'Ended':
                        new_stage = self.env['event.stage'].search([('name', '=', 'New')], limit=1)
                        if new_stage:
                            event.stage_id = new_stage.id
                else:
                    if event.stage_id.name != 'Ended':
                        ended_stage = self.env['event.stage'].search([('name', '=', 'Ended')], limit=1)
                        if ended_stage:
                            event.stage_id = ended_stage.id

        return super(EventEvent, self).write(vals)
