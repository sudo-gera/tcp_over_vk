from http.server import BaseHTTPRequestHandler, HTTPServer
import time
from urllib.request import urlopen
from ic import ic
import traceback
import server_example
def send_loop(q,port):
    while 1:
        try:
            data=q.get()
            # ic(data)
            time.sleep(1)
            urlopen(f'''http://localhost:{port}''',data=data).read()
        except Exception:
            print(traceback.format_exc())


def recv_loop(q,port):
    hostName = "0.0.0.0"
    hostPort = port

    class MyServer(BaseHTTPRequestHandler):
        def do_POST(self):
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            lenn=int(self.headers['Content-Length'])
            data=self.rfile.read(lenn)
            # ic(data)
            q.put(data)

    myServer = HTTPServer((hostName, hostPort), MyServer)
    print(time.asctime(), "Server Starts - %s:%s" % (hostName, hostPort))

    try:
        myServer.serve_forever()
    except KeyboardInterrupt:
        print(traceback.format_exc())
    myServer.server_close()
    print(time.asctime(), "Server Stops - %s:%s" % (hostName, hostPort))
