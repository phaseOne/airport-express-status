import plistlib
import json
from urllib.error import HTTPError, URLError
from urllib.request import urlopen
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler


class APIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        host = self.path[1:]
        
        print(f"Trying host: {host}")

        if host == 'health':
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"Status": "OK"}).encode())
        else:
            (status, statusCode) = self.get_status(host)
            self.send_response(statusCode)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"Status": status}).encode())

    def get_status(self, host):
        try:
            with urlopen(f"http://{host}:7000/info", timeout=60) as response:
                content = response.read()
                data = plistlib.loads(content)
                return (data["statusFlags"] > 2000, response.status)
        except HTTPError as error:
            print(error.status, error.reason)
            return (False, error.status)
        except URLError as error:
            print(error.reason)
            return (False, "500")
        except TimeoutError:
            print("Request timed out")
            return (False, "408")

httpd = ThreadingHTTPServer(("0.0.0.0", 8000), APIHandler)
httpd.serve_forever()
