from odoo import models, fields, api, _


class DocumentDirectory(models.Model):
    _inherit = "document.directory"

    document_file_type_ids = fields.Many2many(
        comodel_name="document.file.type",
        string="Document File Type",
        help="The type of the document file, used to categorize and manage different file types.",
        tracking=True
    )
    area_id = fields.Many2one(
        comodel_name="helpdesk.ticket.area",
        string="Area",
        help="The area associated with the document, useful for organizing documents by their relevant areas.",
        tracking=True
    )
