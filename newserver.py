import socket
import sys
import re
# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('localhost',9000)
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

while True:
    # Wait for a connection
    connection, client_address = sock.accept()
    try:
        while True:
            data = connection.recv(1024)
            datanew = data.decode("utf-8")
            itisok = re.search('/resolve(.+?)', datanew)
            itisturbo = re.search('/dns-query(.+?)', datanew)
            if not (itisok) and not (itisturbo):
                hovno = '400 Bad Request\r\n\r\n'
                hovno = hovno.encode()
                connection.sendall(hovno)
                break
            itisget = re.search('GET (.+?) HTTP', datanew)
            itispost = re.search('POST (.+?) HTTP', datanew)
            if itisget:
                itisget = itisget.group(1)
            elif itispost:
                itispost = itispost.group(1)
            else: 
                hovno = '400 Bad Request\r\n\r\n'
                hovno = hovno.encode()
                connection.sendall(hovno)
                break
            if itisget:
                
                m = re.search('name=(.+?)&', datanew)
                ipadr = re.search('name=(.+?) HTTP', datanew)
                
                if m:
                    found = m.group(1)
                    n = re.search('type=(.+?) ', datanew)
                    foundtype = n.group(1)
                elif ipadr:
                    foundtype = 'PTR'
                    found = ipadr.group(1)
                else:
                    print('chyba')
                if foundtype == 'A':

                    try:
                        socket.gethostbyname(found)
                        turbink = found + ':' + foundtype + '=' + socket.gethostbyname(found) + '\n'
                    except: 
                        turbink = '404 Not Found.\r\n\r\n'
                        
                elif foundtype == 'PTR':
                    
                    try:
                        socket.gethostbyaddr(found)
                        picakurva = socket.gethostbyaddr(found)
                        turbink = found + ':' + foundtype + '=' + picakurva[0] + '\n'
                    except: 
                        turbink = '404 Not Found.\r\n\r\n'
                        
                if not turbink == '404 Not Found.\r\n\r\n':
                    hovno = 'HTTP/1.1 200 OK\r\n\r\n' + turbink
                else:
                    hovno = turbink
                hovno = hovno.encode()
            elif itispost:
        
                groupof = datanew.split('\r\n\r\n', 1)
                groupof = groupof[1].split('\n')
                counter = len(groupof)
                hovno = ''
                
                for addr in groupof:
                    
                    typeof = re.search(':(.+?)', addr)
                    if typeof:
                        typeof = typeof.group(1)
                    else:
                        continue
                    kurvicka = addr + '='
                
                    jebicka = re.search('(.+?):PTR', addr)
                    if jebicka:
                        addr = jebicka.group(1)
                        typeof = 'P'
                    else :
                        jebicka = re.search('(.+?):A', addr)
                        if jebicka:
                            addr = jebicka.group(1)
                            typeof = 'A'
                        else:
                            break
                        
                    if typeof == 'A':
                        hovno = hovno + kurvicka  + socket.gethostbyname(addr) + '\n'
                        
                    elif typeof == 'P':
                        picakurva = socket.gethostbyaddr(addr)
                        hovno = hovno + kurvicka + picakurva[0] +'\n'
                        
                    else:
                        print('zmrde')
                hovno = 'HTTP/1.1 200 OK\r\n\r\n' + hovno
                hovno = hovno.encode()
            else :
                hovno = '400 Bad Request\r\n\r\n'
                hovno = hovno.encode()
                connection.sendall(hovno)
                break
            if data:
                connection.sendall(hovno)
                break
            else:
                
                break
          
    finally:
        # Clean up the connection
        connection.close()