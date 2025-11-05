from odoo import models, fields, api, _
from odoo.exceptions import UserError


class MergeTicketWizard(models.TransientModel):
    _name = "merge.ticket.wizard"
    _description = "Wizard to Change Ticket Area"

    user_id = fields.Many2one(
        "res.users",
        string="User",
        default=lambda self: self.env.user
    )
    ticket_ids = fields.Many2many(
        "helpdesk.ticket",
        string="Tickets",
        required=True
    )
    area_id = fields.Many2one(
        "helpdesk.ticket.area",
        string="Area",
        required=True
    )
    ticket_type_id = fields.Many2one(
        "helpdesk.ticket.type",
        string="Ticket Type",
        required=True,
        domain="[('area_id', '=', area_id)]"
    )
    category_id = fields.Many2one(
        "helpdesk.ticket.category",
        string="Category",
        required=True,
        domain="[('type_id', '=', ticket_type_id)]"
    )
    subcategory_id = fields.Many2one(
        "helpdesk.ticket.subcategory",
        string="Sub-Category",
        required=True,
        domain="[('category_id', '=', category_id)]"
    )
    location_id = fields.Many2one(
        "helpdesk.ticket.location",
        string="Location",
        domain="[('area_id', '=', area_id)]"
    )
    create_new_ticket = fields.Boolean(string="Create New Ticket")
    partner_id = fields.Many2one(
        "res.partner",
        string="Customer",
        required=True
    )
    merge_reason = fields.Text(string="Merge Reason", required=True)

    def default_get(self, fields):
        result = super(MergeTicketWizard, self).default_get(fields)
        current_ticket = self.env["helpdesk.ticket"].browse(self._context.get("active_ids"))
        result["ticket_ids"] = current_ticket
        if len(current_ticket) == 1:
            raise UserError(_("You must select at least two tickets to merge"))
        # result = super(MergeTicketWizard, self).default_get(fields)
        # current_ticket = self.env["helpdesk.ticket"].browse(self._context.get("active_id"))
        # if current_ticket:
        #     result["ticket_ids"] = self.env["helpdesk.ticket"].search([("name", "ilike", current_ticket.name)])
        return result

    def action_merge_tickets(self):
        # TODAS LAS DESCRIpciones de los tickets seleccionados VAN AL NUEVO TICKET
        if not self.ticket_ids:
            raise UserError(_("No tickets selected to merge"))
        if self.ticket_ids.filtered(lambda ticket: ticket.stage_id in ("done")):
            raise UserError(_("All tickets to merge must be in state 'Open'"))
        if self.create_new_ticket:
            self.env["helpdesk.ticket"].create({
                "name": self.ticket_ids[0].name,
                "description": "\n".join([ticket.description for ticket in self.ticket_ids]),
                "area_id": self.area_id.id,
                "type_id": self.ticket_type_id.id,
                "category_id": self.category_id.id,
                "subcategory_id": self.subcategory_id.id,
                "location_id": self.location_id.id,
                "partner_id": self.partner_id.id,
                "user_id": self.user_id.id,
                "merge_reason": self.merge_reason,

            })
        self.context = {"merged": True}
        return {"type": "ir.actions.act_window_close"}




