from odoo import models, fields, api

class StockLocation(models.Model):
    _inherit = "stock.location"

    location_type = fields.Selection([
        ('chambre_positive_mp', 'Chambre positive MP'),
        ('congelation_statique_psf', 'Congélation statique PSF'),
        ('congelation_dynamique_psf', 'Congélation dynamique PSF'),
        ('chambre_negative_psf', 'Chambre Négative PSF'),
        ('pre_fabrication_psf', 'Pré-fabrication PSF'),
        ('apres_fabrication_psf', 'Après-fabrication PSF'),
        ('pre_fabrication_pf', 'Pré-fabrication PF'),
        ('apres_fabrication_pf', 'Après-fabrication PF')], string="Réference interne")

    def _get_putaway_strategy(self, product, quantity=0, package=None, packaging=None, additional_qty=None):
        if package:
            products = package.quant_ids.filtered(lambda x: x.location_id == package.location_id).mapped('product_id')
            if len(products) == 1:
                product = products
        return super()._get_putaway_strategy(product, quantity, package, packaging, additional_qty)