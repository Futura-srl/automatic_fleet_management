{
    'name': 'Automatic fleet management',
    'version': '19.0.1.0.0',
    'author': "Luca Cocozza",
    'application': True,
    'description': "Gestione automatica della flotta.",
    'depends': ['fleet', 'maintenance_request'],
    'data': [
        # Settaggi per accesso ai contenuti
        'data/ir.model.access.csv',
        'data/data.xml',
        # Caricamento delle view,
        'view/fleet_vehicle_log_contract_update.xml',
    ],
}
