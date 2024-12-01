from flask import Flask, render_template, request, jsonify, send_file
import os
import torch
from rope.Dicts import DEFAULT_DATA
import rope.Models as Models
import rope.VideoManager as VM
from pyngrok import ngrok

app = Flask(__name__, 
    template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
    static_folder=os.path.join(os.path.dirname(__file__), 'static'))

class WebServer:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        if self.device == "cuda":
            DEFAULT_DATA['ProvidersPriorityTextSelMode'] = 'CUDA'
            DEFAULT_DATA['ProvidersPriorityTextSelModes'] = ['CUDA', 'TensorRT', 'TensorRT-Engine', 'CPU']
        else:
            DEFAULT_DATA['ProvidersPriorityTextSelMode'] = 'CPU'
            DEFAULT_DATA['ProvidersPriorityTextSelModes'] = ['CPU']
        
        self.models = Models.Models(device=self.device)
        self.vm = VM.VideoManager(self.models)
        self.setup_routes()
        self.ngrok_tunnel = None

    def setup_routes(self):
        @app.route('/')
        def home():
            return render_template('index.html')

        @app.route('/api/load_target_video', methods=['POST'])
        def load_target_video():
            video_path = request.json.get('path')
            self.vm.load_target_video(video_path)
            return jsonify({"status": "success"})

        @app.route('/api/load_target_image', methods=['POST'])
        def load_target_image():
            image_path = request.json.get('path')
            self.vm.load_target_image(image_path)
            return jsonify({"status": "success"})

        @app.route('/api/play_video', methods=['POST'])
        def play_video():
            state = request.json.get('state')
            self.vm.play_video(state)
            return jsonify({"status": "success"})

        @app.route('/api/get_frame')
        def get_frame():
            frame = self.vm.get_current_frame()
            if frame is not None:
                return send_file(frame, mimetype='image/jpeg')
            return jsonify({"error": "No frame available"})

        @app.route('/api/target_faces', methods=['POST'])
        def target_faces():
            faces = request.json.get('faces')
            self.vm.assign_found_faces(faces)
            return jsonify({"status": "success"})

        @app.route('/api/parameters', methods=['POST'])
        def update_parameters():
            params = request.json
            self.vm.parameters = params
            return jsonify({"status": "success"})

    def start_ngrok(self, port):
        try:
            self.ngrok_tunnel = ngrok.connect(port)
            print(f"\nPublic URL: {self.ngrok_tunnel.public_url}")
            return self.ngrok_tunnel.public_url
        except Exception as e:
            print(f"Failed to start ngrok: {str(e)}")
            return None

    def stop_ngrok(self):
        if self.ngrok_tunnel:
            ngrok.disconnect(self.ngrok_tunnel.public_url)
            self.ngrok_tunnel = None

    def run(self, host='localhost', port=5000, public=False):
        if public:
            public_url = self.start_ngrok(port)
            if not public_url:
                print("Warning: Could not start ngrok tunnel. Running in local mode only.")
        try:
            app.run(host=host, port=port, debug=False)
        finally:
            if public:
                self.stop_ngrok() 