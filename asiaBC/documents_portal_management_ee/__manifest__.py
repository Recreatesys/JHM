# -*coding: utf-8 -*-
#################################################################################
# Author      : CFIS (<https://www.cfis.store/>)
# Copyright(c): 2017-Present CFIS.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://www.cfis.store/>
#################################################################################

{
    "name": "Documents Portal | Portal Documents",
    "summary": """
        This module provide simple and very useful portal functionality to enterprise documents module. 
        documents  owners can see their own documents on portal also they can upload documents to odoo documents.
    """,
    "version": "18.0",
    "description": """
        This module provide simple and very useful portal functionality to enterprise documents module. 
        documents  owners can see their own documents on portal also they can upload documents to odoo documents.
        Documents Portal,
        Portal Documents,
    """,    
    "author": "CFIS",
    "maintainer": "CFIS",
    "license" :  "Other proprietary",
    "website": "https://www.cfis.store",
    "images": ["images/documents_portal_management_ee.png"],
    "category": "Sales",
    "depends": [
        "base",
        "mail",
        "portal",
        "sign",
        "web",
        "documents",
        "documents_portal_management"
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        # "data/documents_portal_data.xml",        
        # "views/documents_portal_templates.xml",
        "views/documents_document_view.xml",
        "views/sign_request_templates.xml",
        "wizard/documents_document_export.xml",
        "wizard/sign_send_request_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "documents_portal_management_ee/static/src/js/*.*",
            "documents_portal_management_ee/static/src/dialogs/thank_you_dialog.js",
            'documents_portal_management_ee/static/src/dialogs/signable_PDF_iframe.js',
        ],
        'web.assets_frontend': [
            'documents_portal_management_ee/static/src/dialogs/thank_you_dialog.js',
            'documents_portal_management_ee/static/src/dialogs/signable_PDF_iframe.js',
        ],
        'sign.assets_public_sign': [
            'documents_portal_management_ee/static/src/dialogs/thank_you_dialog.js',
            'documents_portal_management_ee/static/src/dialogs/signable_PDF_iframe.js',
        ],
    },    
    "installable": True,
    "application": True,
    # "price"                 :  18,
    # "currency"              :  "EUR",
}
