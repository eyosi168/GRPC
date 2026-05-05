FROM python:3.11-slim
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 1. Copy the proto file (now that it is inside the server folder)
COPY inference.proto .

# 2. Copy the rest of your server code
COPY . .

# 3. Generate the gRPC code (notice the paths are now simpler)
RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. inference.proto

CMD ["python", "server.py"]