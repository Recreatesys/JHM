
{
    "name": "Document Access Control Mangement",
    "summary": "Manage and control portal user access to documents and directories.",
    "version": "18.0",
    "description": """
        This module provides a comprehensive solution for managing portal user access 
        to documents and directories in Odoo.
    """,
    "author": "SIGB",
    "maintainer": "SIGB",
    "depends": [
        "base","documents_portal_management",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/documents_folder.xml",
        "views/documents_portal_templates.xml",
        "views/ir_attachment_all_views.xml",

    ],

    "installable": True,
    "application": True,
}
