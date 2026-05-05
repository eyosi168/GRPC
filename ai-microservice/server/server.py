import grpc
from concurrent import futures
import os
from groq import Groq
from dotenv import load_dotenv
from pathlib import Path

# Import the generated gRPC code
import inference_pb2
import inference_pb2_grpc

# --- ENVIRONMENT FIX ---
# This looks for the .env file in the parent directory if it's not found locally
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Verify the key is actually loading (printing just the prefix for safety)
api_key = os.environ.get("GROQ_API_KEY")
if api_key:
    print(f"✅ API Key loaded: {api_key[:6]}...")
else:
    print("❌ ERROR: GROQ_API_KEY not found in environment!")

class AIInferenceService(inference_pb2_grpc.AIInferenceServicer):
    
    def AnalyzeSentiment(self, request, context):
        print(f"[Server] Received Sentiment Request: '{request.text}'")
        
        try:
            # Task 2: Implement Unary RPC (Sentiment Analysis)
            # Initializing inside the method to ensure thread-safety
            client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": "Analyze sentiment. Return ONLY: LABEL, SCORE. Labels: POSITIVE, NEGATIVE, NEUTRAL."
                    },
                    {
                        "role": "user",
                        "content": request.text
                    }
                ]
            )
            
            raw_text = completion.choices[0].message.content.strip()
            print(f"[Server] Groq Raw Output: {raw_text}")
            
            # Robust Parsing for the gRPC response[cite: 1]
            if ',' in raw_text:
                parts = raw_text.split(',')
                label = parts[0].strip().upper()
                score = float(parts[1].strip())
            else:
                label = "POSITIVE" if "POSITIVE" in raw_text.upper() else "NEUTRAL"
                score = 0.9
            
        except Exception as e:
            print(f"[Server] Error calling Groq: {e}")
            label = "ERROR"
            score = 0.0

        print(f"[Server] AI Responded - Label: {label}, Score: {score}")
        
        # Return the strictly typed protobuf response[cite: 1]
        return inference_pb2.SentimentResponse(
            label=label,
            confidence_score=score
        )

def serve():
    # gRPC server uses HTTP/2 for high-performance AI inference[cite: 1]
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    inference_pb2_grpc.add_AIInferenceServicer_to_server(AIInferenceService(), server)
    
    # Listening on port 50051 as required by the task[cite: 1]
    server.add_insecure_port('[::]:50051')
    print("🚀 gRPC AI Microservice (Groq) running on port 50051...")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()