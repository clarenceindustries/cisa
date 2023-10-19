from odoo import models, fields, api

class QualityCheckWizard(models.TransientModel):
    _inherit = 'quality.check.wizard'

    package_id = fields.Many2one('stock.quant.package', string='Colis source', related='current_check_id.move_line_id.package_id')
    result_package_id = fields.Many2one('stock.quant.package', string='Colis destination', related='current_check_id.move_line_id.result_package_id')