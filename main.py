import uvicorn
import argparse
from app import create_app

app = create_app()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Uvicorn server.")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    args = parser.parse_args()

    uvicorn.run(app, host="127.0.0.1", port=args.port)

# Run the server
# python script_name.py --port 8000