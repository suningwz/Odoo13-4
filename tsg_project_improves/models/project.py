# -*- coding: utf-8 -*-

from odoo import models, fields


class Project(models.Model):
    _name = 'project.project'
    _inherit = 'project.project'

    date_start = fields.Datetime(string='Date Start')
    date_end = fields.Datetime(string='Date End')
    coverage = fields.Selection(selection=[('national', 'National'), ('international', 'International'), ('local', 'Local')], string='Coverage')
    notes = fields.Text(string='Notes')
    description = fields.Text(string='Description')
    product_list_ids = fields.One2many(comodel_name='project.product.list', inverse_name='project_id', string="Product List", copy=True)

class ProjectProductList(models.Model):
    _name = 'project.product.list'

    project_id = fields.Many2one(comodel_name='project.project', string="Project")
    product_id = fields.Many2one(comodel_name='product.product', string="Product")
    product_uom = fields.Many2one(comodel_name='uom.uom', related='product_id.uom_id', string="Unit of Measure")
    required_qty = fields.Float(string="Required Quantity")

