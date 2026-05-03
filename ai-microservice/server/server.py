import grpc
from concurrent import futures
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Import the generated gRPC code
import inference_pb2
import inference_pb2_grpc

# Load environment variables from the .env file
load_dotenv()

# Configure the Gemini API
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
# Using the flash model for fast inference
model = genai.GenerativeModel('gemini-2.5-flash') 

class AIInferenceService(inference_pb2_grpc.AIInferenceServicer):
    
    # --- Task 2: Unary RPC (Sentiment Analysis) ---
    def AnalyzeSentiment(self, request, context):
        print(f"[Server] Received Sentiment Request: '{request.text}'")
        
        # We instruct Gemini to return a strict format so we can parse it
        prompt = f"""
        Analyze the sentiment of the following text. 
        Return ONLY a single line with the label (POSITIVE, NEGATIVE, or NEUTRAL) 
        and a confidence score (0.0 to 1.0) separated by a comma.
        Example: POSITIVE, 0.95
        
        Text: '{request.text}'
        """
        
        try:
            # Call the Gemini API
            response = model.generate_content(prompt)
            
            # Parse the response (e.g., "POSITIVE, 0.95")
            parts = response.text.strip().split(',')
            label = parts[0].strip().upper()
            score = float(parts[1].strip())
            
        except Exception as e:
            print(f"[Server] Error calling Gemini: {e}")
            label = "ERROR"
            score = 0.0

        print(f"[Server] AI Responded - Label: {label}, Score: {score}")
        
        # Return the strictly typed protobuf response
        return inference_pb2.SentimentResponse(
            label=label,
            confidence_score=score
        )

# --- Server Startup Logic ---
def serve():
    # Create a gRPC server with a thread pool
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Attach our AI service to the server
    inference_pb2_grpc.add_AIInferenceServicer_to_server(AIInferenceService(), server)
    
    # Listen on port 50051 (standard gRPC port)
    server.add_insecure_port('[::]:50051')
    print("🚀 gRPC AI Microservice running on port 50051...")
    
    # Start the server and keep it running
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()