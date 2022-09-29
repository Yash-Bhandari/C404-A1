#  coding: utf-8 
from dataclasses import dataclass, field
import re
import socketserver
import os

# Copyright 2022 Yashaswi Bhandari
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
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
            path = '/'

        if path[-1] == '/':
            path += 'index.html'
        path = path[1:]
        _, file_ext = os.path.splitext(path)
        full_path = os.path.abspath(os.path.join(base_dir, path))
        if not full_path.startswith(base_dir):
            return HttpResponse(404, 'NOT FOUND')
        if os.path.isdir(full_path):
            response = HttpResponse(303, 'SEE OTHER')
            # response.headers['Location'] = self.request
            response.headers['Location'] = path + '/'
            return response
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
