import socket
import re
import sys

if len(sys.argv) is not 2: # test na pocet argumentu
    print("Spatne argumenty.")
    sys.exit(1)
port_arg = int(sys.argv[1])
if not isinstance(port_arg,int) or port_arg < 1024 or port_arg > 65535: # test na port_arg
    print("Spatne cislo portu nebo spatny format cisla portu")
    sys.exit(1)

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port_arg
server_address = ('localhost', port_arg)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

while True:
    # Wait for a connection
    connection = None
    try:
        connection, client_address = sock.accept()
        while True:
            data = connection.recv(512)
            datanew = data.decode("utf-8")
            gethttp = datanew
            gethttp = gethttp.split('\n', 1)
            lajna = gethttp[0]
            words = lajna.split()
            if words[-1] == 'HTTP/1.1' or words[-1] == 'HTTP/1.0':
                version = words[-1] + ' '
            else:
                messageforclient = version + '500 Internal Server Error\r\n\r\n'
                messageforclient = messageforclient.encode()
                connection.sendall(messageforclient)
                break
            
            itisok = re.search('/resolve\\?', datanew)
            itisturbo = re.search('/dns-query\s', datanew)
            if not (itisok) and not (itisturbo):
                messageforclient = version + '400 Bad Request\r\n\r\n'
                messageforclient = messageforclient.encode()
                connection.sendall(messageforclient)
                break
            itisget = re.search('GET (.+?) HTTP', datanew)
            itispost = re.search('POST (.+?) HTTP', datanew)
            if itisget:
                itisget = itisget.group(1)
            elif itispost:
                itispost = itispost.group(1)
            else: 
                messageforclient = version + '405 Method Not Allowed\r\n\r\n'
                messageforclient = messageforclient.encode()
                connection.sendall(messageforclient)
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
                    messageforclient = version + '400 Bad Request\r\n\r\n'
                    messageforclient = messageforclient.encode()
                    connection.sendall(messageforclient)
                    break
                if foundtype == 'A':

                    try:
                        socket.gethostbyname(found)
                        zpravaproklienta = found + ':' + foundtype + '=' + socket.gethostbyname(found) + '\n'
                    except: 
                        zpravaproklienta = version + '404 Not Found.\r\n\r\n'
                        
                elif foundtype == 'PTR':
                    
                    try:
                        socket.gethostbyaddr(found)
                        getnamee = socket.gethostbyaddr(found)
                        zpravaproklienta = found + ':' + foundtype + '=' + getnamee[0] + '\n'
                    except: 
                        zpravaproklienta = version + '404 Not Found.\r\n\r\n'
                        
                if not zpravaproklienta == version + '404 Not Found.\r\n\r\n':
                    messageforclient = version + '200 OK\r\n\r\n' + zpravaproklienta
                else:
                    messageforclient = zpravaproklienta
                messageforclient = messageforclient.encode()
            elif itispost:
        
                groupof = datanew.split('\r\n\r\n', 1)
                groupof = groupof[1].split('\n')
                counter = len(groupof)
                messageforclient = ''
                hlavicka = ''
                for addr in groupof:
                    
                    typeof = re.search(':(.+?)', addr)
                    if typeof:
                        typeof = typeof.group(1)
                    else:
                        continue
                    messagetok = addr + '='
                    
                    iptosolve = re.search('(.+?):PTR$', addr)
                    if iptosolve:
                        addr = iptosolve.group(1)
                        typeof = 'P'
                    else :
                        iptosolve = re.search('(.+?):A$', addr)
                        if iptosolve:
                            addr = iptosolve.group(1)
                            typeof = 'A'
                        else:
                            hlavicka = version + '400 Bad Request\r\n\r\n'
                            continue
                        
                    if typeof == 'A':
                        try:
                            messageforclient = messageforclient + messagetok  + socket.gethostbyname(addr) + '\n'
                        except:
                            hlavicka = version + '404 Not Found.\r\n\r\n'
                    elif typeof == 'P':
                        try:
                            getnamee = socket.gethostbyaddr(addr)
                            messageforclient = messageforclient + messagetok + getnamee[0] +'\n'
                        except:
                            hlavicka = version + '404 Not Found.\r\n\r\n'
                        
                    else:   
                        continue
                if not hlavicka:
                    hlavicka = version + '200 OK\r\n\r\n'
                messageforclient = hlavicka + messageforclient
                messageforclient = messageforclient.encode()
            else :
                messageforclient = version + '400 Bad Request\r\n\r\n'
                messageforclient = messageforclient.encode()
                connection.sendall(messageforclient)
                break
            if data:
                connection.sendall(messageforclient)
                break
            else:
                
                break
    except KeyboardInterrupt:
        try:
            if connection:
                connection.close()
        except: pass
        break
sock.shutdown
sock.close()