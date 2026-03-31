{
    'name': 'JHM CRM Contact Sync',
    'version': '18.0.1.0.0',
    'category': 'CRM',
    'summary': 'Sync CRM opportunity fields to Contact; probability selection field',
    'author': 'JHM',
    'depends': ['crm', 'contacts'],
    'data': [
        'views/res_partner_views.xml',
        'views/crm_lead_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
