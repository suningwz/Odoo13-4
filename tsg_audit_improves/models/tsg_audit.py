from odoo import models, fields

class TsgAudit (models.Model):
      _name = "tsg.audit"
      
      partner = fields.Many2one(comodel_name='res.partner',string="Partner")
      project = fields.Many2one(comodel_name='project.project',string="Project")
      contact = fields.Many2one(comodel_name='res.partner',string="Contact")
      tsg_audit_line_ids = fields.One2many(comodel_name='tsg.audit.line', inverse_name= 'audit_id', string="Audit Lines")

      def load_partner_information (self):
            for record in self:
                stock_picking_class=self.env['stock.picking']
                stock_picking_ids=stock_picking_class.search([('partner_id','=',record.contact.id)])
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
                                    print ("------",values)
                                    self.env['tsg.audit.line'].create(values)
                

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






      