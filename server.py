#  coding: utf-8 
from genericpath import isdir
import socketserver

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
import os

class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)
        #self.request.sendall(bytearray("OK",'utf-8'))
        #print(self.data)
        #for word in self.data.decode("utf-8").split("\r\n"):
        #    print(word)

        response = "HTTP/1.1 "
        headers = self.data.decode("utf-8").split("\r\n")
        if "GET" in headers[0]:
            path = headers[0].split(" ")[1]
            normpath, code = self.validate_path(path)
            if code == 200:
                # 200 OK
                response += "200 OK\r\n"
                response += self.get_resource(normpath)
            elif code == 301:
                # 301 Moved
                response += ("301 Moved Permanently\r\n" + "Location: www{}/\n\r".format(os.path.normpath(path)))
                response += self.get_resource(normpath)
            elif code == 404:
                # 404 Path Not Found
                response += "404 Not Found\r\n"
        else:
            # 405 Method not allowed
            response += "405 Method Not Allowed\r\n"
        self.request.sendall(bytearray(response), "utf-8")
    
    def validate_path(self, path):
        # avoid accessing the parent folders
        normpath = "www" + os.path.normpath(path)
        # assume that the page doesn't exist, thus init with 404
        code = 404 
        if os.path.isdir(normpath) and normpath[-1] != '/':
            normpath += '/index.html'
            code = 301
        elif os.path.isfile(normpath):
            code = 200
        elif os.path.isdir(normpath):
            normpath += 'index.html'
            code = 200
        else:
            code = 404
        #print(normpath)
        #print(code)
        return normpath, code

    def get_resource(self, path):
        resource_header = "Content-Type: {}; charset=UTF-8\r\n\r\n"
        extension = path.split(".")[1]
        if extension == "html":
            resource_header = resource_header.format("text/html")
        elif extension == "css":
            resource_header = resource_header.format("text/css")
        else:
            resource_header = resource_header.format("application/octet-stream")
        resource = resource_header + self.get_file_content(path)
        return resource

    def get_file_content(self, path):
        ret = ""
        with open(path) as f:
            for line in f:
                ret += (line + "\r\n")
        return ret


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
