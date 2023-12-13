import logging
from odoo import models, api, fields

_logger = logging.getLogger(__name__)

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'
    
    
    state_id = fields.Many2one('fleet.vehicle.state', string='Stato', default=9) # ID relativo allo stato "In arrivo" scelto come Default per la creazione dei record

    @api.model
    def log_vehicle_ids(self):
        vehicles = self.env['fleet.vehicle'].search([])

        for vehicle in vehicles:
            _logger.info(f"ID del veicolo: {vehicle.id}")