#!/bin/bash

# Create necessary directories
mkdir -p temp
mkdir -p data

# Start Streamlit
streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0 --browser.serverAddress=0.0.0.0 --server.enableCORS=false --server.enableXsrfProtection=false 