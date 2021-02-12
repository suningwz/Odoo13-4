# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'TSG Project Improves',
    'version' : '1.0',
    'description': """
    - Improves in Project Class
        - Added fields
            - Date Start
            - Date End
            - Coverage
            - Description
            - Notes
    """,
    'category': 'Project',
    'website': 'https://www.tsg.net.co/',
    'depends' : [
        'project',
        'tsg_inventory_improves',
    ],
    'data': [
        'views/project_views.xml',
        'views/stock_picking_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
}
