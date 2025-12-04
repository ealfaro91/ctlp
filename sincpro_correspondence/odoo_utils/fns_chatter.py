from typing import List, Tuple

from odoo import SUPERUSER_ID, api, models
from odoo.exceptions import UserError, ValidationError

#from ..logger import logger


def post_message_in_chatter(instance_res_model, message: str):
    try:
        instance_res_model.message_post(
            author_id=1, message_type="comment", subtype_xmlid="mail.mt_not", body=message
        )
    except Exception as error:
        raise ValidationError("The model does not have the chatter")


def post_message_with_attachments_in_chatter(
    instance_res_model, message: str, attachments: List[Tuple[str, bytes]], author_id: int = 1
):
    """
    instance_res_model: Odoo model instance example: [account.move, res.partner, etc]
    message: string message
    attachments: list of tuples with the binary data
    """
    try:
        instance_res_model.message_post(
            author_id=author_id,
            message_type="comment",
            subtype_xmlid="mail.mt_note",
            body=message,
            attachments=attachments,
        )

    except Exception as error:
      #  logger.error(str(error), exc_info=True)
        raise ValidationError("The model does not have the chatter")


def post_message_with_attachments_ids_in_chatter(
    instance_res_model, message: str, attachments: List[int], author_id: int = 1
):
    """
    instance_res_model: Odoo model instance example: [account.move, res.partner, etc]
    message: string message
    attachments: list of attachment record ids
    """
    try:
        instance_res_model.message_post(
            author_id=author_id,
            message_type="comment",
            subtype_xmlid="mail.mt_note",
            body=message,
            attachment_ids=attachments,
        )

    except (ValidationError, UserError) as odoo_exception:
        raise odoo_exception

    except Exception as error:
       # logger.exception(str(error))
        raise ValidationError("Error al agregar algo chatter")


def post_into_chatter_link_record(
    record_to_add_info: models.Model, new_record: models.Model, env: api.Environment
) -> None:
    # Identify the user who is posting the message
    poster = env.user._is_internal() and env.user.id or SUPERUSER_ID

    # Create link to the record
    links = ""
    model_name = ""
    if new_record.exists():
        model_name = new_record[0]._description
        for r in new_record:
            links += f'<a href="#" data-oe-model="{r._name}" data-oe-id="{r.id}"> {r.display_name}</a> '

    # Add to chatter messages
    if record_to_add_info.exists():
        for r in record_to_add_info:
            r.with_user(poster).message_post(
                message_type="notification",
                subtype_xmlid="mail.mt_note",
                body=f"<p>Se ha añadido el registro: {model_name} {links} </p>",
                body_is_html=True,
            )
