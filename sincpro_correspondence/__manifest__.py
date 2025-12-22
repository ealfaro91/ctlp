{
    "name": "Correspondencia - Sincpro",
    "summary": "Applicacion para gestionar correspondencia",
    "description": """
    - Gestiona CITES \n
    - Gestiona Correspondencia \n
    - Gestion de hojas de ruta \n
    """,
 #   "external_dependencies": {"python": ["python-docx", "sincpro-framework"]},
    "images": ["static/description/screenshot.png"],
    "price": "15.0",
    "currency": "USD",
    "license": "AGPL-3",
    "application": True,
    "author": "Sincpro S.R.L.",
    "website": "https://sincpro.com.bo",
    "category": "Sincpro/Sincpro",
    "version": "17.240729",
    "depends": ["helpdesk_bol"],
    "data": [
        "pre_configure/sequence_reason.xml",
        "data/ir_sequence_data.xml",
        "security/groups.xml",
        "security/ir.model.access.csv",
        "views/mail_template_data.xml",
        "wizards/correspondence_dialog_assign_views.xml",
        "views/correspondence_type_views.xml",
        "views/correspondence_actions_views.xml",
        "views/correspondence_reason_views.xml",
        "views/correspondence_document.xml",
        "views/correspondence_message_views.xml",
        "views/app_menu.xml",
    ],
    "demo": [],
}
