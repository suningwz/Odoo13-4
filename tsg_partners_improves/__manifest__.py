# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'TSG Partners Improves',
    'version' : '1.0',
    'description': """
    - Improves in Partner View
        - The field Parent Company now is always avaible
    """,
    'category': 'Partner',
    'website': 'https://www.tsg.net.co/',
    'depends' : ['base'],
    'data': [
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}
