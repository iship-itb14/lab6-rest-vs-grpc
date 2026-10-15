#!/usr/bin/env python3

import argparse
import base64
import random
import time

import grpc

import lab6_pb2
import lab6_pb2_grpc

IMAGE_FILE = 'Flatirons_Winter_Sunrise_edit_2.jpg'

parser = argparse.ArgumentParser(
    description='gRPC client for measuring server operations'
)
parser.add_argument('host', help='IP address or hostname of the gRPC server')
parser.add_argument('cmd',
                    choices=['add', 'rawImage', 'dotProduct', 'jsonImage'],
                    help='Operation to perform')
parser.add_argument('reps', type=int, help='Number of repetitions for measurement')
parser.add_argument('-p', '--port', type=int, default=50051,
                    help='Server port (default: 50051)')
parser.add_argument('-d', '--debug', action='store_true',
                    help='Print the response from the server')
args = parser.parse_args()

addr = f"{args.host}:{args.port}"
print(f"Running {args.reps} reps against {addr}")

# One channel + stub, reused for every call: this is the single long-lived
# TCP/HTTP2 connection that makes gRPC cheaper than REST per query.
options = [
    ('grpc.max_receive_message_length', 16 * 1024 * 1024),
    ('grpc.max_send_message_length', 16 * 1024 * 1024),
]
channel = grpc.insecure_channel(addr, options=options)
stub = lab6_pb2_grpc.Lab6Stub(channel)

# ---------------------------------------------------------
# Build requests BEFORE the timer starts so we only time the RPC
# ---------------------------------------------------------
if args.cmd == 'add':
    msg = lab6_pb2.addMsg(a=5, b=10)
    call = lambda: stub.add(msg)

elif args.cmd == 'rawImage':
    with open(IMAGE_FILE, 'rb') as f:
        msg = lab6_pb2.rawImageMsg(img=f.read())
    call = lambda: stub.rawImage(msg)

elif args.cmd == 'dotProduct':
    msg = lab6_pb2.dotProductMsg(
        a=[random.random() for _ in range(100)],
        b=[random.random() for _ in range(100)],
    )
    call = lambda: stub.dotProduct(msg)

else:  # jsonImage
    with open(IMAGE_FILE, 'rb') as f:
        msg = lab6_pb2.jsonImageMsg(img=base64.b64encode(f.read()).decode('utf-8'))
    call = lambda: stub.jsonImage(msg)

# Establish the connection first so setup isn't counted in the average
grpc.channel_ready_future(channel).result(timeout=10)

start = time.perf_counter()
for _ in range(args.reps):
    reply = call()
    if args.debug:
        print(reply)
delta = ((time.perf_counter() - start) / args.reps) * 1000
print("Took", delta, "ms per operation")
