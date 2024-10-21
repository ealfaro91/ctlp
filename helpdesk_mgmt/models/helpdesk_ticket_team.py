from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class HelpdeskTeam(models.Model):
    _name = "helpdesk.ticket.team"
    _description = "Helpdesk Ticket Team"
    _inherit = ["mail.thread", "mail.alias.mixin"]
    _order = "sequence, id"

    sequence = fields.Integer(default=10, tracking=True)
    name = fields.Char(required=True, tracking=True)
    user_ids = fields.Many2many(
        comodel_name="res.users",
        string="Members",
        relation="helpdesk_ticket_team_res_users_rel",
        column1="helpdesk_ticket_team_id",
        column2="res_users_id",
        tracking=True
    )
    active = fields.Boolean(default=True, tracking=True)
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
        tracking=True
    )
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Team Leader",
        check_company=True,
        tracking=True
    )
    alias_id = fields.Many2one(
        comodel_name="mail.alias",
        string="Email",
        ondelete="restrict",
        tracking=True,
        required=True,
        help="The email address associated with \
                               this channel. New emails received will \
                               automatically create new tickets assigned \
                               to the channel.",
    )
    color = fields.Integer(string="Color Index", default=0, tracking=True)
    ticket_ids = fields.One2many(
        comodel_name="helpdesk.ticket",
        inverse_name="team_id",
        string="Tickets",
        tracking=True
    )
    todo_ticket_count = fields.Integer(
        string="Number of tickets", compute="_compute_todo_tickets"
    )
    todo_ticket_count_unassigned = fields.Integer(
        string="Number of tickets unassigned", compute="_compute_todo_tickets"
    )
    todo_ticket_count_unattended = fields.Integer(
        string="Number of tickets unattended", compute="_compute_todo_tickets"
    )
    todo_ticket_count_high_priority = fields.Integer(
        string="Number of tickets in high priority", compute="_compute_todo_tickets"
    )
    show_in_portal = fields.Boolean(
        string="Show in portal form",
        default=True,
        tracking=True,
        help="Allow to select this team when creating a new ticket in the portal.",
    )

    def _get_applicable_stages(self):
        if self:
            domain = [
                ("company_id", "in", [False, self.company_id.id]),
                "|",
                ("team_ids", "=", False),
                ("team_ids", "=", self.id),
            ]
        else:
            domain = [
                ("company_id", "in", [False, self.env.company.id]),
                ("team_ids", "=", False),
            ]
        return self.env["helpdesk.ticket.stage"].search(domain)

    def _compute_todo_tickets(self):
        for team in self:
            team.todo_ticket_count = self.env["helpdesk.ticket"].search_count([
                ('team_id', '=', team.id), ('stage_id.closed', '=', False)])
            team.todo_ticket_count_unassigned = self.env["helpdesk.ticket"].search_count([
                ('team_id', '=', team.id), ('user_id', '=', False)])
            team.todo_ticket_count_unattended = self.env["helpdesk.ticket"].search_count([('priority', '=', '2')])
            team.todo_ticket_count_high_priority = self.env["helpdesk.ticket"].search_count([
                ('team_id', '=', team.id),('priority', '=', '2')])

    def _alias_get_creation_values(self):
        values = super()._alias_get_creation_values()
        values["alias_model_id"] = self.env.ref(
            "helpdesk_mgmt.model_helpdesk_ticket"
        ).id
        values["alias_defaults"] = defaults = safe_eval(self.alias_defaults or "{}")
        defaults["team_id"] = self.id
        return values
