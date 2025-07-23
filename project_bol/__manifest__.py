# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Konos
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Project CTLP",
    "version": "17.0",
    "license": "AGPL-3",
    "summary": "",
    "depends": ["project", "helpdesk_bol"],
    "data": [
        "data/project.fsn.benefit.csv",
        "data/project.fsn.system.csv",
        "data/project_task_type_data.xml",
        "data/project_project_stage_data.xml",
        "data/mail_template.xml",
        "security/ir.model.access.csv",
        "security/project_fsn_security.xml",
        "data/approval_state_data.xml",
        "views/approval_log_views.xml",
        "views/approval_state_views.xml",
        "views/project_fsn_benefit_views.xml",
        "views/project_fsn_system_views.xml",
        "views/project_fsn_templates.xml",
        "views/project_fsn_views.xml",
        "views/project_project_views.xml",
       # "views/project_task_views.xml",
        "views/project_task_type_views.xml",
        "views/res_users_views.xml",
    ],
    "application": False,
}
