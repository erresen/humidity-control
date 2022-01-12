#!/usr/bin/env python3

from http.server import BaseHTTPRequestHandler, HTTPServer

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            #Reading the file
            file_to_open = open('/home/pi/metrics').read()
            self.send_response(200)
        except:
            file_to_open = "File not found"
            self.send_response(404)
        
        self.end_headers()
        self.wfile.write(bytes(file_to_open, 'utf-8'))

with HTTPServer(('', 8000), handler) as server:
    server.serve_forever()