from odoo import models, fields, api, _


class AttachmentReviewRequest(models.Model):
    _name = "attachment.review.request"
    _description = "Attachment Review Request"
    _inherit = ["mail.thread", "mail.activity.mixin", "portal.mixin",]

    user_id = fields.Many2one(
        "res.users",
        string="User"
    )
    date = fields.Datetime(string="Date")
    attachment_id = fields.Many2one(
        "ir.attachment",
        string="Attachment"
    )
    message = fields.Text(string="Message")
    version_id = fields.Many2one(
        "document.version",
        string="Version"
    )
