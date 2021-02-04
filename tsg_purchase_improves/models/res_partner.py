# -*- coding: utf-8 -*-

from odoo import models, fields


class Partner(models.Model):
    _name = "res.partner"
    _inherit = "res.partner"

    product_supplier_info_ids = fields.One2many(comodel_name='product.supplierinfo', inverse_name='partner_id', string='Prices List')