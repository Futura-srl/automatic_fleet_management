import logging, json
from odoo import models, api, fields

_logger = logging.getLogger(__name__)

class FleetVehicleLogContract(models.Model):
    _inherit = 'fleet.vehicle.log.contract'
    
    organization_id = fields.Many2one('res.partner', string='Centro di costo', domain=[('type', '=', 'delivery')])



        
    @api.model
    def create(self, values):
        # Eseguiamo la creazione del contratto
        new_contract = super(FleetVehicleLogContract, self).create(values)

        # Chiamiamo la tua funzione personalizzata per il nuovo contratto
        _logger.info('HO CREATO IL RECORD')  
        _logger.info(values)  
        _logger.info(values['organization_id'])  
        _logger.info(new_contract.id)  
        _logger.info('TEST 1')  
        record = self.env['fleet.vehicle.log.contract'].search_read([('id', '=', new_contract.id)])
        _logger.info('TEST 2')  
        _logger.info(record)  
        _logger.info(record[0]['vehicle_id'][0])  
        
        if values['cost_subtype_id'] == 47:
            veicolo = self.env['fleet.vehicle'].browse(record[0]['vehicle_id'][0])
            veicolo.write({'organization_id': values['organization_id']})

        return new_contract