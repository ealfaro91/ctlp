# -*- coding: utf-8 -*-

{
    "name": "Trial 360 Mini Dashboard",
    "version": "17.0.1.0.0",
    "category": "EHR",
    "summary": "Mini dashboard for Appointments, Patients, and Medications",
    "description": """This shows a mini dashboard for Appointments, Patients, and Medications""",
    "author": "Integra IT",
    "website": "https://www.integrait.co",
    "depends": [
        "base",
        "trial_clinic",
    ],
    "data": [
        "views/appointment_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "trial_mini_dashboard/static/src/xml/*.xml",
            "trial_mini_dashboard/static/src/js/*.js",
        ],
    },
    "license": "Other proprietary",
    "installable": True,
    "auto_install": True,
    "application": False,
}
