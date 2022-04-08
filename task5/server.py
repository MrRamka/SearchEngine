from http.server import HTTPServer, BaseHTTPRequestHandler
from jinja2 import Environment, FileSystemLoader

from task5.index import SearchHelper

env = Environment(loader=FileSystemLoader('templates'))
indexes = "../task3/index.json"
files_path = "../task1/task1/index.json"

helper = SearchHelper(indexes, files_path)


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self.set_headers()
        template = env.get_template('index.html')
        self.wfile.write(template.render().encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        template = env.get_template('index.html')
        self.set_headers()
        if content_length == 0:
            self.wfile.write(template.render(result=[], isEmpty=True).encode('utf-8'))
        else:
            try:
                query = self.rfile.read(content_length).decode('utf-8').split('=')[1]
                if len(query) != 0:
                    result = helper.search(query)
                    print(result)
                    self.wfile.write(template.render(result=result, query=query).encode('utf-8'))
                else:
                    self.wfile.write(template.render(result=[], isEmpty=True).encode('utf-8'))
            except OSError:
                self.wfile.write(template.render(result=[], isError=True).encode('utf-8'))


httpd = HTTPServer(('localhost', 8000), SimpleHTTPRequestHandler)
httpd.serve_forever()
