# -*- coding: utf-8 -*-
{
    'name': "Lotes de Facturación de Producto",
    'author': "Elymar Alfaro",
    'category': 'Sales',
    'version': '17.1',
    'depends': ['sale_stock', 'stock_account'],
    'data': [
        'views/sale_order_line_views.xml',
        'reports/report_invoice.xml',
        'reports/sale_report_document.xml',
    ],

}
