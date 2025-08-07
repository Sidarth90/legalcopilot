#!/usr/bin/env python3
"""
Local LLM Demo Server
FastAPI server with DialoGPT-small for local inference
"""
import torch
import time
import psutil
import asyncio
from typing import Dict, List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM
import uvicorn

# Global variables for model
model = None
tokenizer = None
model_name = "meta-llama/Llama-3.2-1B-Instruct"

class ChatMessage(BaseModel):
    message: str
    max_tokens: Optional[int] = 50
    temperature: Optional[float] = 0.7

class ChatResponse(BaseModel):
    response: str
    tokens_per_second: float
    memory_usage_gb: float
    generation_time: float

def get_memory_usage():
    """Get current memory usage in GB"""
    memory = psutil.virtual_memory()
    return memory.used / (1024**3)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model on startup, cleanup on shutdown"""
    global model, tokenizer
    
    print(f"[STARTUP] Loading {model_name}...")
    start_time = time.time()
    
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float32,
            device_map="auto"
        )
        
        load_time = time.time() - start_time
        print(f"[STARTUP] Model loaded in {load_time:.1f}s")
        print(f"[STARTUP] Memory usage: {get_memory_usage():.1f}GB")
        
    except Exception as e:
        print(f"[ERROR] Failed to load model: {e}")
        raise
    
    yield
    
    # Cleanup
    print("[SHUTDOWN] Cleaning up...")
    del model, tokenizer

# Create FastAPI app with lifespan
app = FastAPI(
    title="Local LLM Demo",
    description="Local inference with Llama 3.2 1B Instruct",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint with basic info"""
    return {
        "name": "Local LLM Demo Server",
        "model": model_name,
        "status": "ready" if model is not None else "loading",
        "memory_usage_gb": get_memory_usage(),
        "system": f"{psutil.cpu_count()} cores, {psutil.virtual_memory().total/(1024**3):.1f}GB RAM"
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy" if model is not None else "loading",
        "model_loaded": model is not None,
        "memory_usage_gb": get_memory_usage(),
        "cpu_percent": psutil.cpu_percent()
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_completion(message: ChatMessage):
    """Generate chat completion"""
    if model is None or tokenizer is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        start_time = time.time()
        
        # Encode input
        inputs = tokenizer(message.message, return_tensors="pt")
        
        # Generate response
        with torch.no_grad():
            outputs = model.generate(
                inputs.input_ids,
                max_new_tokens=message.max_tokens,
                temperature=message.temperature,
                pad_token_id=tokenizer.eos_token_id,
                do_sample=True,
                repetition_penalty=1.2
            )
        
        # Decode response
        full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        response = full_response[len(message.message):].strip()
        
        # Calculate metrics
        generation_time = time.time() - start_time
        tokens_generated = len(outputs[0]) - len(inputs.input_ids[0])
        tokens_per_second = tokens_generated / generation_time if generation_time > 0 else 0
        
        return ChatResponse(
            response=response,
            tokens_per_second=tokens_per_second,
            memory_usage_gb=get_memory_usage(),
            generation_time=generation_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for streaming chat"""
    await websocket.accept()
    
    if model is None or tokenizer is None:
        await websocket.send_json({"error": "Model not loaded"})
        await websocket.close()
        return
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            message = data.get("message", "")
            
            if not message:
                await websocket.send_json({"error": "Empty message"})
                continue
            
            start_time = time.time()
            
            # Send typing indicator
            await websocket.send_json({"status": "generating"})
            
            # Generate response
            inputs = tokenizer(message, return_tensors="pt")
            
            with torch.no_grad():
                outputs = model.generate(
                    inputs.input_ids,
                    max_new_tokens=50,
                    temperature=0.7,
                    pad_token_id=tokenizer.eos_token_id,
                    do_sample=True,
                    repetition_penalty=1.2
                )
            
            # Send response
            full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            response = full_response[len(message):].strip()
            
            generation_time = time.time() - start_time
            tokens_generated = len(outputs[0]) - len(inputs.input_ids[0])
            tokens_per_second = tokens_generated / generation_time if generation_time > 0 else 0
            
            await websocket.send_json({
                "response": response,
                "tokens_per_second": tokens_per_second,
                "memory_usage_gb": get_memory_usage(),
                "generation_time": generation_time
            })
            
    except WebSocketDisconnect:
        print("[WS] Client disconnected")
    except Exception as e:
        await websocket.send_json({"error": str(e)})
        await websocket.close()

@app.get("/demo", response_class=HTMLResponse)
async def demo_page():
    """Simple demo web page"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Local LLM Demo</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            .chat-container { border: 1px solid #ddd; height: 400px; overflow-y: scroll; padding: 10px; margin: 10px 0; }
            .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
            .user { background-color: #e3f2fd; text-align: right; }
            .bot { background-color: #f5f5f5; }
            .stats { font-size: 0.8em; color: #666; margin-top: 5px; }
            input[type="text"] { width: 70%; padding: 10px; }
            button { padding: 10px 20px; margin-left: 10px; }
            .loading { color: #999; font-style: italic; }
        </style>
    </head>
    <body>
        <h1>🤖 Local LLM Demo</h1>
        <p>Powered by Llama 3.2 1B Instruct running locally on your machine</p>
        
        <div class="chat-container" id="chat"></div>
        
        <div>
            <input type="text" id="messageInput" placeholder="Type your message here..." onkeypress="handleKeyPress(event)">
            <button onclick="sendMessage()" id="sendBtn">Send</button>
        </div>
        
        <div id="systemStats" style="margin-top: 20px; padding: 10px; background-color: #f9f9f9; border-radius: 5px;">
            <strong>System Status:</strong> <span id="status">Loading...</span>
        </div>

        <script>
            const chatContainer = document.getElementById('chat');
            const messageInput = document.getElementById('messageInput');
            const sendBtn = document.getElementById('sendBtn');
            const statusSpan = document.getElementById('status');

            // Load system status
            async function loadSystemStatus() {
                try {
                    const response = await fetch('/health');
                    const data = await response.json();
                    statusSpan.innerHTML = `${data.status} | Memory: ${data.memory_usage_gb.toFixed(1)}GB | CPU: ${data.cpu_percent.toFixed(1)}%`;
                } catch (error) {
                    statusSpan.innerHTML = 'Error loading status';
                }
            }

            function addMessage(text, isUser = false, stats = null) {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;
                messageDiv.innerHTML = `
                    <div>${text}</div>
                    ${stats ? `<div class="stats">${stats}</div>` : ''}
                `;
                chatContainer.appendChild(messageDiv);
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }

            async function sendMessage() {
                const message = messageInput.value.trim();
                if (!message) return;

                // Add user message
                addMessage(message, true);
                messageInput.value = '';
                sendBtn.disabled = true;

                // Add loading message
                const loadingDiv = document.createElement('div');
                loadingDiv.className = 'message bot loading';
                loadingDiv.innerHTML = '<div>Thinking...</div>';
                chatContainer.appendChild(loadingDiv);
                chatContainer.scrollTop = chatContainer.scrollHeight;

                try {
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ message: message })
                    });

                    const data = await response.json();
                    
                    // Remove loading message
                    chatContainer.removeChild(loadingDiv);
                    
                    // Add bot response
                    const stats = `${data.tokens_per_second.toFixed(1)} tok/s | ${data.generation_time.toFixed(1)}s | ${data.memory_usage_gb.toFixed(1)}GB`;
                    addMessage(data.response, false, stats);
                    
                } catch (error) {
                    chatContainer.removeChild(loadingDiv);
                    addMessage('Error: ' + error.message, false);
                }

                sendBtn.disabled = false;
                loadSystemStatus(); // Update stats
            }

            function handleKeyPress(event) {
                if (event.key === 'Enter') {
                    sendMessage();
                }
            }

            // Initial load
            loadSystemStatus();
            setInterval(loadSystemStatus, 5000); // Update every 5 seconds
            
            // Welcome message
            addMessage("Hello! I'm a local AI assistant running Llama 3.2 1B Instruct. Ask me anything!", false);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    print("Starting Local LLM Demo Server...")
    print(f"Model: {model_name}")
    print(f"System: {psutil.cpu_count()} cores, {psutil.virtual_memory().total/(1024**3):.1f}GB RAM")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )