from odoo import api, fields, models, _

class ResUsers(models.Model):
	_inherit="res.users"

	user_ids = fields.One2many('res.users','user_id',string="Users")
	user_id = fields.Many2one('res.users')


class ResPartner(models.Model):
	_inherit="res.partner"

	member_ids = fields.Many2many("res.users")

	