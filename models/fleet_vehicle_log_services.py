import logging, json
from odoo import models, api, fields
from datetime import datetime


_logger = logging.getLogger(__name__)

class FleetVehicleLogServices(models.Model):
    _inherit = 'fleet.vehicle.log.services'
    
    block_trip_assignment = fields.Boolean('Block trip assignment', index=True, tracking=True)

    
    @api.model_create_multi
    def create(self, vals_list):
        _logger.info("KKKKKKKKKKKKKKKKKKKKKKKKKKKK")
        for data in vals_list:
            if 'odometer' in data and not data['odometer']:
                # if received value for odometer is 0, then remove it from the
                # data as it would result to the creation of a
                # odometer log with 0, which is to be avoided
                del data['odometer']
        res = super(FleetVehicleLogServices, self).create(vals_list)
        another_class_obj = self.env['fleet.vehicle']
        for record in vals_list:
            another_class_obj.check_vehicle_status(self.env['fleet.vehicle'].search([('id', '=', record['vehicle_id'])]))
            status = self.env['fleet.vehicle'].search_read([('id', '=', record['vehicle_id'])])
            state = status[0]['state_id'][1]
            self.env.user.notify_success(message=f"Il mezzo è stato messo sullo stato: {state}")
        return res

    def write(self, vals_list):
        res = super(FleetVehicleLogServices, self).write(vals_list)
        if 'block_trip_assignment' in vals_list and vals_list['block_trip_assignment']:
            if vals_list['block_trip_assignment'] == False or vals_list['block_trip_assignment'] == True:
                service = self.env['fleet.vehicle.log.services'].search_read([('id', '=', self['id'])])
                another_class_obj = self.env['fleet.vehicle']
                another_class_obj.check_vehicle_status(self.env['fleet.vehicle'].search([('id', '=', service[0]['vehicle_id'][0])]))
                status = self.env['fleet.vehicle'].search_read([('id', '=', service[0]['vehicle_id'][0])])
                state = status[0]['state_id'][1]
                self.env.user.notify_success(message=f"Il mezzo è stato messo sullo stato: {state}")
        return res

    