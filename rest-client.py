#!/usr/bin/env python3

from __future__ import print_function

import requests
import json
import time
import base64
import random
import argparse

IMAGE_FILE = 'Flatirons_Winter_Sunrise_edit_2.jpg'


def doRawImage(addr, img, debug=False):
    # Payload is the raw image bytes, marked as an image type (not JSON)
    headers = {'content-type': 'image/jpg'}
    response = requests.post(addr + '/api/rawimage', data=img, headers=headers)

    if debug:
        print("Response is", response)
        print(json.loads(response.text))


def doAdd(addr, debug=False):
    headers = {'content-type': 'application/json'}
    response = requests.post(addr + "/api/add/5/10", headers=headers)

    if debug:
        print("Response is", response)
        print(json.loads(response.text))


def doDotProduct(addr, a, b, debug=False):
    # json= serializes the body and sets content-type: application/json
    response = requests.post(addr + '/api/dotproduct', json={'a': a, 'b': b})

    if debug:
        print("Response is", response)
        print(json.loads(response.text))


def doJsonImage(addr, img_b64, debug=False):
    # Image is base64-encoded into a string so it is valid inside a JSON object
    response = requests.post(addr + '/api/jsonimage', json={'image': img_b64})

    if debug:
        print("Response is", response)
        print(json.loads(response.text))


# ---------------------------------------------------------
# Parse command-line arguments
# ---------------------------------------------------------

parser = argparse.ArgumentParser(
    description='REST client for measuring server operations'
)
parser.add_argument('host', help='IP address or hostname of the REST server')
parser.add_argument('cmd',
                    choices=['add', 'rawImage', 'dotProduct', 'jsonImage'],
                    help='Operation to perform')
parser.add_argument('reps', type=int, help='Number of repetitions for measurement')
parser.add_argument('-p', '--port', type=int, default=5000,
                    help='Server port (default: 5000)')
parser.add_argument('-d', '--debug', action='store_true',
                    help='Print the response from the server')
args = parser.parse_args()

addr = f"http://{args.host}:{args.port}"
print(f"Running {args.reps} reps against {addr}")

# ---------------------------------------------------------
# Build payloads BEFORE the timer starts so we only time the RPC
# ---------------------------------------------------------

if args.cmd in ('rawImage', 'jsonImage'):
    with open(IMAGE_FILE, 'rb') as f:
        img = f.read()
    img_b64 = base64.b64encode(img).decode('utf-8')

if args.cmd == 'dotProduct':
    a = [random.random() for _ in range(100)]
    b = [random.random() for _ in range(100)]

if args.cmd == 'add':
    call = lambda: doAdd(addr, debug=args.debug)
elif args.cmd == 'rawImage':
    call = lambda: doRawImage(addr, img, debug=args.debug)
elif args.cmd == 'dotProduct':
    call = lambda: doDotProduct(addr, a, b, debug=args.debug)
else:
    call = lambda: doJsonImage(addr, img_b64, debug=args.debug)

start = time.perf_counter()
for _ in range(args.reps):
    call()
delta = ((time.perf_counter() - start) / args.reps) * 1000
print("Took", delta, "ms per operation")
