# Lab 6: REST vs gRPC

All times are milliseconds per operation. Local and same-zone runs used 1000 repetitions;
the different-region run used 100. Hosts were e2-standard-2 VMs: local and same-zone in
us-west1-a, the remote server in europe-west3-a (Frankfurt). All tests used internal IPs.

| Method | Local | Same-Zone | Different Region |
|---|---|---|---|
| REST add | 2.48 | 3.71 | 335.41 |
| gRPC add | 0.78 | 1.23 | 180.03 |
| REST rawimg | 4.60 | 7.35 | 1650.94 |
| gRPC rawimg | 7.81 | 9.12 | 213.93 |
| REST dotproduct | 2.98 | 3.87 | 346.26 |
| gRPC dotproduct | 0.81 | 1.27 | 162.26 |
| REST jsonimg | 21.27 | 24.12 | 1678.58 |
| gRPC jsonimg | 14.22 | 16.75 | 188.49 |
| PING | 0.043 | 0.571 | 162.4 |

Note: the first different-region gRPC add measurement was 415.69 ms, an outlier that did
not fit the other gRPC results. Rerunning it with 100 repetitions gave 180.03 ms (REST add
on the same rerun was 339.64 ms, consistent with the table), so the rerun value is reported.

## Observations

**Network latency dominates small calls.** For `add` and `dotproduct` the computation is
trivial, so the time is almost entirely overhead plus round-trip time. Locally REST add is
2.5 ms and gRPC add 0.8 ms; across regions both are dominated by the 162 ms ping.

**Connections.** REST opens a new TCP connection for every query, so a call costs roughly
two round trips (handshake, then request/response): REST add took about 335 ms against a
162 ms ping. gRPC reuses one connection, so a small call costs about one round trip: gRPC
dotproduct took 162 ms and gRPC add 180 ms. gRPC's advantage therefore grows with latency
(about 3x locally, about 1.9x across regions for add).

**Large payloads.** The 1.6 MB image calls show the biggest gap across regions: REST took
about 1650 ms against about 190-215 ms for gRPC. A likely reason is that each new REST
connection starts TCP's slow start from scratch and needs many round trips to send 1.6 MB,
while gRPC's long-lived connection is already warmed up. I did not measure this directly.
Locally the result reverses for rawimg (REST 4.6 ms vs gRPC 7.8 ms), where network
latency is negligible and gRPC's per-message handling of a large payload in Python appears
to cost more than REST's single HTTP body; again, I did not profile this.

**Encoding.** REST jsonimg is much slower than rawimg locally (21.3 vs 4.6 ms) because the
base64 string is about 33% larger and must be JSON-parsed and decoded. gRPC shows the
same pattern locally (jsonimg 14.2 ms vs rawimg 7.8 ms), since the base64 string is also
larger on the wire and must be decoded on the server. Across regions the gap between the
two gRPC image calls is small (188 vs 214 ms) and within what I would expect from noise,
so I do not draw a conclusion from it. Finally, the gRPC dotproduct uses 32-bit floats
(per the provided message types), so its results differ slightly from REST's 64-bit values.
