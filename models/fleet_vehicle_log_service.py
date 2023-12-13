import logging
from odoo import models, api, fields

_logger = logging.getLogger(__name__)

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle.log.service'
    
    organization_id = fields.Many2one('res.partner', string='Centro di costo', domain=[('type', '=', 'delivery')])
