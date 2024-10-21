from odoo import _, api, fields, models, tools
from odoo.exceptions import AccessError


class HelpdeskTicket(models.Model):
    _name = "helpdesk.ticket"
    _description = "Helpdesk Ticket"
    _rec_name = "number"
    _order = "create_date asc"
    _mail_post_access = "read"
    _inherit = ["mail.thread.cc", "mail.activity.mixin", "portal.mixin"]

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        """Show always the stages without team, or stages of the default team."""
        search_domain = [
            "|",
            ("id", "in", stages.ids),
            ("team_ids", "=", False),
        ]
        default_team_id = self.default_get(["team_id"]).get("team_id")
        if default_team_id:
            search_domain = [
                "|",
                ("team_ids", "=", default_team_id),
            ] + search_domain
        return stages.search(search_domain, order=order)

    number = fields.Char(string="Ticket number", default="/", readonly=True, tracking=True)
    name = fields.Char(string="Title", required=True, tracking=True)
    description = fields.Html(required=True, sanitize_style=True)
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Assigned user",
        tracking=True,
        store=True,
        index=True,
        domain="[('id', 'in', user_ids)]",
    )
    user_ids = fields.Many2many(
        comodel_name="res.users",
        related="team_id.user_ids",
        string="Users",
        tracking=True
    )
    stage_id = fields.Many2one(
        comodel_name="helpdesk.ticket.stage",
        string="Stage",
        readonly=False,
        ondelete="restrict",
        tracking=True,
        copy=False,
        index=True,
        default=lambda self: self.env.ref('helpdesk_mgmt.helpdesk_ticket_stage_in_progress').id
    )
    partner_id = fields.Many2one(comodel_name="res.partner", string="Contact", tracking=True)
    partner_email = fields.Char(string="Email", related="partner_id.email", tracking=True)
    last_stage_update = fields.Datetime(default=fields.Datetime.now, tracking=True)
    assigned_date = fields.Datetime(tracking=True)
    closed_date = fields.Datetime(tracking=True)
    closed = fields.Boolean(related="stage_id.closed")
    unattended = fields.Boolean(related="stage_id.unattended", store=True)
    on_hold = fields.Boolean(related="stage_id.on_hold", store=True)
    tag_ids = fields.Many2many(comodel_name="helpdesk.ticket.tag", string="Tags", tracking=True)
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
        tracking=True
    )
    channel_id = fields.Many2one(
        comodel_name="helpdesk.ticket.channel",
        string="Channel",
        help="Channel indicates where the source of a ticket"
        "comes from (it could be a phone call, an email...)",
        tracking=True
    )
    category_id = fields.Many2one(
        comodel_name="helpdesk.ticket.category",
        string="Category",
        tracking=True
    )
    team_id = fields.Many2one(
        comodel_name="helpdesk.ticket.team",
        string="Team",
        index=True,
        tracking=True
    )
    priority = fields.Selection(
        selection=[
            ("0", "Low"),
            ("1", "Medium"),
            ("2", "High"),
        ],
        default="1",
        tracking=True
    )
    color = fields.Integer(string="Color Index", related="team_id.color", tracking=True)
    kanban_state = fields.Selection(
        selection=[
            ("normal", "Default"),
            ("done", "Ready for next stage"),
            ("blocked", "Blocked"),
        ],
        tracking=True
    )
    sequence = fields.Integer(
        index=True,
        default=10,
        help="Gives the sequence order when displaying a list of tickets.",
    )
    active = fields.Boolean(default=True, tracking=True)

    def name_get(self):
        res = []
        for rec in self:
            res.append((rec.id, rec.number + " - " + rec.name))
        return res

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        if self.partner_id:
            self.partner_name = self.partner_id.name
            self.partner_email = self.partner_id.email

    # ---------------------------------------------------
    # CRUD
    # ---------------------------------------------------

    def _creation_subtype(self):
        return self.env.ref("helpdesk_mgmt.hlp_tck_created")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("number", "/") == "/":
                vals["number"] = self._prepare_ticket_number(vals)
            if vals.get("user_id") and not vals.get("assigned_date"):
                vals["assigned_date"] = fields.Datetime.now()
        return super().create(vals_list)

    def copy(self, default=None):
        self.ensure_one()
        if default is None:
            default = {}
        if "number" not in default:
            default["number"] = self._prepare_ticket_number(default)
        res = super().copy(default)
        return res

    def write(self, vals):
        for _ticket in self:
            now = fields.Datetime.now()
            if vals.get("stage_id"):
                stage = self.env["helpdesk.ticket.stage"].browse([vals["stage_id"]])
                vals["last_stage_update"] = now
                if stage.closed and not stage.on_hold:
                    vals["closed_date"] = now
            if vals.get("user_id"):
                vals["assigned_date"] = now
        return super().write(vals)

    def _prepare_ticket_number(self, values):
        seq = self.env["ir.sequence"]
        if "company_id" in values:
            seq = seq.with_company(values["company_id"])
        return seq.next_by_code("helpdesk.ticket.sequence") or "/"

    def _compute_access_url(self):
        res = super()._compute_access_url()
        for item in self:
            item.access_url = "/my/ticket/%s" % (item.id)
        return res

    # ---------------------------------------------------
    # Mail gateway
    # ---------------------------------------------------

    def _track_template(self, tracking):
        res = super()._track_template(tracking)
        ticket = self[0]
        if "stage_id" in tracking and ticket.stage_id.mail_template_id:
            res["stage_id"] = (
                ticket.stage_id.mail_template_id,
                {
                    # Need to set mass_mail so that the email will always be sent
                    "composition_mode": "mass_mail",
                    #"auto_delete_message": True,
                    "subtype_id": self.env["ir.model.data"]._xmlid_to_res_id(
                        "mail.mt_note"
                    ),
                    "email_layout_xmlid": "mail.mail_notification_light",
                },
            )
        return res

    @api.model
    def message_new(self, msg, custom_values=None):
        """Override message_new from mail gateway so we can set correct
        default values.
        """
        if custom_values is None:
            custom_values = {}
        defaults = {
            "name": msg.get("subject") or _("No Subject"),
            "description": msg.get("body"),
            "partner_email": msg.get("from"),
            "partner_id": msg.get("author_id"),
        }
        defaults.update(custom_values)
        # Write default values coming from msg
        ticket = super().message_new(msg, custom_values=defaults)
        # Use mail gateway tools to search for partners to subscribe
        email_list = tools.email_split(
            (msg.get("to") or "") + "," + (msg.get("cc") or "")
        )
        partner_ids = [
            p.id
            for p in self.env["mail.thread"]._mail_find_partner_from_emails(
                email_list, records=ticket, force_create=False
            )
            if p
        ]
        ticket.message_subscribe(partner_ids)

        return ticket

    def message_update(self, msg, update_vals=None):
        """Override message_update to subscribe partners"""
        email_list = tools.email_split(
            (msg.get("to") or "") + "," + (msg.get("cc") or "")
        )
        partner_ids = [
            p.id
            for p in self.env["mail.thread"]._mail_find_partner_from_emails(
                email_list, records=self, force_create=False
            )
            if p
        ]
        self.message_subscribe(partner_ids)
        return super().message_update(msg, update_vals=update_vals)

    def _message_get_suggested_recipients(self):
        recipients = super()._message_get_suggested_recipients()
        try:
            for ticket in self:
                if ticket.partner_id:
                    ticket._message_add_suggested_recipient(
                        recipients, partner=ticket.partner_id, reason=_("Customer")
                    )
                elif ticket.partner_email:
                    ticket._message_add_suggested_recipient(
                        recipients,
                        email=ticket.partner_email,
                        reason=_("Customer Email"),
                    )
        except AccessError:

            return recipients
        return recipients
