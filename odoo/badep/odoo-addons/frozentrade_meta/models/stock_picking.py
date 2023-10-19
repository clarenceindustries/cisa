from odoo import fields, models, api, _, exceptions
from odoo.exceptions import UserError
from odoo.tests import Form

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # harvest_date = fields.Datetime(string='Date récolte')
    # fleet_id = fields.Many2one('gsc.fleet', string='Camion', tracking=True)
    # driver_id = fields.Many2one('gsc.driver', string='Conducteur', tracking=True)
    # cin_driver = fields.Char(string='CIN Conducteur', related='driver_id.cin')
    # farm_id = fields.Many2one('gsc.farm', string='Ferme')
    # count_boxs = fields.Integer(string='Nbr caisses', tracking=True, compute='_get_count_boxs')
    # count_pallets = fields.Integer(string="Nbr palettes", tracking=True, compute='_get_count_pallets')
    # weight_all_pallets = fields.Float(digits='Account', string='Tare palettes',
    #                                   compute='_get_weight_pallets', tracking=True)
    # weight_all_boxs = fields.Float(digits='Account', string='Tare caisses',
    #                                compute='_get_weight_boxs', tracking=True)
    # weight_all_boxs_and_pallets = fields.Float(digits='Account', string='Tare C/P',
    #                                            compute='_get_weight_boxs_pallets', tracking=True)
    # weight_net_crop = fields.Float(digits='Account', string='Poids net', compute='_get_net_crop',tracking=True)
    # average_weight_by_box = fields.Float(digits='Account', string="Poids Moy/Caisse",
    #                                      compute='_get_average_weight_by_box', tracking=True)
    # average_weight_by_pallet = fields.Float(digits='Account', string="Poids Moy/Palette",
    #                                         compute='_get_average_weight_by_pallet', tracking=True)
    container = fields.Char(string='Container')
    booking_number = fields.Integer(string='N° Booking')
    count_boxs = fields.Integer(string="Nombre de cartons")
    ship = fields.Char(string='Navire')
    voyage_number = fields.Char(string='Voy N°')
    lieu_chargement = fields.Char(string='Lieu de chargement', default='SIDI ALLAL TAZI')
    port_chargement = fields.Char(string='Port de chargement', default='TANGER MED')
    port_dechargement = fields.Char(string='Port de déchargement')
    fridge_temperature = fields.Float(string="Températeur frigo")
    imco = fields.Char(string="Imco")
    onu = fields.Char(string="Onu")
    page = fields.Char(string="Page")
    nbr_origine_bl = fields.Integer(string="Nbre Originaux B/L:")
    nbr_copie_bl = fields.Integer(string="Nbre copies B/L:")
    nbr_way_bill = fields.Integer(string="Nbre Way Bill:")
    transport_origine = fields.Selection([('prepaid', 'Prepaid'), ('collecte', 'Collecte')], string='Transport origine')
    frais_empbarquement = fields.Selection([('prepaid', 'Prepaid'), ('collecte', 'Collecte')],
                                           string="Frais d'embarquement")
    fret_maritime = fields.Selection([('prepaid', 'Prepaid'), ('collecte', 'Collecte')], string="Fret Maritime")
    frait_debarquement = fields.Selection([('prepaid', 'Prepaid'), ('collecte', 'Collecte')],
                                          string="Frais de débarquement")
    frait_destination = fields.Selection([('prepaid', 'Prepaid'), ('collecte', 'Collecte')],
                                         string="Transport à destination")
    instructions_speciales = fields.Text(string="Instructions spéciales")
    notify_partner_id = fields.Many2one('res.partner', string='Notify')
    location_type = fields.Selection([
        ('chambre_positive_mp', 'Chambre positive MP'),
        ('congelation_statique_psf', 'Congélation statique PSF'),
        ('congelation_dynamique_psf', 'Congélation dynamique PSF'),
        ('chambre_negative_psf', 'Chambre Négative PSF'),
        ('pre_fabrication_psf', 'Pré-fabrication PSF'),
        ('apres_fabrication_psf', 'Après-fabrication PSF'),
        ('pre_fabrication_pf', 'Pré-fabrication PF'),
        ('apres_fabrication_pf', 'Après-fabrication PF')], string="RÉF emplacement destination",
        related='location_dest_id.location_type')
    location_dest_type = fields.Selection([
        ('tunnel_statique1', 'Tunnel Statique 1'),
        ('tunnel_statique2', 'Tunnel Statique 2'),
        ('tunnel_dynamique1', 'Tunnel Dynamique 1'),
        ('tunnel_dynamique2', 'Tunnel Dynamique 2')], string="Type congélation")

    # @api.depends('move_line_ids.subpackaging_count')
    # def _get_count_boxs(self):
    #     for sp in self:
    #         sp.count_boxs = sum(sml.subpackaging_count for sml in sp.move_line_ids)
    #
    # @api.depends('move_ids_without_package.count_pallets')
    # def _get_count_pallets(self):
    #     for sp in self:
    #         sp.count_pallets = 0
    #         if sp.move_ids_without_package:
    #             sp.count_pallets = sum(sm.count_pallets for sm in sp.move_ids_without_package)
    #
    # @api.depends('move_line_ids.result_package_id')
    # def _get_weight_pallets(self):
    #     for sp in self:
    #         sp.weight_all_pallets = sum(sml.package_type_id.base_weight for sml in sp.move_line_ids.mapped('result_package_id'))
    #
    # @api.depends('move_line_ids.subpackaging_id', 'move_line_ids.subpackaging_count')
    # def _get_weight_boxs(self):
    #     for sp in self:
    #         sp.weight_all_boxs = sum(sml.subpackaging_id.base_weight*sml.subpackaging_count for sml in sp.move_line_ids)
    #
    # @api.depends('weight_all_pallets', 'weight_all_boxs')
    # def _get_weight_boxs_pallets(self):
    #     for sp in self:
    #         sp.weight_all_boxs_and_pallets = 0
    #         if sp.weight_all_pallets != 0 and sp.weight_all_boxs != 0:
    #             sp.weight_all_boxs_and_pallets = sp.weight_all_pallets + sp.weight_all_boxs
    #
    # @api.depends('move_ids_without_package.gross_weight', 'weight_all_boxs_and_pallets')
    # def _get_net_crop(self):
    #     for sp in self:
    #         sp.weight_net_crop = 0
    #         if sp.move_ids_without_package:
    #             sp.weight_net_crop = sum(
    #                 sm.gross_weight for sm in sp.move_ids_without_package) - sp.weight_all_boxs_and_pallets
    #
    # @api.depends('weight_net_crop', 'count_boxs')
    # def _get_average_weight_by_box(self):
    #     for sp in self:
    #         sp.average_weight_by_box = 0
    #         if sp.count_boxs > 0 and sp.weight_net_crop > 0:
    #             sp.average_weight_by_box = sp.weight_net_crop / sp.count_boxs
    #
    # @api.depends('weight_net_crop', 'count_pallets')
    # def _get_average_weight_by_pallet(self):
    #     for sp in self:
    #         sp.average_weight_by_pallet = 0
    #         if sp.count_pallets > 0 and sp.weight_net_crop > 0:
    #             sp.average_weight_by_pallet = sp.weight_net_crop / sp.count_pallets
    # @api.onchange('fleet_id')
    # def _onchange_fleet_id(self):
    #     for sp in self:
    #         if sp.fleet_id:
    #             sp.driver_id = sp.fleet_id.driver_id.id

    @api.constrains("ignore_exception", "move_lines", "state", "partner_id")
    def stock_check_exception(self):
        super().stock_check_exception()

    def button_validate(self):
        # for sp in self:
            # for mlp in sp.move_line_ids_without_package:
            #     if mlp.location_dest_id != sp.location_dest_id:
            #         mlp.move_id.location_dest_id = mlp.location_dest_id
            #         sp.location_dest_id = mlp.location_dest_id
            #     if mlp.product_qty == 0 and mlp.qty_done == 0:
            #         mlp.state = 'draft'
            #         mlp.sudo().unlink()
            #         self.env.cr.commit()
        return super().button_validate()

    def _action_done(self):
        res = super()._action_done()
        for sp in self:
            for sml in sp.move_line_ids.filtered(lambda x: x.lot_id):
                if sp.partner_id and sp.picking_type_id.code == 'incoming':
                    sml.lot_id.partner_ids = sp.partner_id
        return res

    @api.constrains('state')
    def onchange_state(self):
        for sp in self:
            mos = self.env['mrp.production']
            if sp.state == 'done':
                for ml in sp.move_ids.filtered(lambda x: x.state == 'done'):
                    bom_lines = sp.env['mrp.bom.line'].search([('product_id', '=', ml.product_id.id)])
                    boms = bom_lines.mapped('bom_id')
                    factors = len(boms)
                    mo = None
                    for bom in boms:
                        product_id = self.env['product.product'].search([('product_tmpl_id', '=', bom.product_tmpl_id.id)])
                        picking_type = self.env['stock.picking.type'].search(
                            [('code', '=', 'mrp_operation'), ('default_location_src_id', '=', ml.location_dest_id.id)])
                        if factors > 0 and product_id and picking_type:
                            bl = bom.bom_line_ids.filtered(lambda x: x.product_id == ml.product_id)[0]
                            mo = self.env['mrp.production'].sudo().create({
                                'product_id': product_id[0].id,
                                'product_uom_id': product_id[0].uom_id.id,
                                'bom_id': bom.id,
                                'product_qty': ((ml.quantity_done / factors) * bom.product_qty) / bl.product_qty,
                                'picking_type_id': picking_type.id,
                                'location_src_id': picking_type.default_location_src_id.id,
                                'location_dest_id': picking_type.default_location_dest_id.id,
                                'company_id': sp.company_id.id,
                            })
                            mos += mo
        if mos:
            mos.action_confirm()
            if mos.mapped('picking_ids'):
                mos.mapped('picking_ids').action_assign()