from socket import *
import select
import os
import sys
import time
import queue


def pythonWebServer(host, port):
    webServer = socket(AF_INET, SOCK_STREAM)
    webServer.setblocking(0)
    webServer.bind((host, port))
    webServer.listen(5)
    inputs = [webServer]
    outputs = []
    message_queues = {}

    if(host == '' or host == "localhost"):
        # LOG
        print('Ready to serve on localhost:' + str(port))
    else:
        # LOG
        print('Ready to serve on ' + str(host) + ":" + str(port))

    while inputs:
        readable, writable, exceptional = select.select(inputs, outputs, inputs, 0)
        
        for s in readable:
            if s is webServer:
                connection, addr = webServer.accept()
                connection.setblocking(0)
                inputs.append(connection)
                message_queues[connection] = queue.Queue()
            else:
                msg = s.recv(1024)
                if msg:
                    message_queues[s].put(msg)
                    if s not in outputs:
                        outputs.append(s)
                else:
                    if s in outputs:
                        outputs.remove(s)
                    inputs.remove(s)
                    s.close()
                    del message_queues[s]               
        
        for s in writable:
            try:
                next_msg = message_queues[s].get_nowait()
                if next_msg:
                    filename = next_msg.decode("utf-8").split()[1]
                else:
                    #LOG
                    print("\nClient connection timed out. Exiting now...\n")
                    s.close()
                    time.sleep(3)
                    return
                
                # 400 Bad Request HTTP response
                if(filename == "/"):
                    s.send("HTTP/1.1 400 Bad Request\r\n".encode("utf-8"))
                    #LOG
                    print("400 Bad Request")
                    serverGUI.serverLogs("400 Bad Request")
                    s.close()
                    return
                    
                else:
                    try:
                        htmlFile = open(filename[1:]) # Throws IOError if not found
                        htmlFileContent = htmlFile.read() # HTML file content
                        #LOG
                        print("\nCONTENTS OF THE WEBPAGE:")
                        #LOG
                        print(htmlFileContent)
                        
                        fileLocation = process_http_header(webServer, filename)
                        #LOG
                        print("\nFILE PATH: " + fileLocation)
                        
                        # Connection Succesfull, 200 OK HTTP response
                        s.send("HTTP/1.1 200 OK\r\n".encode("utf-8"))
                        #LOG
                        print("\n200 OK")
                        s.send("Content-Type: text/html\r\n\r\n".encode("utf-8"))
                        #LOG
                        print("Content-type: text/html")
                        s.send(htmlFileContent.encode("utf-8"))
                        
                        # Writing HTML file content to the file at the file location
                        filetoWrite = open(fileLocation, "w")
                        filetoWrite.write(htmlFileContent)
                        filetoWrite.close()

                        #LOG
                        print('\nReady to serve on Port ' + str(port))

                    # 404 Not Found HTTP response    
                    except IOError:
                        s.send("HTTP/1.1 404 Not Found\r\n".encode("utf-8"))
                        #LOG
                        print("404 Not Found\n")
                        s.close()
                        return
                        
            except queue.Empty:
                outputs.remove(s)
        
        for s in exceptional:
            inputs.remove(s)
            if s in outputs:
                outputs.remove(s)
            s.close()
            del message_queues[s]    
        
    webServer.close()   
    
def process_http_header(socket, filename):
    filenameList = filename.split("/")[1:]
    currentDir = os.getcwd()
    staticWebServerDir = currentDir + os.sep + "static"
    for item in filenameList:  
        if item == "" or item == " ":
            break;
        # item is a file name
        if("." in item):
            if not os.path.exists(staticWebServerDir):
                os.makedirs(staticWebServerDir)
            staticWebServerDir = staticWebServerDir + os.sep + item
            if not os.path.exists(staticWebServerDir):
                os.mknod(staticWebServerDir)
        # item is a directory name
        else: 
            staticWebServerDir = staticWebServerDir + os.sep + item
            if not os.path.exists(staticWebServerDir):
                os.makedirs(staticWebServerDir)
      
    return staticWebServerDir
    

pythonWebServer('', 8000)
