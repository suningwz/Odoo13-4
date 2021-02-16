from odoo import models, fields, api
from odoo.tools.translate import _

class TsgAudit(models.Model):
    _name = "tsg.audit"

    def _compute_tsg_audit_line_ids(self):
        for record in self:
            record.tsg_audit_lines_count = len(self.mapped('tsg_audit_line_ids').ids)
                
    name = fields.Char(string="Audit Number", readonly=True, required=True, copy=False, default='New')
    partner_id = fields.Many2one(comodel_name='res.partner',string="Partner", required=True)
    project_id = fields.Many2one(comodel_name='project.project',string="Project")
    contact_id = fields.Many2one(comodel_name='res.partner',string="Contact")
    tsg_audit_line_ids = fields.One2many(comodel_name='tsg.audit.line', inverse_name= 'audit_id', string="Audit Lines")
    tsg_audit_lines_count = fields.Integer(compute='_compute_tsg_audit_line_ids')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('tsg.audit.sequence') or 'New'
        result = super(TsgAudit, self).create(vals)
        return result

    def load_partner_information (self):
        for record in self:
            stock_picking_class=self.env['stock.picking']
            domain = []
            if record.contact_id:
                domain += [('partner_id','=',record.contact_id.id)]
            else:
                domain += [('partner_id','=',record.partner_id.id)]
            if record.project_id:
                domain += [('project_id','=',record.project_id.id)]
            stock_picking_ids=stock_picking_class.search(domain)
            tsg_audit_lines_registered = [x.stock_picking_line_id.id for x in record.tsg_audit_line_ids]
            for stock_picking in stock_picking_ids:
                    for move_line in stock_picking.move_ids_without_package:
                        if not move_line.id in tsg_audit_lines_registered:
                                values = {  
                                "audit_id" : record.id,
                                "stock_picking_id" : stock_picking.id,
                                "stock_picking_line_id" : move_line.id,
                                "product_id" : move_line.product_id.id,
                                "product_uom" : move_line.product_uom.id,
                                "requested_qty" : move_line.product_uom_qty,
                                "done_qty" : move_line.quantity_done,
                                "diff_qty" : 0,
                                "average_cost" : move_line.product_id.get_average_cost() 
                                }
                                self.env['tsg.audit.line'].create(values)
    
    def get_tsg_audit_lines(self):
        return {
                'name': _('Audit Lines Analysis'),
                'type': 'ir.actions.act_window',
                'res_model': 'tsg.audit.line',
                'view_mode': 'tree,form,pivot,graph',
                'domain': [('id', 'in', self.mapped('tsg_audit_line_ids').ids)]
        }
            

class TsgAuditLine (models.Model):
    _name = "tsg.audit.line"

    audit_id = fields.Many2one(comodel_name='tsg.audit', string="Audit")
    stock_picking_id = fields.Many2one (comodel_name='stock.picking', string = "Stock Picking") 
    stock_picking_line_id = fields.Many2one (comodel_name='stock.move', string= "Stock Picking Line") 
    product_id = fields.Many2one (comodel_name='product.product', string= "Product")
    product_uom = fields.Many2one (comodel_name='uom.uom', string="Unit of Measure")
    requested_qty =  fields.Float (string='Requested Quantity')
    done_qty = fields.Float (string='Done Quantity')
    diff_qty = fields.Float (string='Difference Quantity')
    installed_qty = fields.Float (string='Installed Quantity')
    observation = fields.Text (string= 'Observation')
    average_cost = fields.Float (string= 'Average Cost')

    @api.onchange('installed_qty', 'done_qty')
    def onchange_qty(self):
        self.diff_qty = (self.installed_qty or 0) - (self.done_qty or 0)






      