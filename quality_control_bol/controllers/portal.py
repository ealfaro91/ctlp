# -*- coding: utf-8 -*-

import binascii
from odoo import http, fields, _
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from collections import OrderedDict

# from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.exceptions import AccessError, MissingError
from odoo.http import request

import base64

class DocumentPortal(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "document_count" in counters:
            document_count = (
                request.env["ir.attachment"].search_count([
                ])
                if request.env["ir.attachment"].check_access_rights(
                    "read", raise_exception=False
                )
                else 0
            )
            values["document_count"] = document_count
        # if "document_to_sign_count" in counters:
        #     member = request.env.user.partner_id.employee_ids
        #     values["document_to_sign_count"] = (
        #         request.env["ir.attachment"].search_count(
        #             [("employee_id", "in", member.ids), ("state", "=", "sent")]
        #         )
        #         if request.env["ir.attachment"].check_access_rights(
        #             "read", raise_exception=False
        #         )
        #         else 0
        #     )
        return values


    def _document_get_searchbar_groupby(self):
        # values = {
        #     "none": {"input": "none", "label": _("None"), "order": 1},
        #     "category": {
        #         "input": "category",
        #         "label": _("Category"),
        #         "order": 2,
        #     },
        #     "stage": {"input": "stage", "label": _("Stage"), "order": 3},
        # }
        values = {"File type": {"input": "file_type", "label": _("File type"), "order": 4}}
        return dict(sorted(values.items(), key=lambda item: item[1]["order"]))

    def _document_get_groupby_mapping(self):
        return {
            "File type": "document_file_type_id",
        }

    def _prepare_document_domain(self):
        # partner = request.env.user.partner_id
        # if partner.employee_ids:
        #     return [
        #         ("employee_id", "in", partner.employee_ids.ids),
        #         ("state", "not in", ["in_process", "cancelled"]),
        #     ]
        # else:
        return []

    def _prepare_searchbar_sortings(self):
        return {
            "date": {"label": _("Newest"), "order": "create_date desc"},
            "name": {"label": _("Name"), "order": "name"},
        }

    @http.route(
        ["/my/document", "/my/document/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_document(
        self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None,  groupby=None, **kw
    ):
        """ FILTRAR LOS PUBLICADOS PARA ESE USUARIO"""

        values = self._prepare_portal_layout_values()
        document = request.env["ir.attachment"]
        domain = self._prepare_document_domain()

        searchbar_sortings = self._prepare_searchbar_sortings()
        if not sortby:
            sortby = "date"
        order = searchbar_sortings[sortby]["order"]

        # FILTROS
        searchbar_filters = {
            "all": {"label": _("All"), "domain": []},
        }
        for file_type in request.env["document.file.type"].search([]):
            searchbar_filters[str(file_type.id)] = {
                "label": file_type.name,
                "domain": [("file_type_id", "=", file_type.id)],
            }
        # for area in request.env["helpdesk.ticket.area"].search([]):
        #     searchbar_filters[str(area.id)] = {
        #         "label": area.name,
        #         "domain": [("area_id", "=", area.id)],
        #     }

        #
        # if date_begin and date_end:
        #     domain += [
        #         ("create_date", ">", date_begin),
        #         ("create_date", "<=", date_end),
        #     ]

        # document count
        document_count = document.search_count(domain)
        # pager
        pager_values = portal_pager(
            url="/my/document",
            url_args={"date_begin": date_begin,
                      "date_end": date_end, "sortby": sortby},
            total=document_count,
            page=page,
            step=self._items_per_page,
        )

        # content according to pager and archive selected
        document = document.search(
            domain,
            order=order,
            limit=self._items_per_page,
            offset=pager_values["offset"],
        )
        request.session["my_document_history"] = document.ids[:100]
        searchbar_groupby = self._document_get_searchbar_groupby()
        if not groupby:
            groupby = "none"

        values.update(
            {
                # "date": date_begin,
                # "date_end": date_end,
                "documents": document.sudo().search([('state', '=', 'published'), ('user_ids', 'in', request.env.user.id)]),
                "page_name": "document_log",
                "default_url": "/my/document",
                "pager": pager_values,
                "searchbar_sortings": searchbar_sortings,
                "sortby": sortby,
                "searchbar_filters": OrderedDict(
                    sorted(searchbar_filters.items(), key=lambda item: item[1]["label"])),
               # "searchbar_groupby": searchbar_groupby,
                #"groupby": groupby,
            #   "filterby": filterby,
            }
        )
        return request.render("quality_control_bol.portal_my_document", values)

    @http.route(
        ["/my/document/<int:document_log_id>"],
        type="http",
        auth="public",
        website=True,
        sitemap=False,
    )
    def my_document_log_data(
        self,
        document_log_id=None,
        access_token=None,
        report_type=None,
        message=False,
        download=False,
        **kw,
    ):
        try:
            document_sudo = self._document_check_access(
                "ir.attachment",
                document_log_id,
                access_token=access_token,
            )
        except (AccessError, MissingError):
            return request.redirect("/my")

        if report_type in ("html", "pdf", "text"):
            return self._show_report(
                model=document_sudo,
                report_type=report_type,
                report_ref="quality_control_bol.report_document",
                download=download,
            )

        values = {
            "document": document_sudo,
            "approval_log": document_sudo.approval_log_ids.filtered(lambda x: x.user_id == request.env.user),
            "message": message,
            "action": document_sudo._get_portal_return_action(),
        }
        return request.render("quality_control_bol.my_document", values)

    @http.route(
        ["/request/review/<int:document_log_id>"],
        type="http",
        auth="public",
        website=True,
        sitemap=False,
    )
    def request_review(
        self, document_log_id, access_token=None, name=None, signature=None
    ):
        # get from query string if not on json param
        access_token = access_token or request.httprequest.args.get(
            "access_token")
        document_sudo = self._document_check_access(
            "ir.attachment",
            document_log_id,
            access_token=access_token,
        )
        document_sudo.request_review()
        values = {
            "document": document_sudo,
            "action": document_sudo._get_portal_return_action(),
          #  "message": message,
        }
        return request.render("quality_control_bol.my_document", values)


    @http.route(
        ["/my/document/<int:document_log_id>/sign"],
        type="json",
        auth="public",
        website=True,
        sitemap=False,
    )
    def document_log_sign(
        self, document_log_id, access_token=None, name=None, signature=None
    ):
        # get from query string if not on json param
        access_token = access_token or request.httprequest.args.get(
            "access_token")
        try:
            document_sudo = self._document_check_access(
                "ir.attachment",
                document_log_id,
                access_token=access_token,
            )
        except (AccessError, MissingError):
            return request.redirect("/my")

        # if not document_sudo._has_to_be_signed():
        #     return {"error": _("The document is not in a state that can be signed.")}
        if not signature:
            return {"error": _("Signature is missing.")}

        try:
            document_sudo.approval_log_ids.filtered(lambda log: log.user_id.id == request.env.user.id).write({
                'sign_signature': signature,
                'signed_date': fields.Datetime.now(),
                'state': 'approved',
            })
            log = document_sudo.approval_log_ids.filtered(lambda log: log.user_id.id == request.env.user.id)[0]
            document_sudo.document_signed = log.attach_signature_to_pdf(document_sudo.document_signed,
                                                                   signature or request.env.user.sign_signature, log.approval_type, log.x_coord, log.y_coord)

            # document_sudo = request.env['ir.attachment'].sudo().browse(document_log_id)
            #
            # log = document_sudo.approval_log_ids.filtered(lambda log: log.user_id.id == request.env.user.id)
            # document_sudo.document_signed = log.attach_signature_to_pdf(document_sudo.document_signed,
            #                                                        request.env.user.sign_signature)
           # document_sudo.signed()
            #document_sudo.action_member_sign_off()
        except (TypeError, binascii.Error) as e:
            raise e
            # return {"error": _("Invalid signature data.")}

        # _message_post_helper(
        #     "ir.attachment",
        #     document_sudo.id,
        #     _("document signed by %s") % (name,),
        #     **(
        #         {
        #             "token": access_token if access_token else {},
        #             "message_type": "notification",
        #             "subtype_xmlid": "mail.mt_note",
        #         }
        #     ),
        # )

        return {
            "force_refresh": True,
            "redirect_url": "/my/document/%s?message=sign_ok&access_token=%s"
            % (document_sudo.id, access_token),
        }
