"""Bounded OpenAI-format SSE decoding. Stream fragments never imply completion."""
from __future__ import annotations

import json
import time

from .http import ProviderError


def read_chat_stream(response, *, progress=None, byte_limit=16 * 1024 * 1024):
    """Assemble choice zero, retaining reasoning separately and authoritative usage.

    Require both a completion reason and the SSE DONE terminator. Return length-
    limited responses intact so the chat layer can reject them *after* journaling
    their token receipts. No connection, retry, model choice or inference occurs here.
    """
    started = time.monotonic()
    fields, answer, reasoning = [], [], []
    size = events = answer_size = reasoning_size = 0
    first_event = first_answer = None
    last_report = None
    identity = model = finish = usage = None
    done = False

    def invalid(message):
        raise ProviderError("invalid_response", message)

    def report(force=False):
        nonlocal last_report
        now = time.monotonic()
        if progress is not None and (force or last_report is None or now - last_report >= 5):
            progress({"events": events, "received_bytes": size,
                      "answer_characters": answer_size, "reasoning_characters": reasoning_size,
                      "elapsed_seconds": now - started, "first_event_seconds": first_event,
                      "first_answer_seconds": first_answer, "done": done,
                      "usage_receipt_present": usage is not None})
            last_report = now

    def consume(payload):
        nonlocal events, first_event, first_answer, identity, model, finish, usage
        nonlocal answer_size, reasoning_size, done
        if first_event is None:
            first_event = time.monotonic() - started
        if payload == "[DONE]":
            done = True
            report(force=True)
            return
        try:
            value = json.loads(payload)
            json.dumps(value, allow_nan=False)
        except (ValueError, TypeError):
            invalid("Stream event must contain finite JSON.")
        if not isinstance(value, dict) or value.get("error") is not None:
            invalid("Provider emitted an invalid or error stream event.")
        events += 1
        identity = value.get("id") or identity
        model = value.get("model") or model
        if value.get("usage") is not None:
            if not isinstance(value["usage"], dict):
                invalid("Stream usage must be an object.")
            usage = value["usage"]
        choices = value.get("choices", [])
        if not isinstance(choices, list):
            invalid("Invalid streaming choices.")
        for choice in choices:
            if not isinstance(choice, dict):
                invalid("Invalid streaming choice.")
            if choice.get("index", 0) != 0:
                continue
            delta = choice.get("delta", {})
            if not isinstance(delta, dict):
                invalid("Invalid streaming delta.")
            text = delta.get("content")
            if text is not None:
                if not isinstance(text, str):
                    invalid("Streaming content must be text.")
                answer.append(text)
                answer_size += len(text)
                if first_answer is None and text.strip():
                    first_answer = time.monotonic() - started
            thought = delta.get("reasoning_content")
            if thought is None:
                thought = delta.get("reasoning")
            if thought is not None:
                if not isinstance(thought, str):
                    invalid("Streaming reasoning must be text.")
                reasoning.append(thought)
                reasoning_size += len(thought)
            if choice.get("finish_reason") is not None:
                finish = choice["finish_reason"]
        report()

    while True:
        line = response.readline(1024 * 1024 + 1)
        if not line:
            break
        size += len(line)
        if len(line) > 1024 * 1024 or size > byte_limit:
            invalid("Provider stream exceeds the local byte limit.")
        try:
            line = line.decode("utf-8").rstrip("\r\n")
        except UnicodeError:
            invalid("Provider stream is not UTF-8.")
        if not line:
            if fields:
                consume("\n".join(fields))
                fields.clear()
                if done:
                    break
        elif line.startswith("data:"):
            text = line[5:]
            fields.append(text[1:] if text.startswith(" ") else text)
        # SSE comments, retry directives and event identifiers are not model text.
    if not done:
        invalid("Provider stream ended without its DONE terminator; response incomplete.")
    if not isinstance(finish, str) or not finish:
        invalid("Provider stream has no completion reason.")
    result = {"id": identity, "model": model,
              "choices": [{"index": 0, "message": {"role": "assistant", "content": "".join(answer),
                             "reasoning_content": "".join(reasoning)}, "finish_reason": finish}],
              "stream_metrics": {"events": events, "received_bytes": size,
                                 "first_event_seconds": first_event,
                                 "first_answer_seconds": first_answer, "done": done}}
    if usage is not None:
        result["usage"] = usage
    return result
