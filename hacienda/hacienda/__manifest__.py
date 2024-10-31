# -*- coding: utf-8 -*-
{
    'name': "Hacienda",

    'summary': """""",
    'description': """ """,
    'author': "",
    'category': 'Uncategorized',
    'version': '13.0.1.0.0',
    'depends': ['cdfi_invoice', 'product', 'sale_management'],
    'data': [
        'security/ir.model.access.csv',
        'data/alert.type.csv',
        'data/partner.occupation.csv',
        'report/search_certificate_report.xml',
        'report/report_invoice_inherit.xml',
        'report/report_sale_order_inherit.xml',
        'views/account_move_view.xml',
        'views/alert_type_view.xml',
        'views/partner_occupation_view.xml',
        'views/product_template_view.xml',
        'views/product_product_view.xml',
        'views/res_company_view.xml',
        'views/res_partner_view.xml',
        'views/sale_order_view.xml'
        ],
}
