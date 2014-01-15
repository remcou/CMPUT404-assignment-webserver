# coding: utf-8

import SocketServer
import sys

# Copyright 2014 Remco Uittenbogerd
# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(SocketServer.BaseRequestHandler):
    
    def return_file_or_404(self, filePath):
        try:
            file = open("www" + filePath, 'r')
            data = file.read()
            file.close()
            
            dataType = filePath.split(".")[-1]
            self.return_data(data, dataType)
        except IOError as error:
            print( "IOError: " + error.strerror + "\n" )
            self.return_404()
        
    def return_404(self, additionalInfo=""):
        if( additionalInfo ):
            additionalInfo = "\r\n\r\n" + additionalInfo +  "\r\n\r\n"
            
        self.request.sendall("HTTP/1.1 404 NOT FOUND\r\nContent-Type: text/html; charset=" + sys.getdefaultencoding() + additionalInfo)
        
    def return_data(self, data, dataType):
        self.request.sendall("HTTP/1.1 200 OK\r\nContent-Type: text/" + dataType + "; charset=" + sys.getdefaultencoding() + "\r\n\r\n" + data)
    
    def handle(self):
        data = self.request.recv(1024).strip()
        split = data.split("\r\n")
        
        if( len(split) == 0 ):
            return_404("Error: Invalid request format")
            return
            
        split = split[0].split(" ")
        if( len(split) < 2 ):
            return_404("Error: Invalid request format")
            return
        
        filePath = split[1]
        
        if( filePath.endswith("/") ):
            filePath += "index.html"
            
        # Prevent it from looking for files like "favicon.ico" when accessing through a web browser
        # Also we only want to serve html and css files.
        if( not ( filePath.endswith(".html") or filePath.endswith(".css") ) ):
            self.return_404("We only return html and css files!")
            
        if not self.valid_path(filePath):
            self.return_404("Permission Denied")
            return

        self.return_file_or_404(filePath)

    def valid_path(self, path):
        depth = 0
        split = path.split("/")
        for part in split:
            if( part == ".." ):
                depth -= 1
            else:
                depth += 1

        return depth - 1 >= 0

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    SocketServer.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
