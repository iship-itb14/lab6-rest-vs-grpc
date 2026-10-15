#!/bin/bash
# Usage: ./bench.sh <host> <reps> [all|rest|grpc]
# Runs every endpoint against <host> and prints ms per operation, then ping.
HOST=$1
REPS=$2
WHICH=${3:-all}

if [ -z "$HOST" ] || [ -z "$REPS" ]; then
  echo "Usage: ./bench.sh <host> <reps> [all|rest|grpc]"
  exit 1
fi

for cmd in add rawImage dotProduct jsonImage; do
  if [ "$WHICH" = "all" ] || [ "$WHICH" = "rest" ]; then
    echo "== REST $cmd"
    uv run python rest-client.py "$HOST" "$cmd" "$REPS" | tail -1
  fi
  if [ "$WHICH" = "all" ] || [ "$WHICH" = "grpc" ]; then
    echo "== gRPC $cmd"
    uv run python grpc-client.py "$HOST" "$cmd" "$REPS" | tail -1
  fi
done

if [ "$WHICH" = "all" ]; then
  echo "== PING"
  ping -c 10 "$HOST" | tail -1
fi
