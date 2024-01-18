import logging
from odoo import models, api, fields
import datetime

_logger = logging.getLogger(__name__)


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'
    
    
    state_id = fields.Many2one('fleet.vehicle.state', string='Stato', default=9) # ID relativo allo stato "In arrivo" scelto come Default per la creazione dei record

    @api.model
    def log_vehicle_ids(self):
        
        vehicles = self.env['fleet.vehicle'].search([])
        for vehicle in vehicles:
            self.check_vehicle_status(vehicle)

    def check_vehicle_status(self,vehicle):
        today = datetime.date.today()
        # Tutti i contratti
        contracts = self.env['fleet.vehicle.log.contract'].search_read([('vehicle_id.id', '=', vehicle.id),  ('cost_subtype_id.id', 'in', [11,45,46,47])])
        contracts_count = self.env['fleet.vehicle.log.contract'].search_count([('vehicle_id.id', '=', vehicle.id),  ('cost_subtype_id.id', 'in', [11,45,46,47])])
        # Contratti di disponibilità
        contracts_available = self.env['fleet.vehicle.log.contract'].search_read([('vehicle_id.id', '=', vehicle.id), ('state', '=', 'open'), ('cost_subtype_id.id', '=', 47)])
        # Contratti di noleggio
        contracts_rent = self.env['fleet.vehicle.log.contract'].search_read([('vehicle_id.id', '=', vehicle.id), ('state', '=', 'open'), ('cost_subtype_id.id', '=', 11)])
        # Contratti di proprietà
        contracts_owner = self.env['fleet.vehicle.log.contract'].search_read([('vehicle_id.id', '=', vehicle.id), ('state', '=', 'open'), ('cost_subtype_id.id', '=', 45)])
        # Contratti di noleggio scorta
        contracts_rent_stock = self.env['fleet.vehicle.log.contract'].search_read([('vehicle_id.id', '=', vehicle.id), ('state', '=', 'open'), ('cost_subtype_id.id', '=', 46)])
        _logger.info(f"ID del veicolo: {vehicle.id}")
        _logger.info(f"Numero contratti attivi: {contracts_count}")
        _logger.info(f"Contratti: {contracts}")
        cessato = self.env['fleet.vehicle.log.contract'].search_read([('vehicle_id.id', '=', vehicle.id), ('state', '=', 'open'), ('cost_subtype_id.id', 'in', [11,45,46])])
        flotta = self.env['fleet.vehicle.log.contract'].search_read([('vehicle_id.id', '=', vehicle.id), ('state', '=', 'open'), ('cost_subtype_id.id', 'in', [11,45])])
        riparazione = self.env['fleet.vehicle.log.contract'].search_read([('vehicle_id.id', '=', vehicle.id), ('state', '=', 'open'), ('cost_subtype_id.id', 'in', [11,45,46])])
        bloccati = self.env['fleet.vehicle.log.services'].search_read([('vehicle_id.id', '=', vehicle.id), ('state', '!=', 'done'), ('block_trip_assignment', '=', True)])
        sostituzione = self.env['fleet.replacement'].search_read([('replacement_fleet_id.id', '=', vehicle.id), ('replacement_start_date', '<', today), '|', ('replacement_end_date', '=', False), ('replacement_end_date', '>', today)])
        in_riparazione = self.env['fleet.vehicle.log.contract'].search_read([('vehicle_id.id', '=', vehicle.id), ('state', '=', 'open'), ('cost_subtype_id.id', 'in', [11,45,46,47])])
        if contracts_available == []:
            _logger.info('Non ci sono contratti di disponibilità attivi')
        else:
            _logger.info('Ci sono contratti di disponibilità attivi')
        _logger.info(contracts_available)
        if contracts_rent == []:
            _logger.info('Non ci sono contratti di noleggio attivi')
        else:
            _logger.info('Ci sono contratti di noleggio attivi')
        _logger.info(contracts_rent)
        if contracts_owner == []:
            _logger.info('Non ci sono contratti di proprietà attivi')
        else:
            _logger.info('Ci sono contratti di proprietà attivi')
        _logger.info(contracts_owner)
        if contracts_rent_stock == []:
            _logger.info('Non ci sono contratti di noleggio scorta attivi')
        else:
            _logger.info('Ci sono contratti di noleggio scorta attivi')
        _logger.info(contracts_rent_stock)
        _logger.info(today)
        _logger.info(sostituzione)

            
        # Mezzi che devono essere con lo stato "Cessato"
        if contracts_count > 0 and cessato == [] and contracts_available == []:
            _logger.info(f"Il mezzo {vehicle.id} deve stare su Cessato")
            veicolo = self.env['fleet.vehicle'].browse(vehicle.id)
            veicolo.write({'state_id': 11})
        # Mezzi che devono essere con lo stato "Flotta"
        if contracts_count > 0 and contracts_available != [] and flotta != [] and bloccati == []:
            _logger.info(f"Il mezzo {vehicle.id} deve stare su Flotta")
            veicolo = self.env['fleet.vehicle'].browse(vehicle.id)
            veicolo.write({'state_id': 8})
        # Mezzi che devono essere con lo stato "Scorta"
        if contracts_count > 0 and contracts_available != [] and contracts_rent_stock != []:
            _logger.info(f"Il mezzo {vehicle.id} deve stare su Scorta")
            veicolo = self.env['fleet.vehicle'].browse(vehicle.id)
            veicolo.write({'state_id': 5})
        # Mezzi che devono esserwe con lo stato "In riparazione"
        if contracts_count > 0 and contracts_available == [] and riparazione != [] and bloccati == []:
            _logger.info(f"Il mezzo {vehicle.id} deve stare su In riparazione")
            veicolo = self.env['fleet.vehicle'].browse(vehicle.id)
            veicolo.write({'state_id': 13})
        # Mezzi che devono esserwe con lo stato "Disponibile"
        if contracts_count > 0 and contracts_available != [] and riparazione == [] and bloccati == [] and sostituzione == []:
            _logger.info(f"Il mezzo {vehicle.id} deve stare su Disponibile")
            veicolo = self.env['fleet.vehicle'].browse(vehicle.id)
            veicolo.write({'state_id': 12})
        # Mezzi che devono esserwe con lo stato "Indisponibile"
        if contracts_count > 0 and bloccati != [] and in_riparazione != []:
            _logger.info(f"Il mezzo {vehicle.id} deve stare su Indisponibile")
            veicolo = self.env['fleet.vehicle'].browse(vehicle.id)
            veicolo.write({'state_id': 10})
        # Mezzi che devono essere con lo stato "Sostituzione"
        if sostituzione != [] and cessato != []:
            _logger.info(f"Il mezzo {vehicle.id} deve stare su Sostituzione")
            veicolo = self.env['fleet.vehicle'].browse(vehicle.id)
            veicolo.write({'state_id': 6})