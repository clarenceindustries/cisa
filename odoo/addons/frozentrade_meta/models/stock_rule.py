from odoo import models, fields, api

class StockRule(models.Model):
    _inherit = 'stock.rule'

    action = fields.Selection(selection_add=[('push_manufacture', 'Pousser & Produire')], ondelete={'push_manufacture': 'cascade'})