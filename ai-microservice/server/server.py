import grpc
from concurrent import futures
import os
import time  # Required for Bonus Task 2 (Deadlines)
from groq import Groq
from dotenv import load_dotenv
from pathlib import Path

# Import the generated gRPC code
import inference_pb2
import inference_pb2_grpc

# --- ENVIRONMENT SETUP ---
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# --- BONUS TASK 1: gRPC SERVER INTERCEPTOR (The Bouncer) ---
class AuthInterceptor(grpc.ServerInterceptor):
    def __init__(self, key):
        self._key = f"Bearer {key}"

    def intercept_service(self, continuation, handler_call_details):
        # 1. Extract metadata from the incoming call
        metadata = dict(handler_call_details.invocation_metadata)
        
        # 2. Check if the 'authorization' key matches our secret key
        # If it doesn't match or is missing, we abort the call immediately
        if metadata.get('authorization') != self._key:
            print(" [Bouncer] Security Alert: Unauthorized access attempt blocked!")
            
            # This context.abort stops the request before it ever hits your AI logic
            context = grpc.ServicerContext()
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "Invalid or missing API Key")
        
        # 3. If valid, let the request continue to the actual service handler
        return continuation(handler_call_details)

class AIInferenceService(inference_pb2_grpc.AIInferenceServicer):
    
    def __init__(self):
        self.api_key = os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            print(" ERROR: GROQ_API_KEY not found!")
        self.client = Groq(api_key=self.api_key)

    # --- Task 2: Unary RPC (Sentiment Analysis) with Bonus Deadline ---
    def AnalyzeSentiment(self, request, context):
        print(f"[Server] Task 2 - Received: '{request.text[:30]}...'")
        
        # --- BONUS TASK 2: Simulating a slow response ---
        # We intentionally sleep for 3 seconds to trigger the client's 2.0s deadline[cite: 1]
        print("⏳ [Server] Simulating heavy AI processing... (3.0s delay)")
        time.sleep(3) 
        
        try:
            completion = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "Analyze sentiment. Return ONLY: LABEL, SCORE. Labels: POSITIVE, NEGATIVE, NEUTRAL."},
                    {"role": "user", "content": request.text}
                ]
            )
            raw_text = completion.choices[0].message.content.strip()
            
            if ',' in raw_text:
                parts = raw_text.split(',')
                label, score = parts[0].strip().upper(), float(parts[1].strip())
            else:
                label = "POSITIVE" if "POSITIVE" in raw_text.upper() else "NEUTRAL"
                score = 0.85
            
            return inference_pb2.SentimentResponse(label=label, confidence_score=score)
        except Exception as e:
            print(f"Error in Task 2: {e}")
            return inference_pb2.SentimentResponse(label="ERROR", confidence_score=0.0)

    # --- Task 3: Server-Streaming RPC ---
    def StreamTextGeneration(self, request, context):
        print(f"[Server] Task 3 - Streaming for: '{request.prompt}'")
        try:
            stream = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": request.prompt}],
                stream=True,
            )
            for chunk in stream:
                token = chunk.choices[0].delta.content
                if token:
                    yield inference_pb2.GenerationResponse(token=token)
        except Exception as e:
            print(f"Error in Task 3: {e}")

    # --- Task 4: Client-Streaming RPC ---
    def SummarizeBatch(self, request_iterator, context):
        print("[Server] Task 4 - Aggregating chunks...")
        full_text = ""
        for request in request_iterator:
            full_text += request.chunk
        
        try:
            completion = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": f"Summarize this:\n\n{full_text}"}]
            )
            return inference_pb2.BatchResponse(summary=completion.choices[0].message.content)
        except Exception as e:
            return inference_pb2.BatchResponse(summary="Error generating summary.")

    # --- Task 5: Bidirectional-Streaming RPC ---
    def ChatAssistant(self, request_iterator, context):
        print("[Server] Task 5 - Chat Session Started")
        history = []
        for message in request_iterator:
            history.append({"role": "user", "content": message.text})
            try:
                completion = self.client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=history
                )
                resp = completion.choices[0].message.content
                history.append({"role": "assistant", "content": resp})
                yield inference_pb2.ChatMessage(text=resp)
            except Exception as e:
                yield inference_pb2.ChatMessage(text="Chat Error.")

def serve():
    # 1. Create the Interceptor with our mock secret key[cite: 1]
    interceptor = AuthInterceptor(key="my-secret-key")
    
    # 2. Attach the interceptor to the server[cite: 1]
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        interceptors=[interceptor]
    )
    
    inference_pb2_grpc.add_AIInferenceServicer_to_server(AIInferenceService(), server)
    server.add_insecure_port('[::]:50051')
    print(" gRPC AI Server (SECURED) starting on port 50051...")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()