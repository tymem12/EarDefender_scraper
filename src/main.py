import uvicorn
from api.api import app
import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    uvicorn.run(app, host="0.0.0.0", port=8000)