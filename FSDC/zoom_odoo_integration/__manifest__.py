# -*- coding: utf-8 -*-
{
    'name': 'Zoom Odoo Integration',
    'version': '18.0',
    'summary': 'Integrates Zoom Webinars with Odoo Events',
    'sequence': 10,
    'description': """
            This module integrates Zoom Webinars with Odoo Events, allowing:
            - Importing webinar registrants into Odoo
            - Tracking attendance records
            - Managing multiple registration links for the same event
        """,
    'depends': ['base', 'event', 'contacts','mass_mailing'],
    'data': [
        'data/ir_config_parameter_data.xml',
        'data/ir_cron_data.xml',
        'security/ir.model.access.csv',
        'views/event_event.xml',
        'views/zoom_attendence_views.xml',
        'views/event_registration.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
}
