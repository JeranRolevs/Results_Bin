"""Offline native SSE, transport and partial-wave regression checks."""
import asyncio
import io
import json
from unittest import TestCase
from unittest.mock import patch

from labtune.providers.streaming import read_chat_stream
from labtune.providers.http import ProviderError
from labtune.providers.chat import ChatCompletionsClient
from labtune.providers.configuration import generation_settings
from labtune.study import TextStudy, StudyError


def event(content=None, thought=None, finish=None, index=0):
    delta = {}
    if content is not None:
        delta["content"] = content
    if thought is not None:
        delta["reasoning_content"] = thought
    return {"id": "offline-id", "model": "offline-model", "choices": [
        {"index": index, "delta": delta, "finish_reason": finish}]}


def wire(*values, done=True):
    text = ": heartbeat\n\n" + "".join("data: " + json.dumps(v) + "\r\n\r\n" for v in values)
    return (text + ("data: [DONE]\n\n" if done else "")).encode()


class StreamingTests(TestCase):
    def test_reasoning_answer_usage_and_empty_delta_timing(self):
        progress = []
        data = wire(event(content=""), event(thought="private thought"), event("answer"),
                    event(finish="stop"), {"choices": [], "usage": {"completion_tokens": 20}})
        result = read_chat_stream(io.BytesIO(data), progress=progress.append)
        self.assertEqual(result["choices"][0]["message"]["content"], "answer")
        self.assertEqual(result["choices"][0]["message"]["reasoning_content"], "private thought")
        self.assertEqual(result["usage"]["completion_tokens"], 20)
        self.assertIsNone(progress[0]["first_answer_seconds"])
        self.assertIsNotNone(progress[-1]["first_answer_seconds"])
        self.assertNotIn("private thought", json.dumps(progress))

    def test_length_retains_authoritative_receipt_before_chat_rejects(self):
        result = read_chat_stream(io.BytesIO(wire(event(thought="thinking"), event(finish="length"),
                    {"choices": [], "usage": {"completion_tokens": 8}})))
        self.assertEqual(result["usage"]["completion_tokens"], 8)
        journal = []
        client = ChatCompletionsClient(None, model="fixture", base_url="https://fixture.invalid", stream=True,
                                      transport=lambda *args: result, on_event=journal.append)
        with self.assertRaises(ProviderError) as caught:
            asyncio.run(client.generate([{"role": "user", "content": "offline"}], budget_ref="test"))
        self.assertEqual(caught.exception.kind, "output_limit")
        self.assertEqual(journal[-1]["kind"], "provider_response")

    def test_disconnect_missing_finish_error_nonfinite_and_empty_answer(self):
        bad = [wire(event("partial", finish="stop"), done=False), wire(event("no finish")),
               wire({"error": {"message": "failure"}}), wire({"bad": float("nan")})]
        for value in bad:
            with self.subTest(value=value), self.assertRaises(ProviderError):
                read_chat_stream(io.BytesIO(value))
        empty = read_chat_stream(io.BytesIO(wire(event(thought="only thought", finish="stop"))))
        client = ChatCompletionsClient(None, model="fixture", base_url="https://fixture.invalid", stream=True,
                                      transport=lambda *args: empty)
        with self.assertRaises(ProviderError):
            asyncio.run(client.generate([{"role": "user", "content": "offline"}], budget_ref="test"))

    def test_missing_usage_not_invented_and_other_choice_ignored(self):
        result = read_chat_stream(io.BytesIO(wire(event("wrong", index=1), event("right", finish="stop"))))
        self.assertNotIn("usage", result)
        self.assertEqual(result["choices"][0]["message"]["content"], "right")

    def test_bounds_and_unicode(self):
        value = wire(event("café", finish="stop"))
        self.assertEqual(read_chat_stream(io.BytesIO(value))["choices"][0]["message"]["content"], "café")
        with self.assertRaises(ProviderError):
            read_chat_stream(io.BytesIO(value), byte_limit=5)
        with self.assertRaises(ProviderError):
            read_chat_stream(io.BytesIO(b"data: \xff\n\n"))

    def test_multiline_sse(self):
        value = b'data: {"choices": [{"delta": {"content":"OK"},\ndata: "finish_reason":"stop"}]}\n\ndata: [DONE]\n\n'
        self.assertEqual(read_chat_stream(io.BytesIO(value))["choices"][0]["message"]["content"], "OK")

    def test_opt_in_stream_is_in_native_body_and_configuration(self):
        config = {"base_url": "https://fixture.invalid", "model": "fixture", "api_key_env": None,
                  "env_file": ".env", "timeout_seconds": 1, "max_output_tokens": 10,
                  "max_parallel_requests": 1}
        self.assertFalse(generation_settings(config)["stream"])
        self.assertTrue(generation_settings(dict(config, stream=True))["stream"])
        for v in [1, "true", None]:
            with self.assertRaises(ProviderError):
                generation_settings(dict(config, stream=v))
        bodies = []
        def transport(method, path, body):
            bodies.append(body)
            return read_chat_stream(io.BytesIO(wire(event("OK", finish="stop"))))
        client = ChatCompletionsClient(None, model="fixture", base_url="https://fixture.invalid",
                                      stream=True, transport=transport)
        self.assertEqual(asyncio.run(client.generate([{"role": "user", "content": "offline"}],
                                                    budget_ref="test"))["content"], "OK")
        self.assertTrue(bodies[0]["stream"])

    def test_actual_http_path_is_mocked_not_network_and_redacts_key(self):
        class Response(io.BytesIO):
            headers = {"Content-Type": "text/event-stream"}
        calls = []
        class Opener:
            def open(self, request, timeout):
                calls.append(json.loads(request.data))
                return Response(wire(event("OFFLINE-SECRET", finish="stop"),
                                     {"usage": {"prompt_tokens": 2}, "choices": []}))
        events = []
        client = ChatCompletionsClient("OFFLINE-SECRET", model="fixture", base_url="https://fixture.invalid",
                                      stream=True, on_event=events.append)
        with patch("labtune.providers.http.urllib.request.build_opener", return_value=Opener()):
            asyncio.run(client.generate([{"role": "user", "content": "offline"}], budget_ref="test"))
        self.assertEqual(len(calls), 1)
        self.assertTrue(any(e["kind"] == "provider_stream_progress" for e in events))
        self.assertNotIn("OFFLINE-SECRET", json.dumps(events))

    def test_successful_wave_sibling_survives_failure(self):
        study = object.__new__(TextStudy)
        study.plan = {"resources": {"max_active_agents": 2}, "work_graph": [
            {"id": "phase", "kind": "episode", "depends_on": [],
             "research_activity": "allowed", "actors": ["ok", "fail"]}]}
        study.outputs = []
        study.event = lambda value: None
        async def episode(node, actor):
            if actor == "fail":
                raise StudyError("offline sibling failure")
            return {"actor": actor, "output": {"summary": "saved"}}
        study.run_node_episode = episode
        with self.assertRaises(StudyError):
            asyncio.run(study.run_graph())
        self.assertEqual([x["actor"] for x in study.outputs], ["ok"])
