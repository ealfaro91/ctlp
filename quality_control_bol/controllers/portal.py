# -*- coding: utf-8 -*-

import binascii
from odoo import http, fields, _
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager

# from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.exceptions import AccessError, MissingError
from odoo.http import request

import base64

class Portalfsn(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "fsn_count" in counters:
            fsn_count = (
                request.env["project.fsn"].search_count([
                ])
                if request.env["project.fsn"].check_access_rights(
                    "read", raise_exception=False
                )
                else 0
            )
            values["fsn_count"] = fsn_count
        # if "fsn_to_sign_count" in counters:
        #     member = request.env.user.partner_id.employee_ids
        #     values["fsn_to_sign_count"] = (
        #         request.env["project.fsn"].search_count(
        #             [("employee_id", "in", member.ids), ("state", "=", "sent")]
        #         )
        #         if request.env["project.fsn"].check_access_rights(
        #             "read", raise_exception=False
        #         )
        #         else 0
        #     )
        return values

    def _prepare_fsn_domain(self):
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
        ["/my/fsn", "/my/fsn/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_fsn(
        self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw
    ):
        values = self._prepare_portal_layout_values()
        fsn = request.env["project.fsn"]
        domain = self._prepare_fsn_domain()

        searchbar_sortings = self._prepare_searchbar_sortings()
        if not sortby:
            sortby = "date"
        order = searchbar_sortings[sortby]["order"]

        if date_begin and date_end:
            domain += [
                ("create_date", ">", date_begin),
                ("create_date", "<=", date_end),
            ]

        # fsn count
        fsn_count = fsn.search_count(domain)
        # pager
        pager_values = portal_pager(
            url="/my/fsn",
            url_args={"date_begin": date_begin,
                      "date_end": date_end, "sortby": sortby},
            total=fsn_count,
            page=page,
            step=self._items_per_page,
        )

        # content according to pager and archive selected
        fsn = fsn.search(
            domain,
            order=order,
            limit=self._items_per_page,
            offset=pager_values["offset"],
        )
        request.session["my_fsn_history"] = fsn.ids[:100]

        values.update(
            {
                "date": date_begin,
                "date_end": date_end,
                "fsn": fsn.sudo(),
                "page_name": "fsn_log",
                "default_url": "/my/fsn",
                "pager": pager_values,
                "searchbar_sortings": searchbar_sortings,
                "sortby": sortby,
            }
        )
        return request.render("project_bol.portal_my_fsn", values)

    @http.route(
        ["/my/fsn/<int:fsn_log_id>"],
        type="http",
        auth="public",
        website=True,
        sitemap=False,
    )
    def my_fsn_log_data(
        self,
        fsn_log_id=None,
        access_token=None,
        report_type=None,
        message=False,
        download=False,
        **kw,
    ):
        try:
            fsn_sudo = self._document_check_access(
                "project.fsn",
                fsn_log_id,
                access_token=access_token,
            )
        except (AccessError, MissingError):
            return request.redirect("/my")

        if report_type in ("html", "pdf", "text"):
            return self._show_report(
                model=fsn_sudo,
                report_type=report_type,
                report_ref="project_bol.report_fsn",
                download=download,
            )

        values = {
            "fsn_log": fsn_sudo,
            "message": message,
            "action": fsn_sudo._get_portal_return_action(),
        }
        return request.render("project_bol.my_fsn", values)

    @http.route(
        ["/my/fsn/<int:fsn_log_id>/sign"],
        type="json",
        auth="public",
        website=True,
        sitemap=False,
    )
    def fsn_log_sign(
        self, fsn_log_id, access_token=None, name=None, signature=None
    ):
        # get from query string if not on json param
        access_token = access_token or request.httprequest.args.get(
            "access_token")
        try:
            fsn_sudo = self._document_check_access(
                "project.fsn",
                fsn_log_id,
                access_token=access_token,
            )
        except (AccessError, MissingError):
            return request.redirect("/my")

        # if not fsn_sudo._has_to_be_signed():
        #     return {"error": _("The fsn is not in a state that can be signed.")}
        if not signature:
            return {"error": _("Signature is missing.")}

        try:
            fsn_sudo.write({
                'approval_log_ids': [(0, 0, {
                    'date': fields.Datetime.now(),
                    'sign_signature': signature,
                    # 'employee_has_to_be_signed': False,  # Si quieres también incluir este campo
                })]
            })
            fsn_sudo = request.env['project.fsn'].sudo().browse(fsn_log_id)
            fsn_sudo.signed()
            #fsn_sudo.action_member_sign_off()
        except (TypeError, binascii.Error) as e:
            raise e
            # return {"error": _("Invalid signature data.")}

        # _message_post_helper(
        #     "project.fsn",
        #     fsn_sudo.id,
        #     _("fsn signed by %s") % (name,),
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
            "redirect_url": "/my/fsn/%s?message=sign_ok&access_token=%s"
            % (fsn_sudo.id, access_token),
        }

class PdfInlineController(http.Controller):
    @http.route('/pdf_inline/<model>/<int:record_id>/<field>', type='http', auth='user')
    def pdf_inline(self, model, record_id, field):
        record = request.env[model].sudo().browse(record_id)
        pdf_data = getattr(record, field)
        if not pdf_data:
            return request.not_found()
        pdf_bytes = base64.b64decode(pdf_data)
        headers = [
            ('Content-Type', 'application/pdf'),
            ('Content-Disposition', 'inline; filename="document.pdf"'),
        ]
        return request.make_response(pdf_bytes, headers)
