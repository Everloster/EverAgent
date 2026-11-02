#!/usr/bin/env python3
"""Local HTTP/1.1 streaming lab, not a Google API Gateway implementation.

Standard library only. The parser deliberately handles this lab's LF-delimited
SSE subset, not the full EventSource standard (CR/CRLF, retry, BOM, etc.).
No cloud credentials, external requests, model inference, or persistent jobs.
"""

import argparse
import codecs
import http.client
import json
import platform
import statistics
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


DELAY_SECONDS = 0.1
TEXT = ["流", "式", "响", "应"]


def frame(event_id, event, data):
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    return f"id: {event_id}\nevent: {event}\ndata: {payload}\n\n".encode("utf-8")


EVENT_LOG = [frame(i, "delta", {"text": text}) for i, text in enumerate(TEXT, 1)]
EVENT_LOG.append(frame(5, "done", {"complete": True}))


class LFEventParser:
    """Incrementally decode UTF-8 before finding application event boundaries."""

    def __init__(self):
        self.decoder = codecs.getincrementaldecoder("utf-8")()
        self.pending = ""
        self.last_id = ""

    def feed(self, chunk):
        self.pending += self.decoder.decode(chunk)
        if len(self.pending) > 65536:
            raise ValueError("lab event buffer limit exceeded")
        events = []
        while "\n\n" in self.pending:
            block, self.pending = self.pending.split("\n\n", 1)
            kind, data = "message", []
            for line in block.split("\n"):
                if not line or line.startswith(":"):
                    continue
                name, _, value = line.partition(":")
                if value.startswith(" "):
                    value = value[1:]
                if name == "id" and "\x00" not in value:
                    self.last_id = value
                elif name == "event":
                    kind = value or "message"
                elif name == "data":
                    data.append(value)
            if data:
                events.append({"id": self.last_id, "event": kind, "data": "\n".join(data)})
        return events

    def finish(self):
        self.decoder.decode(b"", final=True)
        # EOF does not dispatch an event lacking its final blank line.
        self.pending = ""


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *_args):
        pass

    def do_GET(self):
        if self.path not in {"/stream", "/buffered", "/cut"}:
            self.send_error(404)
            return
        try:
            last_id = int(self.headers.get("Last-Event-ID", "0"))
            if not 0 <= last_id <= 5:
                raise ValueError
        except ValueError:
            self.send_error(400)
            return
        selected = [(i, data) for i, data in enumerate(EVENT_LOG, 1) if i > last_id]
        if self.path == "/cut":
            selected = [(i, data) for i, data in selected if i <= 2]
        try:
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Transfer-Encoding", "chunked")
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.flush()
            buffered = []
            for event_id, data in selected:
                if event_id <= 4:
                    time.sleep(DELAY_SECONDS)
                if self.path == "/buffered":
                    buffered.append(data)
                else:
                    # An application event intentionally spans multiple HTTP chunks.
                    middle = len(data) // 2
                    self.send_chunk(data[:middle])
                    self.send_chunk(data[middle:])
            if buffered:
                # Same chunked HTTP framing, but the application buffers all events.
                self.send_chunk(b"".join(buffered))
            self.wfile.write(b"0\r\n\r\n")
            self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            self.close_connection = True

    def send_chunk(self, data):
        self.wfile.write(f"{len(data):x}\r\n".encode("ascii") + data + b"\r\n")
        self.wfile.flush()


def receive(port, path, last_id=""):
    parser, events, delta_times = LFEventParser(), [], []
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    started = time.perf_counter()
    try:
        headers = {"Last-Event-ID": last_id} if last_id else {}
        connection.request("GET", path, headers=headers)
        response = connection.getresponse()
        headers_ms = (time.perf_counter() - started) * 1000
        assert response.status == 200
        assert response.getheader("Transfer-Encoding") == "chunked"
        while chunk := response.read1(7):
            for event in parser.feed(chunk):
                events.append(event)
                if event["event"] == "delta":
                    delta_times.append(round((time.perf_counter() - started) * 1000, 3))
        parser.finish()
        total_ms = (time.perf_counter() - started) * 1000
    finally:
        connection.close()
    return {
        "http_status": response.status,
        "headers_ms": round(headers_ms, 3),
        "first_delta_ms": delta_times[0] if delta_times else None,
        "delta_arrivals_ms": delta_times,
        "total_ms": round(total_ms, 3),
        "event_ids": [event["id"] for event in events],
        "text": "".join(json.loads(event["data"])["text"] for event in events if event["event"] == "delta"),
        "semantic_complete": bool(events and events[-1]["event"] == "done"),
    }


def parser_tests():
    wire = b": heartbeat\n\n" + b"".join(EVENT_LOG)

    def parse(chunks):
        parser, events = LFEventParser(), []
        for chunk in chunks:
            events.extend(parser.feed(chunk))
        parser.finish()
        return events

    expected = parse([wire])
    assert len(expected) == 5
    for split in range(len(wire) + 1):
        assert parse([wire[:split], wire[split:]]) == expected
    assert parse([wire[i:i + 1] for i in range(len(wire))]) == expected
    assert parse([b"data: unfinished\n"]) == []
    assert parse([b"data: first\ndata: second\n\n"])[0]["data"] == "first\nsecond"
    return {
        "all_single_split_positions_passed": len(wire) + 1,
        "one_byte_fragments_passed": True,
        "incomplete_event_discarded": True,
        "multiline_data_passed": True,
        "scope": "LF-only SSE subset; not a production SSE parser",
    }


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--output", type=Path, help="new JSON output file; existing files are not overwritten")
    args = cli.parse_args()
    if args.output and args.output.exists():
        cli.error("output file already exists")
    parser_result = parser_tests()
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        port = server.server_address[1]
        # Paired trials, five per mode; these numbers are not cloud benchmarks.
        samples = {"stream": [], "buffered": []}
        for _ in range(5):
            for mode in samples:
                row = receive(port, "/" + mode)
                assert row["text"] == "流式响应" and row["semantic_complete"]
                samples[mode].append(row)
        cut = receive(port, "/cut")
        assert cut["http_status"] == 200 and not cut["semantic_complete"]
        assert cut["event_ids"] == ["1", "2"]
        resumed = receive(port, "/stream", cut["event_ids"][-1])
        assert resumed["event_ids"] == ["3", "4", "5"] and resumed["semantic_complete"]
        assert cut["text"] + resumed["text"] == "流式响应"
        medians = {
            mode: {key: round(statistics.median(row[key] for row in rows), 3)
                   for key in ["headers_ms", "first_delta_ms", "total_ms"]}
            for mode, rows in samples.items()
        }
        result = {
            "experiment": "local HTTP/1.1 streaming versus full-response buffering",
            "python": platform.python_version(), "platform": platform.system(),
            "delay_seconds_per_delta": DELAY_SECONDS, "delta_count": len(TEXT),
            "trials_per_mode": 5, "medians_ms": medians, "samples": samples,
            "parser_tests": parser_result,
            "clean_http_eof_without_done": cut,
            "resume_from_static_event_log": resumed,
            "limitations": [
                "Loopback only; no Google Cloud resource or real model was tested.",
                "Buffered delivery is simulated inside one server, not a deployed reverse proxy.",
                "Static in-process event log; no persistent job, exactly-once effects or automated reconnection.",
                "Only HTTP/1.1 and the documented LF-only SSE subset were executed.",
                "Latency values illustrate imposed production delays, not system performance or SLOs.",
            ],
        }
        encoded = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            with args.output.open("x", encoding="utf-8") as output:
                output.write(encoded)
        print(encoded, end="")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


if __name__ == "__main__":
    main()
