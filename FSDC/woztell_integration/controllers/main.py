# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)


class WoztellWebhookController(http.Controller):

    @http.route('/woztell/create/lead', type='json', auth='none', methods=['POST'], csrf=False, cors='*')
    def woztell_create_lead(self, **post):
        try:
            raw_data = http.request.httprequest.data
            payload = json.loads(raw_data.decode('utf-8')) if raw_data else {}
            print("🚀 Woztell Payload Received:", payload)

            first_name = payload.get("first_name")
            last_name = payload.get("last_name")
            phone = payload.get("phone")

            if not first_name or not phone:
                return {"status": "error", "message": "Missing required fields: first_name or phone"}

            lead_name = f"{first_name or ''} {last_name or ''}".strip() or "New Lead"
            admin_user = request.env.ref("base.user_admin")
            env = request.env(user=admin_user)

            lead_vals = {
                "name": lead_name,
                "contact_name": lead_name,
                "phone": phone,
                "description": "Lead created from Woztell Chatbot",
            }

            Lead = env["crm.lead"].sudo().create(lead_vals)
            print(f"✅ Lead Created: ID {Lead.id}, Name: {Lead.name}")

            return {
                "status": "success",
                "lead_id": Lead.id,
                "message": "Lead created successfully",
            }

        except Exception as e:
            http.request.env.cr.rollback()
            print("❌ Error creating lead:", str(e))
            return {"status": "error", "message": str(e)}