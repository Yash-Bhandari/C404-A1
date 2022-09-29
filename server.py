#  coding: utf-8 
from dataclasses import dataclass, field
import re
import socketserver
import os

# 服务器端
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
class HttpRequest:
    def __init__(self, data: str):
        self.data = data
        self.method = None
        self.path = None
        self.version = None
        lines = self.data.split('\r\n')
        self.method, self.path, self.version = lines[0].split(' ')

@dataclass
class HttpResponse:
    status_code: int
    status_text: str
    headers: dict = field(default_factory=lambda: {'Content-Length':0})
    body: str = ''

    def __str__(self):
        header_lines = [f'{key}: {value}' for key, value in self.headers.items() if value is not None]
        headers = self.status_line() + '\r\n' + '\r\n'.join(header_lines) + '\r\n\r\n'
        return headers + '\r\n' + self.body

    def status_line(self):
        return f"HTTP/1.1 {self.status_code} {self.status_text}"

    def encode(self):
        return bytearray(str(self), 'utf-8')

content_types = {
    '.css': 'text/css',
    '.html': 'text/html'
}

class MyWebServer(socketserver.BaseRequestHandler):

    def handle(self):
        self.data = self.request.recv(1024).strip()
        self.text = self.data.decode('utf-8')
        print("===== INCOMING REQUEST =====")
        print(self.text)
        print("============================")
        response = self.prepare_response()

        print("===== OUTGOING RESPONSE =====")
        print(response)
        print("============================")
        self.request.sendall(response.encode())

    def prepare_response(self) -> HttpResponse:
        request = HttpRequest(self.text)

        if request.method != 'GET':
            return HttpResponse(405, 'METHOD NOT ALLOWED')

        base_dir = os.path.join(os.getcwd(), 'www')
        path = request.path
        if path is None:
            raise Exception

        if path[-1] == '/':
            path += 'index.html'
        path = path[1:]
        _, file_ext = os.path.splitext(path)
        full_path = os.path.join(base_dir, path)
        if os.path.isdir(full_path):
            full_path += '/'
        if  os.path.exists(full_path):
            with open(full_path, 'r') as file:
                lines = file.readlines()
            response = HttpResponse(200, 'OK')
            response.body = '\r\n'.join(lines)
            response.headers['Content-Length'] = len(response.body)
            response.headers['Content-Type'] = content_types.get(file_ext)
            return response
        else:
            return HttpResponse(404, 'Not Found')

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
