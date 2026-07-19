import uvicorn
import os
import sys

if __name__ == "__main__":
    # Add current directory to python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    os.environ["PYTHONPATH"] = current_dir

    print("Starting SCODE Recommender API server...")
    uvicorn.run("api.main:app", host="0.0.0.0", port=8080, reload=True)
