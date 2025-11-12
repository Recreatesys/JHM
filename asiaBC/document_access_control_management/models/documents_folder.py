from odoo import models, fields, api

class DocumentFolders(models.Model):
    _inherit = "documents.folders"

    upload_access = fields.Many2many(
        'res.users',
        'folder_upload_access_rel',
        string="Upload Access",
        domain=lambda self: self._get_upload_access_domain(),
        help="Users with upload access."
    )
    read_access = fields.Many2many(
        'res.users',
        'folder_read_access_rel',
        string="Read Access",
        domain=lambda self: self._get_upload_access_domain(),
        help="Users with read access."
    )

    @api.model
    def _get_upload_access_domain(self):
        group_id = self.env.ref('base.group_portal').id
        return [('groups_id', 'in', [group_id])]

    def write(self, vals):
        res = super(DocumentFolders, self).write(vals)
        if 'upload_access' in vals:
            self._update_upload_group()
        if 'read_access' in vals:
            self._update_read_group()
        return res

    def _update_upload_group(self):
        """Update the upload access group based on field changes."""
        group_upload = self.env.ref('document_access_control_management.upload_access_group')
        group_upload.users = self.upload_access

    def _update_read_group(self):
        """Update the read access group based on field changes."""
        group_read = self.env.ref('document_access_control_management.read_access_group')
        group_read.users = self.read_access
