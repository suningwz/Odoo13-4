# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'TSG Inventory Improves',
    'version' : '1.0',
    'description': """
    - Improves in Inventory Class
        - Added fields
            - Project
        - Changes
            - Owner and Partner always required
            - Unable negative quants
    """,
    'category': 'Inventory',
    'website': 'https://www.tsg.net.co/',
    'depends' : ['stock'],
    'data': [
        'views/stock_picking_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}
