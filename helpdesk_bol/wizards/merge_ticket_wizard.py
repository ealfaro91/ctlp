from odoo import models, fields, api, _


class MergeTicketWizard(models.TransientModel):
    _name = 'merge.ticket.wizard'
    _description = 'Wizard to Change Ticket Area'

    ticket_ids = fields.Many2one('helpdesk.ticket', string='Tickets', required=True)
    area_id = fields.Many2one('helpdesk.ticket.area', string='New Area', required=True)
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

    @api.onchange('merge_by')
    def _onchange_merge_ticket(self):
        self.ticket_ids = self.env['helpdesk.ticket'].search([])

    def action_merge_tickets(self):
        self.env['helpdesk.ticket'].create({

        })
        return {'type': 'ir.actions.act_window_close'}




