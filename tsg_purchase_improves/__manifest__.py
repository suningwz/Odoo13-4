# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'TSG Purchase Improves',
    'version' : '1.0',
    'description': """
    - Improves in Purchase Module
        - Added fields
            - In Supplier:
                - New Basic Information Page
                - New Sales page
                - New Purchases Page
                    - New Price List Field
        - Changes
            - Sales and Purchases page removed
            - Intelligent Purchase Implemented
    """,
    'category': 'Purchase',
    'website': 'https://www.tsg.net.co/',
    'depends' : [
        'base', 
        'product',
        'account'
    ],
    'data': [
        'views/res_partner_views.xml',
        'views/product_supplierinfo_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}
