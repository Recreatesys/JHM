# -*- coding: utf-8 -*-
{
    'name': 'Woztell Lead Integration',
    'summary': 'Create CRM Leads from Woztell Chatbot messages automatically',
    'version': '18.0.1.0.0',
    'description': """
        This module integrates Odoo CRM with the Woztell chatbot platform.
        Whenever a message is received from the chatbot with customer details,
        it automatically creates a CRM Lead record

        Key Features:
        - REST API endpoint for lead creation (`/woztell/create/lead`)
        - Automatic lead generation from chatbot input
        - Secure and lightweight JSON-based integration
    """,
    'author': 'CodeTrade India Pvt. Ltd.',
    'website': 'https://www.codetrade.io/',
    'support': "support@codetrade.io",
    'category': 'Lead Automation',
    'depends': ['crm','mail','base',],
    'license': 'LGPL-3',
    'data': [],
    'demo': [],
    'images': [
        'static/description/icon.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
