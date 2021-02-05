# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools.translate import _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import AccessError

from datetime import datetime, date


class PurchaseOrder(models.Model):
    _name = "purchase.order"
    _inherit = "purchase.order"
    
    intelligent_purchase = fields.Boolean(string="Intelligent Purchase")
    
    def _add_supplier_to_product(self):
        # Add the partner in the supplier list of the product if the supplier is not registered for
        # this product. We limit to 10 the number of suppliers for a product to avoid the mess that
        # could be caused for some generic products ("Miscellaneous").
        for line in self.order_line:
            # Do not add a contact as a supplier
            partner = self.partner_id if not self.partner_id.parent_id else self.partner_id.parent_id
            if line.product_id and partner:
                for seller_id in line.product_id.seller_ids:
                    if seller_id.partner_id == partner and not seller_id.date_end:
                        seller_id.sudo().write({'date_end': date.today()})
                # Convert the price in the right currency.
                currency = partner.property_purchase_currency_id or self.env.company.currency_id
                price = self.currency_id._convert(line.price_unit, currency, line.company_id, line.date_order or fields.Date.today(), round=False)
                # Compute the price for the template's UoM, because the supplier's UoM is related to that UoM.
                if line.product_id.product_tmpl_id.uom_po_id != line.product_uom:
                    default_uom = line.product_id.product_tmpl_id.uom_po_id
                    price = line.product_uom._compute_price(price, default_uom)

                supplierinfo = {
                    'name': _('Price from purchase order'),
                    'partner_id': partner.id,
                    'sequence': max(line.product_id.seller_ids.mapped('sequence')) + 1 if line.product_id.seller_ids else 1,
                    'min_qty': 1,
                    'price': price,
                    'currency_id': currency.id,
                    'date_start': date.today(),
                    'delay': 0,
                }
                # In case the order partner is a contact address, a new supplierinfo is created on
                # the parent company. In this case, we keep the product name and code.
                seller = line.product_id._select_seller(
                    partner_id=line.partner_id,
                    quantity=line.product_qty,
                    date=line.order_id.date_order and line.order_id.date_order.date(),
                    uom_id=line.product_uom)
                if seller:
                    supplierinfo['product_name'] = seller.product_name
                    supplierinfo['product_code'] = seller.product_code
                vals = {
                    'seller_ids': [(0, 0, supplierinfo)],
                }
                try:
                    line.product_id.write(vals)
                except AccessError:  # no write access rights -> just ignore
                    break
    
    @api.onchange('partner_id')
    def get_purchase_list(self):
        for record in self:
            processed_products = []
            order_line_lists = []
            if record.partner_id:
                for order_line in record.order_line:
                    order_line.sudo().unlink()
                for price_product in record.partner_id.product_supplier_info_ids:
                    if not price_product.date_end and not price_product.product_tmpl_id.id in processed_products:
                        values = {}
                        values['product_id'] = price_product.product_tmpl_id.id
                        values['name'] = price_product.product_tmpl_id.name
                        values['product_qty'] = price_product.min_qty
                        values['product_uom'] = price_product.product_tmpl_id.uom_po_id.id
                        values['price_unit'] = price_product.price
                        values['taxes_id'] = price_product.product_tmpl_id.supplier_taxes_id.filtered(lambda tax: tax.company_id == self.env.user.company_id).ids
                        values['date_planned'] = self.date_order + relativedelta(days=price_product.delay)
                        processed_products.append(price_product.product_tmpl_id.id)
                        order_line_lists += [(0, 0, values)]
            record.order_line = order_line_lists

    def intelligent_purchases(self):
        for record in self:
            processed_products = []
            new_partner_orders = {}
            lines_to_unlink = []
            for line in record.order_line:
                lower_price = line.price_unit
                lower_price_seller = record.partner_id
                seller_delay = 0
                for price_list_line in line.product_id.seller_ids:
                    if price_list_line.partner_id != lower_price_seller and (not price_list_line.date_end or price_list_line.date_end >= record.date_order.date()) and price_list_line.price < lower_price:
                        lower_price = price_list_line.price
                        lower_price_seller = price_list_line.partner_id
                        seller_delay = price_list_line.delay or 0
                if lower_price_seller and lower_price_seller != record.partner_id:
                    values = {}
                    values['product_id'] = line.product_id.id
                    values['name'] = line.product_id.name
                    values['product_qty'] = line.product_qty
                    values['product_uom'] = line.product_id.uom_po_id.id
                    values['price_unit'] = lower_price
                    values['taxes_id'] = line.product_id.supplier_taxes_id.filtered(lambda tax: tax.company_id == self.env.user.company_id).ids
                    values['date_planned'] = self.date_order + relativedelta(days=seller_delay)
                    processed_products.append(line.product_id.id)
                    if lower_price_seller in new_partner_orders:
                        new_partner_orders[lower_price_seller.id] += [(0, 0, values)]
                    else:
                        new_partner_orders[lower_price_seller.id] = [(0, 0, values)]
                    lines_to_unlink.append(line.id)
            for line_id in lines_to_unlink:
                line = self.env['purchase.order.line'].browse([line_id])
                line.unlink()
            new_lines = 0
            new_orders_ids = []
            for partner_id in new_partner_orders:
                notes = record.notes or ''
                new_order = record.copy({
                        'notes': notes + _("\nPurchase Order Created and Confirmed by Intelligent Purchases"),
                        'partner_id': partner_id,
                        'order_line': new_partner_orders[partner_id],
                        'state': 'draft',
                        })
                new_lines += len(new_partner_orders[partner_id])
                new_order.button_confirm()
                new_orders_ids.append(new_order.id)
            if not record.order_line:
                record.button_cancel()
                record.unlink()
            elif len(new_orders_ids) > 0:
                new_orders_ids.append(record.id)
            return new_orders_ids or False

    def button_confirm(self):
        if self.id and self.intelligent_purchase:
            new_orders_ids = self.intelligent_purchases()
            if (new_orders_ids and self.id in new_orders_ids) or self.id:
                result = super(PurchaseOrder, self).button_confirm()
            else:
                result = True
            if new_orders_ids:
                tree_view_id = self.env.ref('purchase.purchase_order_tree').ids
                form_view_id = self.env.ref('purchase.purchase_order_form').ids
                return {
                    'name': _('Intelligent Purchase'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'purchase.order',
                    'views': [[tree_view_id, 'tree'],[form_view_id, 'form']],
                    'domain': '[("id", "in",' + str(new_orders_ids) + ')]',
                    'view_mode': 'tree',
                    'target': 'current',
                }
            else:
                return result
        else:
            return super(PurchaseOrder, self).button_confirm()
