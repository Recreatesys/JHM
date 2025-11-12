# -*- coding: utf-8 -*-
{
    'name': 'Custom FSDC',
    'version': '18.0',
    'summary': 'Custom FSDC',
    'sequence': 10,
    'description': """
            Enhance the Contact module by recording individuals' past occupations.
        """,
    'depends': ['base', 'contacts','event','event_sale','zoom_odoo_integration', 'mass_mailing', 'documents'],
    'data': [
        'security/ir.model.access.csv',
        'data/mail_template.xml',
        "data/res_sectors.xml",
        "data/res_industry.xml",
        "data/event_teams.xml",
        "data/ir_cron.xml",
        'views/event_views.xml',
        'views/res_partner_occupation_views.xml',
        'views/res_partner_views.xml',
        'wizard/import_event_wizard_views.xml',
        'wizard/mp_report_wizard.xml',
        'wizard/pr_report_wizard.xml',
        'views/event_menu.xml', # Needs to locate at the bottom
        'views/event_record_tree.xml',
    ],
    'demo': [
    ],
    'assets': {
        'web.assets_backend': [
            'custom_fsdc/static/src/js/dashboard.js',
            'custom_fsdc/static/src/css/dashboard.css',
            'custom_fsdc/static/src/xml/dashboard.xml',
            'custom_fsdc/static/src/js/xlsx_registry.js',
        ],
    },
    'installable': True,
    'application': True,
}
