#!/usr/bin/env python3
"""
Simple test server to verify Flask is working
"""
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return '<h1>Contract Explainer Test Server</h1><p>Flask is working!</p>'

if __name__ == '__main__':
    print("Testing Flask on port 5001...")
    app.run(debug=True, host='localhost', port=5001)