from odoo import models
"""
Buscar y heredar la clase de productos "product.product"
Hacer una funcion que tome la lista de precios de compra y haga un promedio de costo solamente con los que esten activos (que no tienen fecha final) y que al final retorne dicho promedio.
"""
class ProductProduct(models.Model):
     _name = "product.product"
     _inherit = "product.product"
     
     def get_average_cost (self):
          for record in self:
               average = 0
               total = 0
               count = 0
               for price in record.seller_ids:
                    if not price.date_end:
                         count += 1
                         total += price.price
               average = total / count 
               return average
                    

