# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools import float_compare


class ProductProduct(models.Model):
    _name = "product.product"
    _inherit = "product.product"
    
    def _prepare_sellers(self, params):
        # This search is made to avoid retrieving seller_ids from the cache.
        return self.env['product.supplierinfo'].search([('product_tmpl_id', '=', self.product_tmpl_id.id),
                                                        ('partner_id.active', '=', True)]).sorted(lambda s: (s.sequence, -s.min_qty, s.price, s.id))
    
    @api.depends_context('partner_id')
    def _compute_product_code(self):
        for product in self:
            for supplier_info in product.seller_ids:
                if supplier_info.partner_id.id == product._context.get('partner_id'):
                    product.code = supplier_info.product_code or product.default_code
                    break
            else:
                product.code = product.default_code

    @api.depends_context('partner_id')
    def _compute_partner_ref(self):
        for product in self:
            for supplier_info in product.seller_ids:
                if supplier_info.partner_id.id == product._context.get('partner_id'):
                    product_name = supplier_info.product_name or product.default_code or product.name
                    product.partner_ref = '%s%s' % (product.code and '[%s] ' % product.code or '', product_name)
                    break
            else:
                product.partner_ref = product.display_name
    
    def _select_seller(self, partner_id=False, quantity=0.0, date=None, uom_id=False, params=False):
        self.ensure_one()
        if date is None:
            date = fields.Date.context_today(self)
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        res = self.env['product.supplierinfo']
        sellers = self._prepare_sellers(params)
        if self.env.context.get('force_company'):
            sellers = sellers.filtered(lambda s: not s.company_id or s.company_id.id == self.env.context['force_company'])
        for seller in sellers:
            # Set quantity in UoM of seller
            quantity_uom_seller = quantity
            if quantity_uom_seller and uom_id and uom_id != seller.product_uom:
                quantity_uom_seller = uom_id._compute_quantity(quantity_uom_seller, seller.product_uom)

            if seller.date_start and seller.date_start > date:
                continue
            if seller.date_end and seller.date_end < date:
                continue
            if partner_id and seller.partner_id not in [partner_id, partner_id.parent_id]:
                continue
            if float_compare(quantity_uom_seller, seller.min_qty, precision_digits=precision) == -1:
                continue
            if seller.product_id and seller.product_id != self:
                continue
            if not res or res.name == seller.partner_id:
                res |= seller
        return res.sorted('price')[:1]