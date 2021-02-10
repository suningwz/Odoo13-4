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



class ProductTemplate(models.Model):
    _name = "product.template"
    _inherit = "product.template"

    def clean_seller_ids(self):
        for record in self.env['product.template'].search([('id', '!=', 0)]):
            if record.seller_ids:
                to_delete_ids = []
                for seller_cost_line in record.seller_ids:
                    if not seller_cost_line.id in to_delete_ids:
                        for seller_to_validate in record.seller_ids:
                            if seller_to_validate.partner_id == seller_cost_line.partner_id and seller_to_validate.price == seller_cost_line.price and seller_to_validate.date_start == seller_cost_line.date_start and seller_to_validate.id != seller_cost_line.id:
                                if not seller_to_validate.date_end and seller_cost_line.date_end:
                                    to_delete_ids.append(seller_cost_line.id)
                                else:
                                    if not seller_to_validate.id in to_delete_ids:
                                        to_delete_ids.append(seller_to_validate.id)
                for line_to_delete_id in to_delete_ids:
                    line_to_delete = self.env['product.supplierinfo'].browse(line_to_delete_id)
                    line_to_delete.unlink()