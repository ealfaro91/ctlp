from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


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
        domain=[('show_in_directory', '=', True)],
        help="The area associated with the document, useful for organizing documents by their relevant areas.",
        tracking=True
    )

    def unlink(self):
        for dir in self:
            if dir.attachment_ids:
                raise ValidationError(_("The directory has attachments, please move them first."))
        return super(DocumentDirectory, self).unlink()

    @api.onchange("area_id")
    def _onchange_area_id(self):
        for dir in self:
            if dir.area_id:
                dir.color = dir.area_id.color
