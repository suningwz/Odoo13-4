# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import Warning
from odoo.tools.translate import _

class Picking(models.Model):
    _name = "stock.picking"
    _inherit = "stock.picking"

    def _apply_guide_number(self):
        if self.picking_type_id.code == 'outgoing':
            self.apply_guide_number = True
        else:
            self.apply_guide_number = False

    partner_parent_id = fields.Many2one(comodel_name='res.partner', related='partner_id.parent_id', string='Owner')
    project_id = fields.Many2one(comodel_name='project.project', string="Project")
    attachment_ids = fields.Many2many(comodel_name='ir.attachment', relation='atthacments_for_pickings',column1='picking_id', column2='att_id',string='Attachments')
    is_devolution = fields.Boolean (string= "Is Devolution?")
    devolution_origin_id = fields.Many2one (comodel_name="stock.picking", string="Devolution Origin")
    devolution_related_ids = fields.One2many(comodel_name='stock.picking', inverse_name='devolution_origin_id', string='Devolutions') 
    guide_number = fields.Char(string="Guide Number")
    apply_guide_number = fields.Boolean(compute='_apply_guide_number', string="Apply Guide Number?")

    @api.onchange('partner_id')
    def onchange_partner_owner(self):
        for record in self:
            if record.partner_id:
                if record.partner_id.parent_id:
                    record.owner_id = record.partner_id.parent_id
                else:
                    record.owner_id = record.partner_id

    def action_assign(self):
        result = super(Picking, self).action_assign()
        for record in self:
            message = ""
            for line in record.move_line_ids_without_package:
                if line.product_id.tracking == 'serial':    
                    if not message:
                        message = _("Next you'll see the specific Serial Numbers reserved for some products:")
                    message += _("\n\t For the product %s was assigned the Serial Number: %s" % (line.product_id.name, line.lot_id.name))

            if message:    
                wizard_id = self.env['lot.reserved.warning'].create({'message':message})
                context = dict(self.env.context or {})
                context['action_assign_result'] = result
                view_id = self.env.ref('tsg_inventory_improves.lot_reserved_warning_form_view')
                action = {
                        'name': _('Lot Reserved Warning!'),
                        'view_mode': 'form',
                        'res_model': 'lot.reserved.warning',
                        'view_id': view_id.id,
                        'type': 'ir.actions.act_window',
                        'res_id': wizard_id.id,
                        'context': context,
                        'target': 'new'
                    }
                return action
            else:
                return result

    def button_validate(self):
        result = super(Picking, self).button_validate()
        for record in self:
            if record.apply_guide_number and not record.guide_number:
                raise Warning(_('The field Guide Number must be filled before validate the quantities.'))
        return result