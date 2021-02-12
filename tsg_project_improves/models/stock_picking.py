# -*- coding: utf-8 -*-

from itertools import product
from odoo import models, fields, api
from odoo.exceptions import Warning
from odoo.tools.translate import _

class Picking(models.Model):
    _name = "stock.picking"
    _inherit = "stock.picking"

    take_product_list_from_project = fields.Boolean(string="Take Product List from project?")
    multiplicity = fields.Integer(string="Multiplicity")

    def update_list_multiplicity(self):
        for record in self:
            if record.project_id.product_list_ids:
                new_lines = []
                if record.multiplicity:
                    multiplicity = abs(record.multiplicity)
                else:
                    raise Warning(_("You must fill the multiplicity before update requested products"))
                moves_to_delete_ids = [x.id for x in record.move_ids_without_package]
                for move_to_delete_id in moves_to_delete_ids:
                    move_to_delete = self.env['stock.move'].browse(move_to_delete_id)
                    move_to_delete.unlink()
                for product_line in record.project_id.product_list_ids:
                    vals = {
                        'name': _("Line Created From Project Product List"),
                        'product_id': product_line.product_id.id,
                        'product_uom_qty': product_line.required_qty * multiplicity,
                        'product_uom': product_line.product_uom.id,
                        'location_id': record.location_id.id,
                        'location_dest_id': record.partner_id.property_stock_customer.id,
                    }
                    new_lines += [(0,0,vals)]
                record.write({'move_ids_without_package': new_lines})
            else:
                raise Warning(_("There isn't Product List for the project: %s") % (record.project_id.name))
            
