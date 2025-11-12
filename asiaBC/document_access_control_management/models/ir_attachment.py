from odoo import models, fields

class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    fold_id = fields.Many2one('documents.folders', string="Folder", compute="_compute_folder", store=True)

    def _compute_folder(self):
        """Ensure all folders appear in the group even if they are empty."""
        folders = self.env['documents.folders'].search([])
        for folder in folders:
            if not self.search([('folder_id', '=', folder.id)]):
                # Create a dummy record to allow grouping
                self.create({'folder_id': folder.id, 'name': 'Empty Folder Placeholder', 'type': 'binary'})
