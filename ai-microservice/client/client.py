import grpc

# Import the generated gRPC code
import inference_pb2
import inference_pb2_grpc

def run_client():
    # 1. Open a channel to the server
    print("🔌 Connecting to gRPC server on localhost:50051...")
    
    # We use insecure_channel because we aren't setting up SSL/TLS certificates for local testing
    with grpc.insecure_channel('localhost:50051') as channel:
        
        # 2. Create the "Stub" (This is the client object that knows about your server's methods)
        stub = inference_pb2_grpc.AIInferenceStub(channel)
        
        # 3. Create the exact Protobuf request object
        # We will send it a highly positive sentence to test the AI
        test_sentence = "After hours of debugging, my code finally works and I am absolutely thrilled!"
        
        request = inference_pb2.SentimentRequest(
            text=test_sentence
        )
        
        print(f"📤 Sending request to server: '{test_sentence}'\n")
        
        # 4. Call the AnalyzeSentiment method on the server
        try:
            response = stub.AnalyzeSentiment(request)
            
            # 5. Print out the structured response we got back!
            print("✨ --- Response from Gemini --- ✨")
            print(f"Label: {response.label}")
            print(f"Confidence: {response.confidence_score}")
            print("----------------------------------")
            
        except grpc.RpcError as e:
            print(f"❌ gRPC Failed: {e.code()} - {e.details()}")

if __name__ == '__main__':
    run_client()