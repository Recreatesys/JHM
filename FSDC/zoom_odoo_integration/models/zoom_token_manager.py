from odoo import models
import requests
import base64
from datetime import datetime, timedelta

from odoo.exceptions import ValidationError


class ZoomTokenManager(models.AbstractModel):
    _name = 'zoom.token.manager'
    _description = 'Zoom Token Manager'

    def _get_zoom_access_token(self):
        config = self.env['ir.config_parameter'].sudo()
        token = config.get_param('zoom.access_token')
        expiry_str = config.get_param('zoom.token_expiry')

        if token and expiry_str:
            expiry = datetime.strptime(expiry_str, '%Y-%m-%d %H:%M:%S')
            if expiry > datetime.utcnow():
                return token  # token still valid

        #  Token expired or missing: regenerate
        client_id = config.get_param('zoom.client_id')
        client_secret = config.get_param('zoom.client_secret')
        account_id = config.get_param('zoom.account_id')

        if not all([client_id, client_secret, account_id]):
            raise ValidationError(
                "Zoom credentials are not fully configured. Please set Client ID, Client Secret, and Account ID.")

        auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "grant_type": "account_credentials",
            "account_id": account_id
        }

        res = requests.post("https://zoom.us/oauth/token", headers=headers, data=data)
        res.raise_for_status()

        json_response = res.json()
        access_token = json_response['access_token']
        expires_in = json_response['expires_in']  # usually 3600 seconds
        expiry_time = datetime.utcnow() + timedelta(seconds=expires_in - 120)  # refresh 2 min early

        # Store in config parameters
        config.set_param('zoom.access_token', access_token)
        config.set_param('zoom.token_expiry', expiry_time.strftime('%Y-%m-%d %H:%M:%S'))
        return access_token
