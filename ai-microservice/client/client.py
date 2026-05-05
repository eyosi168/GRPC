import grpc
import time
import inference_pb2
import inference_pb2_grpc

# --- GLOBAL SECURITY SETTINGS ---
# We must pass this key in the metadata for EVERY call, otherwise the server 
# bouncer (interceptor) will reject the request[cite: 1]
AUTH_METADATA = (('authorization', 'Bearer my-secret-key'),)

def run_task_2_unary(stub):
    print("\n" + "="*60)
    print(" TASK 2: UNARY RPC + BONUS DEADLINE TEST")
    print("="*60)
    
    request = inference_pb2.SentimentRequest(text="This should trigger a timeout.")
    
    try:
        print(" Sending request with a 2.0s deadline...")
        # We enforce a strict 2.0-second deadline here[cite: 1]
        response = stub.AnalyzeSentiment(request, timeout=2.0, metadata=AUTH_METADATA)
        print(f" Label: {response.label}")
    except grpc.RpcError as e:
        # We catch the specific error code for a timeout[cite: 1]
        if e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
            print(" [Client] Deadline Exceeded! The server was too slow (as expected).")
        else:
            print(f" gRPC Failed: {e.code()} - {e.details()}")

def run_task_3_server_streaming(stub):
    print("\n" + "="*60)
    print(" TASK 3: SERVER-STREAMING (Secured)")
    print("="*60)
    request = inference_pb2.GenerationRequest(prompt="Explain Docker in one sentence.")
    
    # Passing metadata so the bouncer lets us through[cite: 1]
    responses = stub.StreamTextGeneration(request, metadata=AUTH_METADATA)
    for response in responses:
        print(response.token, end='', flush=True)
    print("\n")

def run_task_4_client_streaming(stub):
    print("\n" + "="*60)
    print(" TASK 4: CLIENT-STREAMING (Secured)")
    print("="*60)
    
    def generate_chunks():
        for chunk in ["gRPC is fast. ", "Nginx balances. ", "Docker scales."]:
            print(f" Sending: {chunk}")
            yield inference_pb2.BatchRequest(chunk=chunk)
            time.sleep(0.5)

    # Passing metadata[cite: 1]
    response = stub.SummarizeBatch(generate_chunks(), metadata=AUTH_METADATA)
    print(f" Summary: {response.summary}")

def run_task_5_bidirectional_streaming(stub):
    print("\n" + "="*60)
    print("TASK 5: BIDIRECTIONAL-STREAMING (Secured)")
    print("="*60)
    
    def generate_messages():
        messages = ["Hello AI!", "How are you?"]
        for m in messages:
            print(f" You: {m}")
            yield inference_pb2.ChatMessage(text=m)
            time.sleep(1)
            
    # Passing metadata[cite: 1]
    responses = stub.ChatAssistant(generate_messages(), metadata=AUTH_METADATA)
    for response in responses:
        print(f" AI: {response.text}")

def run_all_tasks():
    target_address = 'localhost:8080'
    print(f" Connecting to Nginx Load Balancer at {target_address}...")
    
    with grpc.insecure_channel(target_address) as channel:
        stub = inference_pb2_grpc.AIInferenceStub(channel)
        try:
            run_task_2_unary(stub)
            time.sleep(1)
            run_task_3_server_streaming(stub)
            time.sleep(1)
            run_task_4_client_streaming(stub)
            time.sleep(1)
            run_task_5_bidirectional_streaming(stub)
            print("\n All tasks (including bonuses) completed!")
        except grpc.RpcError as e:
            print(f"\n Global gRPC Error: {e.code()}")

if __name__ == '__main__':
    run_all_tasks()