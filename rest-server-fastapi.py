#!/usr/bin/env python3
"""
FastAPI version of the REST server (extra credit: Flask -> FastAPI + uvicorn).

Same endpoints and response shapes as rest-server.py, so rest-client.py
works against either server unchanged.
"""

import argparse
import base64
import io

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from PIL import Image
from pydantic import BaseModel

app = FastAPI()


class DotProductRequest(BaseModel):
    a: list[float]
    b: list[float]


class JsonImageRequest(BaseModel):
    image: str  # base64-encoded image bytes


def image_size(data: bytes) -> dict:
    try:
        img = Image.open(io.BytesIO(data))
        return {'width': img.size[0], 'height': img.size[1]}
    except Exception:
        return {'width': 0, 'height': 0}


@app.api_route('/api/add/{a}/{b}', methods=['GET', 'POST'])
def add(a: int, b: int):
    return {'sum': str(a + b)}


@app.post('/api/rawimage')
async def rawimage(request: Request):
    # The whole payload is the image (content-type image/jpg), not JSON
    return image_size(await request.body())


@app.post('/api/dotproduct')
def dotproduct(req: DotProductRequest):
    if len(req.a) != len(req.b):
        raise HTTPException(status_code=400,
                            detail='vectors must be the same length')
    return {'dotproduct': sum(x * y for x, y in zip(req.a, req.b))}


@app.post('/api/jsonimage')
def jsonimage(req: JsonImageRequest):
    try:
        data = base64.b64decode(req.image)
    except Exception:
        return {'width': 0, 'height': 0}
    return image_size(data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='FastAPI REST server')
    parser.add_argument('-p', '--port', type=int, default=5000,
                        help='Port on which to run the server (default: 5000)')
    args = parser.parse_args()

    uvicorn.run(app, host='0.0.0.0', port=args.port, log_level='warning')
