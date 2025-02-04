import logging
from odoo import models, api, fields
import datetime

_logger = logging.getLogger(__name__)


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    state_id = fields.Many2one(
        'fleet.vehicle.state',
        string='Stato',
        default=lambda self: self._default_state(),
        readonly=True
    )

    @api.model
    def _default_state(self):
        return self.env.ref('automatic_fleet_management.fleet_vehicle_state_in_arrivo',
                            raise_if_not_found=False)  # ID relativo allo stato "In arrivo" scelto come Default per la creazione dei record

    @api.model
    def log_vehicle_ids(self):

        vehicles = self.env['fleet.vehicle'].sudo().search([])
        for vehicle in vehicles:
            self.check_vehicle_status(vehicle)

    def check_vehicle_status(self, vehicle):
        today = datetime.date.today()
        # Tutti i contratti
        contracts = self.env['fleet.vehicle.log.contract'].search_read([('vehicle_id.id', '=', vehicle.id), (
        'cost_subtype_id.id', 'in', [self.env.ref('maintenance_request.fleet_service_type_noleggio').id,
                                     self.env.ref('maintenance_request.fleet_service_type_proprieta').id,
                                     self.env.ref('maintenance_request.fleet_service_type_noleggio_scorta').id,
                                     self.env.ref(
                                         'maintenance_request.fleet_service_type_disponibilita_mezzo').id])])  # 11,45,46,47
        contracts_count = self.env['fleet.vehicle.log.contract'].search_count([('vehicle_id.id', '=', vehicle.id), (
        'cost_subtype_id.id', 'in', [self.env.ref('maintenance_request.fleet_service_type_noleggio').id,
                                     self.env.ref('maintenance_request.fleet_service_type_proprieta').id,
                                     self.env.ref('maintenance_request.fleet_service_type_noleggio_scorta').id,
                                     self.env.ref(
                                         'maintenance_request.fleet_service_type_disponibilita_mezzo').id])])  # 11,45,46,47
        # Contratti di disponibilità
        contracts_available = self.env['fleet.vehicle.log.contract'].search_read(
            [('vehicle_id.id', '=', vehicle.id), ('state', '=', 'open'),
             ('cost_subtype_id.id', '=', self.env.ref('maintenance_request.fleet_service_type_disponibilita_mezzo').id)])  # 47
        # Contratti di noleggio
        contracts_rent = self.env['fleet.vehicle.log.contract'].search_read(
            [('vehicle_id.id', '=', vehicle.id), ('state', '=', 'open'),
             ('cost_subtype_id.id', '=', self.env.ref('maintenance_request.fleet_service_type_noleggio').id)])  # 11
        # Contratti di proprietà
        contracts_owner = self.env['fleet.vehicle.log.contract'].search_read(
            [('vehicle_id.id', '=', vehicle.id), ('state', '=', 'open'),
             ('cost_subtype_id.id', '=', self.env.ref('maintenance_request.fleet_service_type_proprieta').id)])  # 45
        # Contratti di noleggio scorta
        contracts_rent_stock = self.env['fleet.vehicle.log.contract'].search_read(
            [('vehicle_id.id', '=', vehicle.id), ('state', '=', 'open'), ('cost_subtype_id.id', '=', self.env.ref(
                'maintenance_request.fleet_service_type_noleggio_scorta').id)])  # 46
        _logger.info(f"ID del veicolo: {vehicle.id}")
        _logger.info(f"Numero contratti attivi: {contracts_count}")
        _logger.info(f"Contratti: {contracts}")
        cessato = self.env['fleet.vehicle.log.contract'].search_read(
            [('vehicle_id.id', '=', vehicle.id), ('state', '=', 'open'), ('cost_subtype_id.id', 'in', [
                self.env.ref('maintenance_request.fleet_service_type_noleggio').id,
                self.env.ref('maintenance_request.fleet_service_type_proprieta').id,
                self.env.ref('maintenance_request.fleet_service_type_noleggio_scorta').id,
                self.env.ref('maintenance_request.fleet_service_type_non_contrattualizzato').id])])  # [11,45,46,55]
        flotta = self.env['fleet.vehicle.log.contract'].search_read(
            [('vehicle_id.id', '=', vehicle.id), ('state', '=', 'open'), ('cost_subtype_id.id', 'in', [
                self.env.ref('maintenance_request.fleet_service_type_noleggio').id,
                self.env.ref('maintenance_request.fleet_service_type_proprieta').id])])  # 11,45
        riparazione = self.env['fleet.vehicle.log.contract'].search_read(
            [('vehicle_id.id', '=', vehicle.id), ('state', '=', 'open'), ('cost_subtype_id.id', 'in', [
                self.env.ref('maintenance_request.fleet_service_type_noleggio').id,
                self.env.ref('maintenance_request.fleet_service_type_proprieta').id,
                self.env.ref('maintenance_request.fleet_service_type_noleggio_scorta').id])])  # 11,45,46
        bloccati = self.env['fleet.vehicle.log.services'].search_read(
            [('vehicle_id.id', '=', vehicle.id), ('state', '!=', 'done'), ('block_trip_assignment', '=', True)])
        sostituzione = self.env['fleet.replacement'].search_read(
            [('replacement_fleet_id.id', '=', vehicle.id), ('replacement_start_date', '<', today), '|',
             ('replacement_end_date', '=', False), ('replacement_end_date', '>', today)])
        in_riparazione = self.env['fleet.vehicle.log.contract'].search_read(
            [('vehicle_id.id', '=', vehicle.id), ('state', '=', 'open'), ('cost_subtype_id.id', 'in', [
                self.env.ref('maintenance_request.fleet_service_type_noleggio').id,
                self.env.ref('maintenance_request.fleet_service_type_proprieta').id,
                self.env.ref('maintenance_request.fleet_service_type_noleggio_scorta').id,
                self.env.ref('maintenance_request.fleet_service_type_disponibilita_mezzo').id])])  # 11,45,46,47
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
        # _logger.info(sostituzione)
        _logger.info(f"sostituzione = {sostituzione}")
        _logger.info(f"riparazione = {riparazione}")
        _logger.info(f"bloccati = {bloccati}")
        _logger.info(f"cessato = {cessato}")

        assegnato = ""
        # Mezzi che devono essere con lo stato "Cessato"
        if contracts_count > 0 and cessato == [] and contracts_available == []:
            _logger.info(f"Il mezzo {vehicle.id} deve stare su Cessato")
            veicolo = self.env['fleet.vehicle'].browse(vehicle.id)
            veicolo.write(
                {'state_id': self.env.ref('automatic_fleet_management.fleet_vehicle_state_cessato').id})  # 11 Cessato
            assegnato = "cessato"
        # Mezzi che devono essere con lo stato "Flotta"
        elif contracts_count > 0 and contracts_available != [] and flotta != [] and bloccati == []:
            _logger.info(f"Il mezzo {vehicle.id} deve stare su Flotta")
            veicolo = self.env['fleet.vehicle'].browse(vehicle.id)
            veicolo.write(
                {'state_id': self.env.ref('automatic_fleet_management.fleet_vehicle_state_flotta').id})  # 8 Flotta
            assegnato = "flotta"
        # Mezzi che devono essere con lo stato "Scorta"
        elif contracts_count > 0 and contracts_available != [] and contracts_rent_stock != []:
            _logger.info(f"Il mezzo {vehicle.id} deve stare su Scorta")
            veicolo = self.env['fleet.vehicle'].browse(vehicle.id)
            veicolo.write(
                {'state_id': self.env.ref('automatic_fleet_management.fleet_vehicle_state_scorta').id})  # 5 Scorta
            assegnato = "scorta"
        # Mezzi che devono esserwe con lo stato "Disponibile"
        elif contracts_count > 0 and contracts_available != [] and riparazione == [] and bloccati == [] and sostituzione == []:
            _logger.info(f"Il mezzo {vehicle.id} deve stare su Disponibile")
            veicolo = self.env['fleet.vehicle'].browse(vehicle.id)
            veicolo.write({'state_id': self.env.ref(
                'automatic_fleet_management.fleet_vehicle_state_disponibile').id})  # 12 Disponibile
            assegnato = "disponibile"
        # Mezzi che devono esserwe con lo stato "Indisponibile"
        elif contracts_count > 0 and bloccati != [] and in_riparazione != []:
            _logger.info(f"Il mezzo {vehicle.id} deve stare su Indisponibile")
            veicolo = self.env['fleet.vehicle'].browse(vehicle.id)
            veicolo.write({'state_id': self.env.ref(
                'automatic_fleet_management.fleet_vehicle_state_indisponibile').id})  # 10 Indisponibile
            assegnato = "indisponibile"
        # Mezzi che devono esserwe con lo stato "In riparazione"
        elif contracts_count > 0 and contracts_available == [] and riparazione != [] and bloccati != []:
            _logger.info(f"Il mezzo {vehicle.id} deve stare su In riparazione")
            veicolo = self.env['fleet.vehicle'].browse(vehicle.id)
            veicolo.write({'state_id': self.env.ref(
                'automatic_fleet_management.fleet_vehicle_state_in_riparazione').id})  # 13 In riparazione
            assegnato = "in riparazione"
        # Mezzi che devono essere con lo stato "Sostituzione"
        elif sostituzione != [] and cessato != []:
            _logger.info(f"Il mezzo {vehicle.id} deve stare su Sostituzione")
            veicolo = self.env['fleet.vehicle'].browse(vehicle.id)
            veicolo.write({'state_id': self.env.ref(
                'automatic_fleet_management.fleet_vehicle_state_sostituzione').id})  # 6 Sostituzione
            assegnato = "sostituzione"

        elif contracts_count == 0:
            _logger.info(f"Il mezzo {vehicle.id} deve stare su In arrivo")
            veicolo = self.env['fleet.vehicle'].browse(vehicle.id)
            veicolo.write({'state_id': self.env.ref(
                'automatic_fleet_management.fleet_vehicle_state_in_arrivo').id})  # 9 In arrivo
            assegnato = "In arrivo"


        # PER METTERE SU DISPONIBILE
        elif assegnato == "":
            _logger.info(f"Il mezzo {vehicle.id} non è stato assegnato a nessun gruppo. Verrà segnato IN ARRIVO")
            veicolo = self.env['fleet.vehicle'].browse(vehicle.id)
            veicolo.write({'state_id': self.env.ref(
                'automatic_fleet_management.fleet_vehicle_state_in_arrivo').id})  # 9 In arrivo