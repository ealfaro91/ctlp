
from odoo import models, fields, api


class ReplaceDocumentVersion(models.TransientModel):
    _name = "replace.document.version"
    _description = "Replace Document Version"


    attachment_id = fields.Many2one(
        "ir.attachment", string="Archivo",
    )
    datas = fields.Binary(string="Archivo", required=True)
    datas_filename = fields.Char(string="Nombre del archivo",)
    old_document_version_id = fields.Many2one(
        "document.version", string="Versión actual",
    )
    new_attachment_id = fields.Many2one(
        "ir.attachment", string="Nuevo adjunto",
    )
    new_document_version_id = fields.Many2one(
        "document.version", string="Versión nueva",
    )
    new_version = fields.Integer(string="Version")

    def action_replace_version(self):
        self.attachment_id.datas = self.datas
        self.attachment_id.name = "version_nueva"
        self.old_document_version_id.active = False
        self.new_document_version_id = self.env['document.version'].create({
            'attachment_id': self.attachment_id.id,
            'version': self.new_version,
        })
       #  self.document_version_id.attachment_id.active = False
