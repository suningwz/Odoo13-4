# -*- coding: utf-8 -*-
from odoo import models, fields, api

class Picking(models.Model):
    _name = "stock.picking"
    _inherit = "stock.picking"

    project_id = fields.Many2one(comodel_name='project.project', string="Project")
    attachment_ids = fields.Many2many(comodel_name='ir.attachment', relation='atthacments_for_pickings',column1='picking_id', column2='att_id',string='Attachments')

    @api.onchange('partner_id')
    def oncahnge_partner_owner(self):
        for record in self:
            if record.partner_id:
                if record.partner_id.parent_id:
                    record.owner_id = record.partner_id.parent_id
                else:
                    record.owner_id = record.partner_id
