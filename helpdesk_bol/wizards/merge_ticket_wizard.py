from odoo import models, fields, api, _
from odoo.exceptions import UserError


class MergeTicketWizard(models.TransientModel):
    _name = 'merge.ticket.wizard'
    _description = 'Wizard to Change Ticket Area'

    user_id = fields.Many2one(
        'res.users',
        string='User',
        default=lambda self: self.env.user
    )
    ticket_ids = fields.Many2many('helpdesk.ticket', string='Tickets', required=True)
    area_id = fields.Many2one('helpdesk.ticket.area', string='Area', required=True)
    ticket_type_id = fields.Many2one(
        'helpdesk.ticket.type', string='Ticket Type',
        required=True, domain="[('area_id', '=', area_id)]"
    )
    category_id = fields.Many2one(
        'helpdesk.ticket.category', string='Category',
        required=True, domain="[('type_id', '=', ticket_type_id)]"
    )
    subcategory_id = fields.Many2one(
        'helpdesk.ticket.subcategory', string='Sub-Category',
        required=True, domain="[('category_id', '=', category_id)]"
    )
    location_id = fields.Many2one(
        'helpdesk.ticket.location', string='Location',
        domain="[('area_id', '=', area_id)]"
    )
    merge_by = fields.Selection([
        ("title", "Title"),
        ("description", "Description")],
        string="Merge by",
        default="title", required=True
    )
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    merge_reason = fields.Text(string="Merge Reason", required=True)

    def default_get(self, fields):
        result = super(MergeTicketWizard, self).default_get(fields)
        current_ticket = self.env['helpdesk.ticket'].browse(self._context.get('active_ids'))
        result['ticket_ids'] = current_ticket
        # result = super(MergeTicketWizard, self).default_get(fields)
        # current_ticket = self.env['helpdesk.ticket'].browse(self._context.get('active_id'))
        # if current_ticket:
        #     result['ticket_ids'] = self.env['helpdesk.ticket'].search([('name', 'ilike', current_ticket.name)])
        return result

    @api.onchange('merge_by')
    def _onchange_merge_ticket(self):
        self.ticket_ids = self.env['helpdesk.ticket'].search([])

    def action_merge_tickets(self):
        # TODAS LAS DESCRIpciones de los tickets seleccionados VAN AL NUEVO TICKET
        if not self.ticket_ids:
            raise UserError(_("No tickets selected to merge"))
        self.env['helpdesk.ticket'].create({

        })
        return {'type': 'ir.actions.act_window_close'}




