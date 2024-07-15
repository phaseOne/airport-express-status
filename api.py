from plistlib import loads, InvalidFileException
from json import dumps
from urllib.error import HTTPError, URLError
from urllib.request import urlopen
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from enum import IntFlag

class AirplayStatusFlags(IntFlag):
    AudioCableIsAttached = 1 << 2
    DeviceSupportsRelay = 1 << 11
    ReceiverSessionIsActive = 1 << 17

class APIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        host = self.path[1:]
        
        print(f"Trying host: {host}")

        if host == 'health':
            self.set_response("OK", 200)
        else:
            
            self.get_status(host)

    def get_status(self, host: str) -> None:
        try:
            with urlopen(f"http://{host}:7000/info", timeout=15) as response:
                content = response.read()
                data = loads(content)
                airplay_status_flags = AirplayStatusFlags(data["statusFlags"])
                self.set_response({flag.name: (flag in airplay_status_flags) for flag in AirplayStatusFlags}, response.status)
        except InvalidFileException as error: 
            self.set_response("Invalid file", 200)
        except HTTPError as error:
            self.set_response(False, error.status)
        except URLError as error:
            self.set_response(False, 500)
        except TimeoutError:
            print("Request timed out")
            self.set_response(False, 408)
           
    def set_response(self, data: dict = {'error': "Unknown error"}, statusCode: int = 500) -> None:
            self.send_response(statusCode)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(dumps(data).encode())


httpd = ThreadingHTTPServer(("0.0.0.0", 8000), APIHandler)
httpd.serve_forever()
