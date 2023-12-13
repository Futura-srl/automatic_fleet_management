{
    'name': 'Automatic fleet management',
    'version': '16',
    'author': "Luca Cocozza",
    'application': True,
    'description': "Gestione automatica della flotta.",
    'depends': ['fleet'],
    'data': [
        # # Settaggi per accesso ai contenuti
        'data/ir.model.access.csv',
        # # Caricamento delle view,
        'view/fleet_vehicle_log_service_update.xml',
    ],
}
