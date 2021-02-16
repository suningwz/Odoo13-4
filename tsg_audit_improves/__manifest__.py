{
     'name': 'Tsg Audit',    
     'version' : '1.0',
     'description': 'This app is a task register for all your',
     'author' : 'Andres Peña',
     'website': 'https://www.tsg.net.co/',
     'depends': [
          'stock',
          'project',], 
     'data': [
          'data/sequence.xml',
          'views/audit.xml',
          'security/security.xml',
          'security/ir.model.access.csv',
     ],
     'installable': True,
     'auto_install': False,           
}