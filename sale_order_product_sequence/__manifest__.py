# -*- coding: utf-8 -*-
{
    'name': "Secuencia de productos por categoría",
    'author': "Elymar Alfaro",
    'category': 'Sales',
    'version': '17.1',
    'depends': ['sale', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_category_sequence_views.xml',
        'views/product_template_views.xml',
        'views/sale_order_views.xml',
    ],

}
