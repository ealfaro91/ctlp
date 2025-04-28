# -*- coding: utf-8 -*-

import pytz
import logging
from markupsafe import Markup, escape
from odoo.tools import is_html_empty, html_escape, html2plaintext, parse_contact_from_email

from werkzeug import urls


from datetime import datetime, timedelta

from odoo import api, fields, models
from odoo.tools import datetime, DEFAULT_SERVER_DATETIME_FORMAT

TODAY = fields.Datetime.now()
_logger = logging.getLogger(__name__)


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    resource_calendar_id =  fields.Many2one(
        "resource.calendar",
        string="Work schedule",
        tracking=True,
        required=True,
        default=lambda self: self.env.ref('resource.resource_calendar_std').id
    )
    category_id = fields.Many2one(
        comodel_name="helpdesk.ticket.category",
        string="Category",
        domain="[('type_id', '=', type_id)]",
        tracking=True
    )
    subcategory_id = fields.Many2one(
        "helpdesk.ticket.subcategory",
        string="Sub-Category",
        domain="[('category_id', '=', category_id)]",
        tracking=True
    )
    location_id = fields.Many2one(
        "helpdesk.ticket.location",
        string="Location",
        tracking=True
    )
    max_attention_time = fields.Float(related="subcategory_id.max_attention_time")
    elapsed_attention_time = fields.Float(
        string="Elapsed Attention Time (hours)",
        compute="_compute_attention_time_state",
    )
    attention_time_state = fields.Selection([
        ("on_time", "On time"), ("delayed", "Delayed")],
        default="on_time", string="Attention time state",
        compute="_compute_attention_time_state",
        search="_search_attention_time_state"
    )
    resolution = fields.Text(string="Resolution", tracking=True)
    reopen_reason = fields.Text(string="Reopen reason", tracking=True)
    area = fields.Char(string="Requester area", tracking=True)
    area_id = fields.Many2one(
        "helpdesk.ticket.area",
        string="Area",
        tracking=True,
    )
    origen_id = fields.Many2one("helpdesk.ticket.origen", string="Origen", tracking=True)
    code = fields.Char(string="Code", related="area_id.code", required=True, tracking=True)
    user_id = fields.Many2one("res.users", tracking=True)
    create_date_utc = fields.Datetime(compute="_get_create_date_userutc")
    area_log_ids = fields.One2many("change.area.log", "ticket_id", string="Area changes")
    state_log_ids = fields.One2many("change.state.log", "ticket_id", string="State changes")
    parent_id = fields.Many2one("helpdesk.ticket", string="Parent ticket")
    child_ticket_ids = fields.One2many("helpdesk.ticket", "parent_id", string="Child tickets")
    merge_reason = fields.Text(string="Merge Reason")
    member_code = fields.Char(string="Member Code", related="partner_id.member_code", tracking=True)
    mobile = fields.Char(string="Mobile", related="partner_id.mobile", tracking=True)
    phone = fields.Char(string="Phone", related="partner_id.phone", tracking=True)
    address = fields.Text(string="Address", compute="_compute_partner_address", tracking=True)
    derived_from_area_id = fields.Many2one("helpdesk.ticket.area", string="Derived From Area")
    derived_from_sdss = fields.Boolean(string="Derived From SDSS", store=True, compute="_compute_derived_from_sdss")
    has_locations = fields.Boolean(related="area_id.has_locations")
    has_origins = fields.Boolean(related="area_id.has_origins")
    has_categories = fields.Boolean(related="area_id.has_categories")
    portal = fields.Char(
        string="Portal", store=True, compute="_compute_portal",
        help="Indicates if the user is a portal user"
    )

    @api.depends('partner_id', 'partner_id.is_member')
    def _compute_portal(self):
        for ticket in self:
            if ticket.partner_id.is_member:
                ticket.portal = "/web/socios/login?redirect="
            else:
                ticket.portal = "/web/login?redirect="

    @api.depends('derived_from_area_id')
    def _compute_derived_from_sdss(self):
        for ticket in self:
            ticket.derived_from_sdss = ticket.derived_from_area_id.code == "SDSS"


    @api.depends('partner_id')
    def _compute_partner_address(self):
        for ticket in self:
            address_parts = [
                ticket.partner_id.street or "",
                ticket.partner_id.street2 or "",
                ticket.partner_id.city or "",
                ticket.partner_id.country_id.name or "",
                ticket.partner_id.zip or ""
            ]
            ticket.address = ", ".join(filter(None, address_parts))

    @api.onchange('team_id')
    def _onchange_area_id(self):
        for ticket in self:
            ticket.area_id = False
            ticket.type_id = False
            ticket.category_id = False
            ticket.subcategory_id = False
            ticket.location_id = False

    @api.onchange('type_id')
    def _onchange_ticket_type_id(self):
        for ticket in self:
            ticket.category_id = False
            ticket.subcategory_id = False

    @api.onchange('category_id')
    def _onchange_category_id(self):
        for ticket in self:
            ticket.subcategory_id = False

    @api.onchange('area_id')
    def _onchange_origen_id(self):
        for ticket in self:
            ticket.origen_id = False

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        for ticket in self:
            if ticket.partner_id:
                ticket.partner_email = ticket.partner_id.email
                ticket.area = ticket.partner_id.area

    def _search_attention_time_state(self, operator, value):
        other_record_ids = self.search([])
        delayed_ids = other_record_ids.filtered(lambda x: 0 < x.max_attention_time < (
                (datetime.strptime(fields.Datetime.to_string(x.closed_date or TODAY), DEFAULT_SERVER_DATETIME_FORMAT)
                 - datetime.strptime(fields.Datetime.to_string(x.create_date), DEFAULT_SERVER_DATETIME_FORMAT)).seconds / 3600
        ))

        if value == "delayed":
            return [('id', 'in', delayed_ids.ids)]
        elif value == "on_time":
            return [('id', 'in', (other_record_ids - delayed_ids).ids)]

    def _get_create_date_userutc(self):
        user_tz = self.env.user.tz or pytz.utc
        local = pytz.timezone(user_tz)
        for ticket in self:
            ticket.create_date_utc = datetime.strftime(pytz.utc.localize(
                datetime.strptime(fields.Datetime.to_string(ticket.create_date),
                                  DEFAULT_SERVER_DATETIME_FORMAT)
            ).astimezone(local), "%Y-%m-%d %H:%M:%S")

    @api.onchange("category_id")
    def _onchange_user_id(self):
        for ticket in self:
            if ticket.category_id.user_id:
                ticket.user_id = ticket.category_id.user_id.id

    @api.model
    def create(self, vals):
        res = super(HelpdeskTicket, self).create(vals)
        template = self.env.ref('helpdesk_bol.ticket_creation')
        if template:
            template.mail_server_id = res.area_id.mail_server_id.id
            template.send_mail(res.id, force_send=False)
        return res

    def _prepare_ticket_number(self, values):
        seq = self.env["helpdesk.ticket.area"].browse(values["area_id"]).sequence_id
        if "company_id" in values:
            seq = seq.with_company(values["company_id"])
        return seq.next_by_id() or "/"

    def write(self, vals):
        res = super(HelpdeskTicket, self).write(vals)
        if vals.get('user_id'):
            template = self.env.ref('helpdesk_bol.ticket_assignation')
            if template:
                template.send_mail(self.id, force_send=False)
        if vals.get('area_id'):
            self.area_log_ids.create({
                'ticket_id': self.id,
                'area_id': vals.get('area_id'),
                'user_id': self.env.user.id,
                'date': fields.Datetime.now()
            })
        if vals.get('stage_id'):
            self.state_log_ids.create({
                'ticket_id': self.id,
                'stage_id': vals.get('stage_id'),
                'user_id': self.env.user.id,
                'date': fields.Datetime.now()
            })
        return res

    def _track_template(self, tracking):
        res = super()._track_template(tracking)
        ticket = self[0]
        if "stage_id" in tracking and ticket.stage_id.mail_template_id:
            res["stage_id"] = (
                ticket.stage_id.mail_template_id,
                {
                    # Need to set mass_mail so that the email will always be sent
                    "composition_mode": "mass_mail",
                    # "auto_delete_message": True,
                    "subtype_id": self.env["ir.model.data"]._xmlid_to_res_id(
                        "mail.mt_note"
                    ),
                    "email_layout_xmlid": "mail.mail_notification_light",
                    "mail_server_id": ticket.area_id.mail_server_id.id,
                 #   "email_from": ticket.area_id.mail_server_id.smtp_user
                },
            )
            ticket.stage_id.mail_template_id.mail_server_id = ticket.area_id.mail_server_id.id
           # ticket.stage_id.mail_template_id.email_from = ticket.area_id.mail_server_id.smtp_user

        return res

    def _notify_get_action_link(self, link_type, **kwargs):
        """ Prepare link to an action: view document, follow document, ... """
        params = {
            'res_id': kwargs.get('res_id', self.ids and self.ids[0] or False),
        }

        # keep only accepted parameters:
        # - action (deprecated), token (assign), access_token (view)
        # - auth_signup: auth_signup_token and auth_login
        # - portal: pid, hash
        params.update(dict(
            (key, value)
            for key, value in kwargs.items()
            if key in ('action', 'token', 'access_token', 'auth_signup_token',
                       'auth_login', 'pid', 'hash')
        ))

        if link_type in ['view', 'assign', 'follow', 'unfollow']:
            base_link = '/mail/%s' % link_type
        elif link_type == 'controller':
            controller = kwargs.get('controller')
            params.pop('model')
            base_link = '%s' % controller
        else:
            return ''

        if link_type not in ['view']:
            token = self._encode_link(base_link, params)
            params['token'] = token

        link = '/my_ticket/%s' % (self.id)
        if self:
            link = self[0].get_base_url() + link

        return link

    def _compute_attention_time_state(self):
        # Que no incluya los tiempos en pausa
        user_tz = self.env.user.tz or pytz.utc
        local = pytz.timezone(user_tz)

        for ticket in self:
            ticket.attention_time_state = "on_time"
            ticket.elapsed_attention_time = 0
            if not ticket.create_date:
                continue

            create_date = pytz.utc.localize(ticket.create_date).astimezone(local)
            close_date = pytz.utc.localize(ticket.closed_date).astimezone(
                local) if ticket.closed_date and ticket.stage_id.id == self.env.ref('helpdesk_mgmt.helpdesk_ticket_stage_done').id else datetime.now(local)
            calendar = ticket.resource_calendar_id

            total_hours = 0
            current_date = create_date

            while current_date < close_date:
                # Verifica si el día actual está en el calendario laboral
                weekday = current_date.weekday()  # 0 = Lunes, ..., 6 = Domingo
                for attendance in calendar.attendance_ids.filtered(
                    lambda a: int(a.dayofweek) == weekday and a.day_period != 'lunch'):
                    # Configuración de horario de trabajo
                    start_time = current_date.replace(hour=int(attendance.hour_from),
                                                      minute=int((attendance.hour_from % 1) * 60))
                    end_time = current_date.replace(hour=int(attendance.hour_to),
                                                    minute=int((attendance.hour_to % 1) * 60))

                    # Ajustes de límites a `create_date` y `close_date`
                    if start_time < create_date:
                        start_time = create_date
                    if end_time > close_date:
                        end_time = close_date

                    if start_time < end_time:
                        total_hours += (end_time - start_time).total_seconds() / 3600

                # Avanza al siguiente día laboral
                current_date += timedelta(days=1)
                current_date = current_date.replace(hour=0, minute=0, second=0, microsecond=0)

            ticket.elapsed_attention_time = total_hours
            if total_hours > ticket.max_attention_time > 0:
                ticket.attention_time_state = "delayed"

    def _automatic_closure(self):
        """
        Changes stage to closed if customer didn't
        answer in the time period settled in configurations
        """
        tickets = self.search([
            ('stage_id', '=',
             self.env.ref('helpdesk_mgmt.helpdesk_ticket_stage_awaiting').id)])
        _logger.info(len(tickets))
        time_to_closure = float(
            self.env['ir.config_parameter'].sudo().get_param('helpdesk_bol.time_to_close_ticket'))
        for ticket in tickets:
            time_from_update = (
                (datetime.strptime(fields.Datetime.to_string(TODAY), DEFAULT_SERVER_DATETIME_FORMAT)
                 - datetime.strptime(fields.Datetime.to_string(ticket.last_stage_update),
                                     DEFAULT_SERVER_DATETIME_FORMAT)).total_seconds() / 3600
            )
            if time_from_update >= time_to_closure:
                ticket.sudo().write({'stage_id': self.env.ref('helpdesk_mgmt.helpdesk_ticket_stage_done').id})

    def _notify_by_email_prepare_rendering_context(self, message, msg_vals=False,
                                                   model_description=False,
                                                   force_email_company=False,
                                                   force_email_lang=False):
        """ Prepare rendering context for notification email.

        Signature: if asked a default signature is computed based on author. Either
        it has an user and we use the user's signature. Either we do not find any
        user and we compute a default one based on the author's name.

        Company: either there is one defined on the record (company_id field set
        with a value), either we use env.company. A new parameter allows to force
        its value.

        Lang: when calling this method, ``_fallback_lang`` should already been
        called, or a lang set in context with another way. A wild guess is done
        based on templates to try to retrieve the recipient's language when a flow
        like "send by email" is performed. Lang is used to try to have the
        notification layout in the same language as the email content. A new
        parameter allows to force its value.

        :param record message: <mail.message> record being notified. May be
          void as 'msg_vals' superseeds it;
        :param dict msg_vals: values dict used to create the message, allows to
          skip message usage and spare some queries;
        :param str model_description: description of current model, given to
          avoid fetching it and easing translation support;
        :param record force_email_company: <res.company> record used when rendering
          notification layout. Otherwise computed based on current record;
        :param str force_email_lang: lang used when rendering content, used
          notably to compute model name or translate access buttons;

        :return: dictionary of values used when rendering notification layout;
        """
        if msg_vals is False:
            msg_vals = {}
        lang = force_email_lang if force_email_lang else self.env.lang
        record_wlang = self.with_context(lang=lang)

        # compute send user and its related signature; try to use self.env.user instead of browsing
        # user_ids if they are the author will give a sudo user, improving access performances and cache usage.
        signature = ''
        email_add_signature = "Hola"
        if email_add_signature:
            author = message.env['res.partner'].browse(
                msg_vals.get('author_id')) if 'author_id' in msg_vals else message.author_id
            author_user = self.env.user if self.env.user.partner_id == author else author.user_ids[
                0] if author and author.user_ids else False
            signature = self.company_id.name
            # if author_user:
            #     signature = self.company_id.name
            # elif author.name:
            #     signature = Markup("<p>-- <br/>%s</p>") % "hola"

        if force_email_company:
            company = force_email_company
        else:
            company = record_wlang.company_id.sudo() if (
                record_wlang and 'company_id' in record_wlang and record_wlang.company_id
            ) else record_wlang.env.company
        if company.website:
            website_url = 'http://%s' % company.website if not company.website.lower().startswith(
                ('http:', 'https:')) else company.website
        else:
            website_url = False

        # record, model
        if not model_description:
            model_description = record_wlang._get_model_description(
                msg_vals.get('model') if 'model' in msg_vals else message.model
            )
        record_name = msg_vals.get('record_name') if 'record_name' in msg_vals else self.name

        # tracking: in case of missing value, perform search (skip only if sure we don't have any)
        check_tracking = msg_vals.get('tracking_value_ids', True) if msg_vals else bool(self)
        tracking = []
        if check_tracking:
            tracking_values = self.env['mail.tracking.value'].sudo().search(
                [('mail_message_id', '=', message.id)]
            ).filtered(
                lambda track: not track.field_groups or self.env.is_superuser() or self.user_has_groups(
                    track.field_groups)
            )
            if tracking_values and hasattr(record_wlang, '_track_filter_for_display'):
                tracking_values = record_wlang._track_filter_for_display(tracking_values)
            tracking = [
                (
                    fmt_vals['changedField'],
                    fmt_vals['oldValue']['value'],
                    fmt_vals['newValue']['value'],
                ) for fmt_vals in tracking_values._tracking_value_format()
            ]

        subtype_id = msg_vals.get('subtype_id') if msg_vals and 'subtype_id' in msg_vals else message.subtype_id.id
        is_discussion = subtype_id == self.env['ir.model.data']._xmlid_to_res_id('mail.mt_comment')

        return {
            # message
            'is_discussion': is_discussion,
            'message': message,
            'subtype': message.subtype_id,
            'tracking_values': tracking,
            # record
            'model_description': model_description,
            'record': record_wlang,
            'record_name': record_name,
            'subtitles': [record_name],
            # user / environment
            'company': company,
            'email_add_signature': self.company_id.name,
            'lang': lang,
            'signature': signature,
            'website_url': website_url,
            # tools
            'is_html_empty': is_html_empty,
        }


    def _notify_by_email_get_base_mail_values(self, message, additional_values=None):
        """ Return model-specific and message-related values to be used when
        creating notification emails. It serves as a common basis for all
        notification emails based on a given message.

        :param record message: <mail.message> record being notified;
        :param dict additional_values: optional additional values to add (ease
          custom calls and inheritance);

        :return: dictionary of values suitable for a <mail.mail> create;
        """
        mail_subject = self.name
        if not mail_subject and self and hasattr(self, '_message_compute_subject'):
            mail_subject = self._message_compute_subject()
        if not mail_subject:
            mail_subject = self.name
        if mail_subject:
            # replace new lines by spaces to conform to email headers requirements
            mail_subject = ' '.join(mail_subject.splitlines())

        # compute references: set references to parents likely to be sent and add current message just to
        # have a fallback in case replies mess with Messsage-Id in the In-Reply-To (e.g. amazon
        # SES SMTP may replace Message-Id and In-Reply-To refers an internal ID not stored in Odoo)
        message_sudo = message.sudo()
        ancestors = self.env['mail.message'].sudo().search(
            [
                ('model', '=', message_sudo.model), ('res_id', '=', message_sudo.res_id),
                ('id', '!=', message_sudo.id),
                ('subtype_id', '!=', False),  # filters out logs
                ('message_id', '!=', False),  # ignore records that somehow don't have a message_id (non ORM created)
            ], limit=32, order='id DESC',  # take 32 last, hoping to find public discussions in it
        )

        # filter out internal messages, to fetch 'public discussion' first
        outgoing_types = ('comment', 'auto_comment', 'email', 'email_outgoing')
        history_ancestors = ancestors.sorted(lambda m: (
            not m.is_internal and not m.subtype_id.internal,
            m.message_type in outgoing_types,
            m.message_type != 'user_notification',  # user notif -> avoid if possible
        ), reverse=True)  # False before True unless reverse
        # order from oldest to newest
        ancestors = history_ancestors[:3].sorted('id')
        references = ' '.join(m.message_id for m in (ancestors + message_sudo))
        # prepare notification mail values
        base_mail_values = {
            'mail_message_id': message.id,
            'references': references,
        }
        if mail_subject != message.subject:
            base_mail_values['subject'] = mail_subject
        if additional_values:
            base_mail_values.update(additional_values)

        # prepare headers (as sudo as accessing mail.alias.domain, restricted)
        headers = {}
        base_mail_values.update({'email_from': self.company_id.name})
        if message_sudo.record_alias_domain_id.bounce_email:
            headers['Return-Path'] = message_sudo.record_alias_domain_id.bounce_email
        headers = self._notify_by_email_get_headers(headers=headers)
        if headers:
            base_mail_values['headers'] = repr(headers)
        return base_mail_values

    # def _notify_by_email_render_layout(self, message, recipients_group,
    #                                    msg_vals=False,
    #                                    render_values=None):
    #     """ Renders the email layout for a given recipients group which
    #     encapsulate the message body.
    #
    #     :param record message: <mail.message> record being notified. May be
    #       void as 'msg_vals' superseeds it;
    #     :param dict recipients_group: a dict containing data for the recipients,
    #       see @ _notify_get_recipients_groups;
    #     :param dict msg_vals: values dict used to create the message, allows to
    #       skip message usage and spare some queries;
    #     :param dict render_values: values to render the notification layout;
    #
    #     At this point expected values are
    #       render_values: company, is_discussion, lang, message, model_description,
    #                      record, record_name, signature, subtype, tracking_values,
    #                      website_url
    #       recipients_group: actions, button_access, has_button_access, recipients
    #
    #     :return str: rendered complete layout;
    #     """
    #     if render_values is None:
    #         render_values = {}
    #
    #     email_layout_xmlid = msg_vals.get('email_layout_xmlid') if msg_vals else message.email_layout_xmlid
    #     template_xmlid = email_layout_xmlid if email_layout_xmlid else 'mail.mail_notification_layout'
    #
    #     render_values = {**render_values, **recipients_group}
    #     mail_body = self.env['ir.qweb']._render(
    #         template_xmlid,
    #         render_values,
    #         minimal_qcontext=True,
    #         raise_if_not_found=False,
    #         lang=render_values.get('lang', self.env.lang),
    #     )
    #     if not mail_body:
    #         _logger.warning(
    #             'QWeb template %s not found or is empty when sending notification emails. Sending without layouting.',
    #             template_xmlid)
    #         mail_body = message.body
    #     return mail_body
