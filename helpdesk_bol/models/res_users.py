# -*- coding: utf-8 -*-

from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    area = fields.Char(string="ara")

	# @staticmethod
	# def create_tickets():
	# 	return {
	# 		"name": "Go to website",
	# 		"res_model": "ir.actions.act_url",
	# 		"type": "ir.actions.act_url",
	# 		"target": "self",
	# 		"url": "/service_desk"
	# 	}
