# -*coding: utf-8 -*-

{
    "name": "Document Sign Customization",
    "summary": """Document Sign Customization""",
    "version": "18.0",
    "description": """Document Sign Customization""",
    "author": "codetrade.io",
    "license" :  "",
    "website": "",
    "depends": [
        "base",
        "sign",
        "dics_asiabc",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/sign_send_request_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "documents_sign_customization/static/src/js/*.*"
        ],
    },    
    "installable": True,
    "application": True,
}
