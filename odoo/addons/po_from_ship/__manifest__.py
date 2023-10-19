# -*- coding: utf-8 -*-

{   
    'name': 'Purchase order from Picking/Incoming Shipment/Delivery Order',
    'version': '1.0',
    'category': 'website',
    'license': 'OPL-1',
    'summary': """Create purchase order from delivery order & picking""", 
    'description': """


        po from picking & delivery order
        purchase from picking & delivery order
        create po from picking & delivery order
        create purchase from picking & delivery order
        create purchase order from picking & delivery order
        picking & delivery order to purchase
        picking & delivery order to po 
        one click po generate
        picking & delivery order to po automation

        po from picking & incoming shipment
        purchase from picking & incoming shipment
        create po from picking & incoming shipment
        create purchase from picking & incoming shipment
        create purchase order from picking & incoming shipment
        picking & incoming shipment to purchase
        picking & incoming shipment to po 
        one click po generate
        picking & incoming shipment to po automation
        
        

    """,  
    'depends': ['purchase_stock'],    
    'data' : [
        'view/picking.xml',
    ],
    
    'images': ['static/description/main_screen.png'],      
    'author': 'Craftsync Technologies',
    'website': 'https://www.craftsync.com',
    'maintainer': 'Craftsync Technologies',
    'installable': True,
    'currency': 'EUR',
    'price': 9.99,
    'auto_install': False,
    'application': True,
          
}
