# -*- coding: utf-8 -*-
{
    'name': "Help Desk TI",
    'summary': """ Extensión de helpdesk para el control de tickets de TI """,
    'author': "",
    'website': "http://www.ctlp.bo",
    'category': 'Helpdesk',
    'version': '17.0',
    'depends': [
        'auth_ldap',
        'helpdesk_mgmt',
        'helpdesk_type',
        'website',
    ],
    'data': [
        'data/mail_template_data.xml',
        'data/helpdesk_ticket_data.xml',
        'data/helpdesk.ticket.type.csv',
        'security/ir.model.access.csv',
        'views/helpdesk_ticket_category_views.xml',
        'views/helpdesk_ticket_type_views.xml',
        'views/helpdesk_ticket_subcategory_views.xml',
        'views/helpdesk_ticket_views.xml',
        'views/service_desk_page_template.xml',
        'views/res_users_views.xml',
        #'views/service_desk_result_page_template.xml',

    ],

    'assets': {'web.assets_frontend': ['helpdesk_bol/static/src/js/**']}
}
