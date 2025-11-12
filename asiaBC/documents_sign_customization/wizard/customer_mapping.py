from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class CustomerMapping(models.TransientModel):
    _name = "customer.mapping"
    _description = 'Customer Mapping'

    sign_item_type_id = fields.Many2one("sign.item.type", string="Name of the placeholder")
    director_id = fields.Many2one("res.partner", string="Director")
    sign_send_request_id = fields.Many2one("sign.send.request")
    placeholder_domain_ids = fields.Many2many('sign.item.type', compute='compute_placeholder_domain')
    director_domain_ids = fields.Many2many('res.partner', compute='compute_director_domain')

    @api.depends('sign_send_request_id.placeholder_mapped_ids')
    def compute_placeholder_domain(self):
        for record in self:
            if record.sign_send_request_id.template_id:
                place_holder_ids = record.sign_send_request_id.template_id.sign_item_ids.mapped('type_id').ids
                used_placeholder_ids = record.sign_send_request_id.placeholder_mapped_ids.mapped('sign_item_type_id').ids
                available_placeholder_ids = list(set(place_holder_ids) - set(used_placeholder_ids))
                record.placeholder_domain_ids = [(6, 0, available_placeholder_ids)]
            else:
                record.placeholder_domain_ids = []

    @api.depends('sign_send_request_id.default_director_id')
    def compute_director_domain(self):
        for record in self:
            if record.sign_send_request_id.partner_company_id:
                partner_company_director_ids = record.sign_send_request_id.partner_company_id.parent_company_ids.ids
                record.director_domain_ids = [(6, 0, partner_company_director_ids)]
            else:
                record.director_domain_ids = []
