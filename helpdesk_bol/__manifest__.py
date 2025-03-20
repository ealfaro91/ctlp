# -*- coding: utf-8 -*-
{
    'name': "Service Desk TI",
    'summary': """ Extensión de helpdesk para el control de tickets de TI """,
    'author': "",
    'website': "http://www.ctlp.bo",
    'category': 'Helpdesk',
    'version': '17.0.1.1.1',
    'depends': [
        'auth_ldap',
        'helpdesk_mgmt',
        'helpdesk_type',
        'website',
        'web_login_styles'
    ],
    'data': [
        'data/ir_sequence_data.xml',
        'data/mail_template_data.xml',
        'data/helpdesk_ticket_area_data.xml',
        'data/helpdesk_ticket_team_data.xml',
        'data/helpdesk.ticket.type.csv',
        'data/ir_cron.xml',
        'security/ir_rule.xml',
        'security/ir.model.access.csv',
        'wizards/merge_ticket_wizard_views.xml',
        'wizards/change_ticket_area_wizard_views.xml',
        'views/change_state_log_views.xml',
        'views/helpdesk_ticket_area_views.xml',
        'views/helpdesk_ticket_category_views.xml',
        'views/helpdesk_ticket_category_views.xml',
        'views/helpdesk_ticket_location_views.xml',
        'views/helpdesk_ticket_type_views.xml',
        'views/helpdesk_ticket_team_views.xml',
        'views/helpdesk_ticket_subcategory_views.xml',
        'views/helpdesk_ticket_views.xml',
        'views/login_template.xml',
        'views/gss_page_template.xml',
        'views/service_desk_page_template.xml',
        'views/res_config_settings_views.xml',
        'views/res_partner_views.xml',
        'views/res_users_views.xml',
    ],

    'assets': {'web.assets_frontend': [
        'helpdesk_bol/static/src/js/**',
        'helpdesk_bol/static/src/css/main.css']}
}
