#!/usr/bin/env python3
"""
Test script for lightweight LLM inference
"""
import torch
import time
import psutil
from transformers import AutoTokenizer, AutoModelForCausalLM, set_seed

def get_memory_usage():
    """Get current memory usage in GB"""
    memory = psutil.virtual_memory()
    return memory.used / (1024**3)

def test_model(model_name, prompt="Hello, how are you?"):
    """Test a model with the given prompt"""
    print(f"\n[TEST] Testing {model_name}")
    print(f"[MEM] Initial memory usage: {get_memory_usage():.1f}GB")
    
    try:
        # Start timing
        start_time = time.time()
        
        print("[LOAD] Loading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        print("[LOAD] Loading model...")
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto"
        )
        
        load_time = time.time() - start_time
        print(f"[TIME] Model loaded in {load_time:.1f}s")
        print(f"[MEM] Memory after loading: {get_memory_usage():.1f}GB")
        
        # Generate response
        print(f"[GEN] Generating response to: '{prompt}'")
        inputs = tokenizer(prompt, return_tensors="pt")
        
        generation_start = time.time()
        
        with torch.no_grad():
            outputs = model.generate(
                inputs.input_ids,
                max_new_tokens=50,
                temperature=0.7,
                pad_token_id=tokenizer.eos_token_id,
                do_sample=True
            )
        
        generation_time = time.time() - generation_start
        
        # Decode response
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        tokens_generated = len(outputs[0]) - len(inputs.input_ids[0])
        tokens_per_second = tokens_generated / generation_time
        
        print(f"[RESULT] Response: {response}")
        print(f"[SPEED] Generated {tokens_generated} tokens in {generation_time:.1f}s ({tokens_per_second:.1f} tok/s)")
        print(f"[MEM] Peak memory usage: {get_memory_usage():.1f}GB")
        
        return True, tokens_per_second
        
    except Exception as e:
        print(f"[ERROR] {e}")
        return False, 0

def main():
    """Test multiple lightweight models"""
    print("=== Local LLM Testing Suite ===")
    print(f"System: {psutil.cpu_count()} cores, {psutil.virtual_memory().total/(1024**3):.1f}GB RAM")
    
    # List of models to test (starting with smallest)
    models_to_test = [
        "microsoft/DialoGPT-small",  # ~117M parameters
        "microsoft/DialoGPT-medium", # ~355M parameters  
        "TinyLlama/TinyLlama-1.1B-Chat-v1.0", # ~1.1B parameters
    ]
    
    results = []
    
    for model_name in models_to_test:
        success, speed = test_model(model_name)
        results.append((model_name, success, speed))
        
        # Memory cleanup
        torch.cuda.empty_cache() if torch.cuda.is_available() else None
        
        print("\n" + "="*60)
    
    # Summary
    print("\n=== RESULTS SUMMARY ===")
    for model, success, speed in results:
        status = "[SUCCESS]" if success else "[FAILED]"
        speed_str = f"({speed:.1f} tok/s)" if success else ""
        print(f"{status} {model} {speed_str}")

if __name__ == "__main__":
    main()