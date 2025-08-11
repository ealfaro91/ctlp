# -*- coding: utf-8 -*-
import datetime

from dateutil.relativedelta import relativedelta

from odoo import api, models, fields
import pytz


class Appointment(models.Model):
    _inherit = "ctms.clinic.appointment"

    @api.model
    def get_dashboard_values(self):
        """This method returns values to the dashboard in appointment views."""
        result = {
            "today_appointments": 0,
            "today_appointments_in_progress": 0,
            "today_appointments_closed_typed": 0,
            "my_appointments": 0,
            "my_appointments_in_progress": 0,
            "my_appointments_closed_typed": 0,
            "studies": 0,
            "this_week_appointments": 0,
        }
        appointments = self.env["ctms.clinic.appointment"]

        result["today_appointments"] = appointments.search_count(
            [("init_date", "=", fields.Date.context_today(self))]
        )
        result["today_appointments_in_progress"] = appointments.search_count(
            [
                ("init_date", "=", fields.Date.context_today(self)),
                ("state", "in", ["wait", "consultation"]),
            ]
        )
        result["today_appointments_closed_typed"] = appointments.search_count(
            [
                ("init_date", "=", fields.Date.context_today(self)),
                ("state", "in", ["done", "typed"]),
            ]
        )
        result["my_appointments"] = appointments.search_count(
            [
                ("init_date", "=", fields.Date.context_today(self)),
                "|",
                "|",
                ("monitoring_user_id", "=", self.env.user.id),
                ("medical_user_id", "=", self.env.user.id),
                ("user_ids", "in", self.env.user.id),
            ]
        )
        result["my_appointments_in_progress"] = appointments.search_count(
            [
                ("init_date", "=", fields.Date.context_today(self)),
                ("state", "in", ["wait", "consultation"]),
                "|",
                "|",
                ("monitoring_user_id", "=", self.env.user.id),
                ("medical_user_id", "=", self.env.user.id),
                ("user_ids", "in", self.env.user.id),
            ]
        )
        result["my_appointments_closed_typed"] = appointments.search_count(
            [
                ("init_date", "=", fields.Date.context_today(self)),
                ("state", "in", ["done", "typed"]),
                "|",
                "|",
                ("monitoring_user_id", "=", self.env.user.id),
                ("medical_user_id", "=", self.env.user.id),
                ("user_ids", "in", self.env.user.id),
            ]
        )

        result["studies"] = len(self.env.user.delegated_ids)

        result["this_week_appointments"] = appointments.search_count(
            [
                (
                    "date_start",
                    ">=",
                    (
                        datetime.datetime.combine(
                            fields.Date.context_today(self)
                            + relativedelta(weeks=-1, days=1, weekday=0),
                            datetime.time(0, 0, 0),
                        ).astimezone(pytz.utc)
                    ).strftime("%Y-%m-%d %H:%M:%S"),
                ),
                (
                    "date_start",
                    "<=",
                    (
                        datetime.datetime.combine(
                            fields.Date.context_today(self)
                            + relativedelta(days=1, weekday=0),
                            datetime.time(0, 0, 0),
                        ).astimezone(pytz.utc)
                    ).strftime("%Y-%m-%d %H:%M:%S"),
                ),
            ]
        )
        return result
