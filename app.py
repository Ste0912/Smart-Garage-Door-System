from dotenv import load_dotenv
load_dotenv()

import os, atexit
from config.utils import configure, raise_error
from config.FlaskServer import FlaskServer

if __name__ == "__main__":
    try:
        configure()
        print("Starting Flask server...")
        # Start Flask server
        server = FlaskServer()
        # Run the server
        server.run(host=os.getenv("FLASK_HOST"), port=int(os.getenv("FLASK_PORT")))
    except Exception as e:
        raise_error(e, __file__, "main", [])