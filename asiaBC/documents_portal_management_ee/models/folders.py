from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class DocumentFolder(models.Model):
    _inherit = 'documents.folder'
    
    is_portal_directory = fields.Boolean(string="Is Poratal Document", default=False)
    
    def unlink(self):
        for folder in self:
            portal_folder = self.env.ref('documents_portal_management_ee.portal_folder')
            if folder.id in [portal_folder.id]:
                raise UserError(_("Sorry...! you can't delete Portal folder, you can rename it."))
        return super(DocumentFolder, self).unlink()
