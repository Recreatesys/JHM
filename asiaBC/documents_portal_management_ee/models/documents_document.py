from odoo import models, fields, api, _

class Document(models.Model):
    _inherit = 'documents.document'
    
    
    # is_portal_directory = fields.Boolean(related="folder_id.is_portal_directory", string="Is Portal Document", store=True)    
    shared_user_ids = fields.Many2many('res.users','documents_document_shared_user_rel', 'document_id', 'user_id', string="Shared Users",help="If you choose users, it will only be viewable to those individuals.")
    is_shared_file = fields.Boolean(compute='_compute_is_shared_file',string="Is a Shared File", default=False)
    color = fields.Integer('Color Index', default=0)  

    @api.depends('shared_user_ids')
    def _compute_is_shared_file(self):
        user = self.env.uid
        for rec in self:
            if user in rec.shared_user_ids.ids and user != rec.create_uid.id:
                rec.is_shared_file = True
            else:
                rec.is_shared_file = False