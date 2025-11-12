# -*- coding: utf-8 -*-
{
    "name": "Contact Customization",
    "version": "18.0",
    "summary": "",
    "category": "",
    'author': 'Codetrade India Private Limited',
    'maintainer': 'Codetrade India Private Limited',
    'company': 'Codetrade India Private Limited',
    "depends": ['base','contacts','account_accountant','activity_dashboard_mngmnt','accountant'],
    "data": [
        "security/ir.model.access.csv",
        "data/email_template.xml",
        "data/ir_cron.xml",
        "views/res_partner_view.xml",
        "views/account_move_view.xml",
        "wizards/account_payment_send_view.xml",
    ],
    'assets': {
        'web.assets_backend': [
            'contact_customization/static/src/js/wizard.js',
        ]
    },
    "installable": True,
    "license": "AGPL-3",
}
