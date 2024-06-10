from odoo import api, fields, models


class HelpdeskTicketStage(models.Model):
    _name = "helpdesk.ticket.stage"
    _description = "Helpdesk Ticket Stage"
    _order = "sequence, id"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Stage Name", required=True, translate=True, tracking=True)
    description = fields.Html(translate=True, sanitize_style=True, tracking=True)
    sequence = fields.Integer(default=1, tracking=True)
    active = fields.Boolean(default=True, tracking=True)
    unattended = fields.Boolean(tracking=True)
    on_hold = fields.Boolean(tracking=True)
    closed = fields.Boolean(tracking=True)
    close_from_portal = fields.Boolean(
        help="Display button in portal ticket form to allow closing ticket "
        "with this stage as target.",
        tracking=True
    )
    mail_template_id = fields.Many2one(
        comodel_name="mail.template",
        string="Email Template",
        domain=[("model", "=", "helpdesk.ticket")],
        help="If set an email will be sent to the "
        "customer when the ticket"
        "reaches this step.",
        tracking=True
    )
    fold = fields.Boolean(
        string="Folded in Kanban",
        help="This stage is folded in the kanban view "
        "when there are no records in that stage "
        "to display.",
        tracking=True
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
        tracking=True
    )
    team_ids = fields.Many2many(
        comodel_name="helpdesk.ticket.team",
        string="Helpdesk Teams",
        help="Specific team that uses this stage. If it is empty all teams could uses",
        check_company=True,
        tracking=True
    )

    @api.onchange("closed")
    def _onchange_closed(self):
        if not self.closed:
            self.close_from_portal = False
