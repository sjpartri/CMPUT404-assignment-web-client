#!/usr/bin/env python
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
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

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib
import urlparse

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):

    def connect(self, host, port):
        # use sockets!

        #Attempt to create a socket
        try:
            clientSocket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as msg:
            print "Failed to create socket"
            print ("Error code: " +str(msg[0]) + ", Error message: "+msg[1])
            sys.exit()
        
        #Attempt to connect to server
        try:
            clientSocket.connect((host, port)) 
        except socket.timeout as msg:
            print "Failed to create socket"
            print ("Error code: " +str(msg[0]) + ", Error message: "+msg[1])

        return clientSocket

    def get_code(self, data):
        parameters = data.split('\r\n\r\n')
        

        #parse the header to get the code
        headers = parameters[0].split('\r\n')
        code_block = headers[0].split(" ")
        code_number = int(code_block[1])
        return code_number

    def get_headers(self,data):
        return None

    def get_body(self, data):
        parameters = data.split("\r\n\r\n")
       
        body = parameters[1]
        return body

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)

    # Give a url in format: http://www.test.com:port/path/
    # Get ['http', "test.com:port",'path0','path1','etc']
    def url_parser(self, url):
    
        host=""
        port=80
        path =""

        if ("http://") not in url:
             url="http://"+url
        
        url_parsed = url.split("/")


        #Remove the empty string that may have concurred when splitting
        while '' in url_parsed:
             url_parsed.remove('')
        

        #If we have port number
        if(len(url_parsed))>=2:
            if ":" in url_parsed[1]:
                host_port = url_parsed[1].split(":")
                host = host_port[0]
                port = host_port[1]
               
        #No port number
            elif ":" not in url_parsed[1]:
                host = url_parsed[1]
                

       #Check if there is  path
        for x in range (2, len(url_parsed)):
            part = "/"+url_parsed[x]
            path += part

        #port needs to be casted in order for it to work with socket.connect()
        port = int(port)

        return host,port,path

    def sendData(self,clientSocket,method,host,path,encoding):
        try:
            if (method == "GET"):
                request =  method+" /"+path+" HTTP/1.1\r\n" \
                           "Host: "+host+"\r\n"\
                           "Accept:*/*\r\n"\
                           "Connection:close\r\n\r\n"

            elif (method == "POST"):
                request =  method+" /"+path+" HTTP/1.1\r\n" \
                           "Host: "+host+"\r\n"\
                           "Accept:*/*\r\n"\
                           "Content-Length: "+str(len(encoding))+"\r\n"\
                           "Content-Type: application/x-www-form-urlencoded\r\n\r\n"+encoding+\
                           "Connection:close\r\n\r\n"
               
            clientSocket.sendall(request)
            recv_data = self.recvall(clientSocket)


         
        except socket.error as msg:
            print("Message Failed to Send")
            print ("Error code: " +str(msg[0]) + ", Error message: "+msg[1])

        return recv_data

    def GET(self, url, args=None):
        code = 500
        body = ""
     
        host,port,path = self.url_parser(url)
       
        #Connect with the server
        clientSocket=self.connect(host,port)

        #Get data from server
        recv_data = self.sendData(clientSocket,"GET",host,path,"N/A")

        #Parse Recieved Data
        code = self.get_code(recv_data)
        body = self.get_body(recv_data)

       

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""
        encoding = ""
        host,port,path = self.url_parser(url)

        #Connect with the server
        clientSocket=self.connect(host,port)

        #Check if encoding is necessary
        if args != None:
            encoding = urllib.urlencode(args)

        #Get data from server
        recv_data = self.sendData(clientSocket,"POST",host,path,encoding)
     
        code=self.get_code(recv_data)
        body=self.get_body(recv_data)


        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command( sys.argv[2], sys.argv[1] )
    else:
        print client.command( sys.argv[1],command )   
