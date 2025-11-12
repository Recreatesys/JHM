# -*- coding: utf-8 -*-
#############################################################################
#
#    Socius Innovative Global Brains
#
#    Copyright (C) 2024-TODAY Socius Innovative Global Brains
#    Author: Socius Innovative Global Brains (<https://sociusus.com/>)
#
#############################################################################

{
    'name': 'AsiaBC CRM',
    'version': '18.0',
    'author': 'Socius Innovative Global Brains',
    'website': 'https://sociusus.com',
    'license': 'AGPL-3',
    'summary': 'Enhances CRM Leads with new fields and email content extraction',
    'depends': [
        'base','crm'
    ],
    'data': [
            'views/crm_lead.xml',
            'security/ir.model.access.csv',
        ],
    'sequence': 2,
    'installable': True,
    'application': True,
    'auto_install': False,
    'maintainers': ['Socius Innovative Global Brains'],
}

