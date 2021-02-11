# -*- coding : utf-8 -*-

from odoo import models, fields, api
from odoo.tools.translate import _


class LotReservedWarning(models.TransientModel):
    _name = "lot.reserved.warning"

    message = fields.Text(string="Alert")
