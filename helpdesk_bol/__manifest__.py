# -*- coding: utf-8 -*-
{
    'name': "Service Desk TI",
    'summary': """ Extensión de helpdesk para el control de tickets de TI """,
    'author': "",
    'website': "http://www.com",
    'category': 'Helpdesk',
    'version': '17.0',
    'depends': [
        'auth_ldap',
        'helpdesk_type',
        'website',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/helpdesk.ticket.type.csv',
      #  'data/helpdesk.ticket.category.csv',
      #  'data/helpdesk.ticket.subcategory.csv',
        #'data/mail_template_data.xml',
        'data/helpdesk_ticket_data.xml',
        #'views/change_stage_page_template.xml',
        #'views/helpdesk_stage_views.xml',
        'views/helpdesk_ticket_category_views.xml',
        'views/helpdesk_ticket_type_views.xml',
        'views/helpdesk_ticket_subcategory_views.xml',
        'views/helpdesk_ticket_views.xml',
        'views/service_desk_page_template.xml',
        'views/res_users_views.xml',
        #'views/service_desk_result_page_template.xml',

    ],
}
