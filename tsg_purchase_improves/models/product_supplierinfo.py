# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SupplierInfo(models.Model):
    _name = "product.supplierinfo"
    _inherit = "product.supplierinfo"

    name = fields.Char(string='Name of Price')
    partner_id = fields.Many2one(
        'res.partner', 'Vendor',
        ondelete='cascade', required=True,
        help="Vendor of this product", check_company=True)

    @api.onchange('partner_id')
    def _onchange_name(self):
        self.currency_id = self.partner_id.property_purchase_currency_id.id or self.env.company.currency_id.id
