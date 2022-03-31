from http.server import BaseHTTPRequestHandler, HTTPServer

hostName = "localhost"
serverPort = 80

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        # Cache request
        path = self.path

        # Validate request path, and set type
        if path == "/resources/index.html":
            type = "text/html"
        elif path == "/resources/script.js":
            type = "text/javascript"
        elif path == "/resources/style.css":
            type = "text/css"
        elif path == "/favicon.ico":
            path = "/resources/favicon.ico"
            type = "image/x-icon"
        else:
            # Wild-card/default
            if not path == "/":
                print("UNRECONGIZED REQUEST: ", path)
                
            path = "/resources/index.html"
            type = "text/html"
        
        # Set header with content type
        self.send_response(200)
        self.send_header("Content-type", type)
        self.end_headers()
        
        # Open the file, read bytes, serve
        with open(path[1:], 'rb') as file: 
            self.wfile.write(file.read()) # Send

# Main()
if __name__ == "__main__":    
    webServer = HTTPServer((hostName, serverPort), MyServer)

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")