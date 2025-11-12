import json
import base64
from odoo import http
from odoo.http import request

class IrAttachemntsShareController(http.Controller):

    @http.route('/web/get_attachments_data', type='http', auth="user")
    def get_attachments_data(self, id, **kwargs):
        try:
            ir_attachment_env = request.env['ir.attachment']
            ir_attachment = ir_attachment_env.sudo().browse(int(id))

            if not ir_attachment or not ir_attachment.exists():
                return request.make_response(
                    json.dumps({'error': True, 'message': "Attachment not found"}),
                    [('Content-Type', 'application/json')]
                )
            is_accessible = False
            if request.env.user.id == ir_attachment.create_uid.id:
                is_accessible = True
            elif request.env.user.id in ir_attachment.shared_user_ids.ids:
                is_accessible = True
            elif request.env.user.id in ir_attachment.folder_id.read_access.ids:
                is_accessible = True

            if not is_accessible:
                return request.make_response(
                    json.dumps({'error': True, 'message': "You do not have permission to access this attachment"}),
                    [('Content-Type', 'application/json')]
                )

            if not ir_attachment or not ir_attachment.datas:
                return request.make_response(
                    json.dumps({'error': True, 'message': "Attachment not found"}),
                    [('Content-Type', 'application/json')]
                )

            content = base64.b64decode(ir_attachment.datas)
            filename = ir_attachment.name or 'attachment'
            mimetype = ir_attachment.mimetype or 'application/octet-stream'

            return request.make_response(
                content,
                headers=[
                    ('Content-Type', mimetype),
                    ('Content-Disposition', f'attachment; filename="{filename}"'),
                ]
            )
        except Exception as e:
            return request.make_response(
                json.dumps({'error': True, 'message': f"An error occurred: {str(e)}"}),
                [('Content-Type', 'application/json')]
            )