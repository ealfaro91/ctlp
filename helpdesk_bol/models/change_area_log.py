# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models

TODAY = fields.Datetime.now()
_logger = logging.getLogger(__name__)


class ChangeStateLog(models.Model):
    _name = "change.area.log"
    _description = "Change Area Log"
    _order = "date desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    ticket_id = fields.Many2one(
        "helpdesk.ticket", string="Ticket",
        required=True, tracking=True
    )
    user_id = fields.Many2one(
        "res.users", string="User",
        required=True, tracking=True
    )
    area_id = fields.Many2one(
        "helpdesk.ticket.area", string="Area",
        required=True, tracking=True
    )
    date = fields.Datetime(
        string="Date", required=True,
        default=TODAY, tracking=True
    )

