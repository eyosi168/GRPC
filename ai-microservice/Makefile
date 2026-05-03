.PHONY: proto

proto:
	python -m grpc_tools.protoc -I./protos --python_out=./server --grpc_python_out=./server ./protos/inference.proto
	python -m grpc_tools.protoc -I./protos --python_out=./client --grpc_python_out=./client ./protos/inference.proto
	