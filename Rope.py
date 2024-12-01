#!/usr/bin/env python3

import sys
from rope import Coordinator
from rope.web_server import WebServer

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--web":
        # Web mode
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
        public = "--public" in sys.argv
        server = WebServer()
        print(f"Starting web server on http://localhost:{port}")
        if public:
            print("Initializing public URL via ngrok...")
        server.run(port=port, public=public)
    else:
        # GUI mode
        Coordinator.run()