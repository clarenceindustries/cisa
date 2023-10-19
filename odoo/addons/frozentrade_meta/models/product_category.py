from odoo import models, fields, api, _

class ProductCategory(models.Model):
    _inherit = "product.category"

    family = fields.Selection([
                                 ('caisserie','CAISSERIE'),
                                 ('palette','PALETTE'),
                                 ('matiere_premiere','MATIERE PREMIERE'),
                                 ('produit_semi_fini','PRODUIT SEMI FINI'),
                                 ('produit_fini','PRODUIT FINI'),
                                 ('autre','AUTRE')], string="Famille", default='autre')
    restrict_to_packaging = fields.Boolean('Doit être colisé')
