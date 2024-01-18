import logging, json
from odoo import models, api, fields
from datetime import datetime


_logger = logging.getLogger(__name__)

class FleetVehicleLogContract(models.Model):
    _inherit = 'fleet.vehicle.log.contract'
    
    organization_id = fields.Many2one('res.partner', string='Centro di costo', domain=[('type', '=', 'delivery'), ('is_company', '=', True), ('name', 'ilike', "cdc")], context="{'create': False}")
    expiration_date = fields.Date(
        'Contract Expiration Date',
        default=False,
        help='Date when the coverage of the contract expirates (by default, one year after begin date)')
    cost_frequency = fields.Selection([
        ('no', 'No'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly')
        ], 'Recurring Cost Frequency', default='no', required=True)

        
    @api.model
    def create(self, values):
        # Eseguiamo la creazione del contratto
        new_contract = super(FleetVehicleLogContract, self).create(values)

        # Chiamiamo la tua funzione personalizzata per il nuovo contratto
        _logger.info('HO CREATO IL RECORD')  # Sostituisci con il nome della tua funzione
        _logger.info(values)  # Sostituisci con il nome della tua funzione
        _logger.info(values['organization_id'])  # Sostituisci con il nome della tua funzione
        _logger.info(new_contract.id)  # Sostituisci con il nome della tua funzione
        _logger.info('TEST 1')  # Sostituisci con il nome della tua funzione
        record = self.env['fleet.vehicle.log.contract'].search_read([('id', '=', new_contract.id)])
        _logger.info('TEST 2')  # Sostituisci con il nome della tua funzione
        _logger.info(record)  # Sostituisci con il nome della tua funzione
        _logger.info(record[0]['vehicle_id'][0])  # Sostituisci con il nome della tua funzione

        

        if values['cost_subtype_id'] == 47:
            veicolo = self.env['fleet.vehicle'].browse(record[0]['vehicle_id'][0])
            veicolo.write({'organization_id': values['organization_id']})
            
            # Controllo se c'è un documento di disponibilità in corso e nel caso viene chiuso
            contract = self.env['fleet.vehicle.log.contract'].search([('vehicle_id', '=', record[0]['vehicle_id'][0]),('cost_subtype_id', '=', 47),('expiration_date', '=', False), ('id', '!=', record[0]['id'])])
            contract.write({'expiration_date': datetime.now().date()})
            self.env.user.notify_success(message='Ho chiuso il contratto di disponibilità precedentemente aperto e impostato il centro di costo sul veicolo.')
        # Se il contratto fa parte di una certa selezione procedo con la chimata della funzione di check / update stato veicolo
        if record[0]['cost_subtype_id'][0] in [47,50,5,7,11,46,45,9]:
                another_class_obj = self.env['fleet.vehicle']
                another_class_obj.check_vehicle_status(self.env['fleet.vehicle'].search([('id', '=', record[0]['vehicle_id'][0])]))
                _logger.info("FUNZIONE CHIAMATA")

        return new_contract


    def write(self, vals):
        res = super(FleetVehicleLogContract, self).write(vals)      
        if 'start_date' in vals or 'expiration_date' in vals:
            date_today = fields.Date.today()
            future_contracts, running_contracts, expired_contracts = self.env[self._name], self.env[self._name], self.env[self._name]
            for contract in self.filtered(lambda c: c.start_date and c.state != 'closed'):
                if date_today < contract.start_date:
                    future_contracts |= contract
                elif not contract.expiration_date or contract.start_date <= date_today <= contract.expiration_date:
                    running_contracts |= contract
                else:
                    expired_contracts |= contract
            future_contracts.action_draft()
            running_contracts.action_open()
            expired_contracts.action_expire()
        if vals.get('expiration_date') or vals.get('user_id'):
            self.activity_reschedule(['fleet.mail_act_fleet_contract_to_renew'], date_deadline=vals.get('expiration_date'), new_user_id=vals.get('user_id'))
        # Check/Update status mezzo
        vehicle = self.env['fleet.vehicle.log.contract'].search_read([('id', '=', self.id)])
        _logger.info("1111111111111111111111")
        _logger.info(vehicle)
        if vehicle and vehicle[0]['id']:
            _logger.info("@#@#@#@#@#@#@#")
            _logger.info(vehicle[0]['cost_subtype_id'][0])
            if vehicle[0]['cost_subtype_id'][0] in [47,50,5,7,11,46,45,9]:
                another_class_obj = self.env['fleet.vehicle']
                another_class_obj.check_vehicle_status(self.env['fleet.vehicle'].search([('id', '=', self.vehicle_id.id)]))
                _logger.info("FUNZIONE CHIAMATA")
        return res