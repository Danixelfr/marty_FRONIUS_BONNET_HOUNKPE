from server.http_server import HTTPServer

if __name__ == "__main__":
    server = HTTPServer(host="0.0.0.0", port=8080)
    server.start()
