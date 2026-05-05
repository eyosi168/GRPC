📝 The README.md File
You need this for your Git repository so your teacher or mentor can run your code. Create a file named README.md in your main folder and paste this:  

Markdown
# AI Inference Microservice (gRPC + Docker)

This project is a highly scalable AI Inference Microservice built using **gRPC**, **Python**, and **Nginx**. It implements all four gRPC communication models and uses Nginx as a Layer 7 load balancer to distribute traffic across three containerized backend instances.

## 🚀 Tech Stack
- **RPC:** gRPC & Protocol Buffers (Protobuf)
- **Language:** Python
- **AI Engine:** Groq API (Llama 3.3 70B)
- **Infrastructure:** Docker & Docker Compose
- **Load Balancing:** Nginx (Configured for HTTP/2 and gRPC)

## 🛠️ Prerequisites
- Docker and Docker Compose installed.
- A Groq API Key (added to a `.env` file in the root directory).

## 🏃 How to Run the Project

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd ai-microservice
Set up your environment:
Create a .env file in the root directory and add your key:

Code snippet
GROQ_API_KEY=your_actual_key_here
Start the Microservice Mesh:
Use Docker Compose to build and spin up the three servers and the Nginx proxy:

Bash
docker-compose up --build -d
Run the Client Tester (Task 7):
In a new terminal, activate your local virtual environment and run the tester:

Bash
# For Windows
.\venv\Scripts\activate
python client/client.py
📊 Features Demonstrated
Task 2: Unary RPC - Simple sentiment analysis.

Task 3: Server-Streaming - Real-time AI token generation (typing effect).

Task 4: Client-Streaming - Sending large text chunks for summarization.

Task 5: Bidirectional-Streaming - Full-duplex live chat assistant.

🛡️ Infrastructure Details
Load Balancing: Nginx is configured to accept HTTP/2 traffic and use grpc_pass to distribute requests via Round Robin.

Scalability: The system uses three backend server replicas as defined in docker-compose.yml.