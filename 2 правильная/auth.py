import cherrypy
from cherrypy.lib import auth_basic

USERS = {'jon': 'secret'}

def validate_password(username, password):
    if username in USERS and USERS[username] == password:
       return True
    return False

conf = {
    '/': {
       'tools.auth_basic.on': True,
       'tools.auth_basic.realm': 'localhost',
       'tools.auth_basic.checkpassword': validate_password
    }
}

if __name__ == '__main__':

    cherrypy.config.update({
        'server.socket_host': '127.0.0.1',
        'server.socket_port': 8080,
    })

    cherrypy.engine.start()