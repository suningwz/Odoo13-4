# -*- coding: utf-8 -*-

from odoo import models, fields


class Project(models.Model):
    _name = 'project.project'
    _inherit = 'project.project'

    date_start = fields.Datetime(string='Date Start')
    date_end = fields.Datetime(string='Date End')
    coverage = fields.Selection(selection=[('national', 'National'), ('international', 'Internationa'), ('local', 'Local')], string='Coverage')
    notes = fields.Text(string='Notes')
    description = fields.Text(string='Description')