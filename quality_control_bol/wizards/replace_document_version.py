
from odoo import models, fields, api


class ReplaceDocumentVersion(models.TransientModel):
    _name = "replace.document.version"
    _description = "Replace Document Version"


    attachment_id = fields.Many2one(
        "ir.attachment", string="Attachment", required=True
    )
    old_document_version_id = fields.Many2one(
        "document.version", string="Old Document Version", required=True
    )
    new_attachment_id = fields.Many2one(
        "ir.attachment", string="New Attachment", required=True
    )
    new_document_version_id = fields.Many2one(
        "document.version", string="New Document Version", required=True
    )

    def action_replace_version(self):
        self.attachment_id
        self.document_version_id.active = False
        self.document_version_id.attachment_id.active = False
