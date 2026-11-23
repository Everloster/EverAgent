#!/usr/bin/env python3
"""Offline, virtual-time examples. This does not call or emulate an OpenAI server.

Run: python3 controller.py
Only application-owned deadline, question, and output-selection rules are tested.
"""
from dataclasses import dataclass, field
import json


@dataclass(frozen=True)
class CallKey:
    session: str
    turn: str
    call: str


@dataclass
class Controller:
    reply_cutoff: float = 600
    delivery_cutoff: float = 720
    now: float = 0
    questions: dict = field(default_factory=dict)
    outputs: list = field(default_factory=list)
    latest_response: str | None = None
    saved_brief: str = ""
    delivered: bool = False
    submissions: set = field(default_factory=set)
    approval: bool = False

    def tick(self, seconds):
        """Virtual monotonic elapsed time; a displayed UTC clock is separate."""
        if seconds < self.now:
            raise ValueError("elapsed time cannot go backwards")
        self.now = seconds
        if self.now >= self.reply_cutoff and not self.delivered:
            for key, question in self.questions.items():
                if question["state"] == "pending":
                    self._close(key, {"status": "no_answer"})
        if self.now >= self.delivery_cutoff:
            self.deliver()

    def ask(self, key):
        if self.delivered or key in self.questions:
            return False
        self.questions[key] = {"state": "pending"}
        if self.now >= self.reply_cutoff:
            self._close(key, {"status": "no_answer"})
        return True

    def _close(self, key, result):
        question = self.questions.get(key)
        if question is None or question["state"] != "pending":
            return False
        question.update(state="resolved", result=result)
        self.outputs.append((key, result))
        return True

    def reply(self, key, answer):
        if self.delivered or self.now >= self.reply_cutoff:
            return False
        if not answer.strip():
            return False  # An empty form submission is not an answer.
        return self._close(key, {"status": "answered", "answer": answer})

    def completed_response(self, response_id):
        self.latest_response = response_id

    def ready_continuation(self):
        """Illustrative Responses input, using original call IDs, latest history."""
        results = []
        for key, value in self.outputs:
            if key not in self.submissions:
                results.append({"type": "function_call_output", "call_id": key.call,
                                "output": json.dumps(value, ensure_ascii=False)})
        return {"previous_response_id": self.latest_response, "input": results}

    def confirm_submission(self, keys):
        """Record acknowledgement separately from constructing an output batch."""
        for key in keys:
            if key not in self.questions or self.questions[key]["state"] != "resolved":
                raise ValueError("cannot acknowledge an unresolved question")
            self.submissions.add(key)

    def save_item(self, text, status, phase, role="assistant"):
        if (not self.delivered and self.now < self.delivery_cutoff and
                role == "assistant" and status == "completed" and phase == "final_answer"):
            self.saved_brief = text

    def deliver(self):
        self.delivered = True
        for question in self.questions.values():
            if question["state"] == "pending":
                question["state"] = "closed"
        return self.saved_brief or "No verified findings were available by the deadline."

    def can_execute_purchase(self):
        """A separate illustrative permission gate, not an OpenAI API field."""
        return self.approval and not self.delivered


def run_scenarios():
    key = CallKey("session_example", "turn_example", "call_example")
    results = []

    c = Controller(); c.ask(key); c.tick(180)
    assert c.reply(key, "technical evaluation")
    assert c.outputs[0][1]["status"] == "answered"
    results.append("reply_received_before_cutoff")

    c = Controller(); c.ask(key); c.tick(600)
    assert c.outputs[0][1] == {"status": "no_answer"}
    assert not c.reply(key, "arrived at the cutoff")
    results.append("cutoff_expires_question_without_inventing_answer")

    c = Controller(); c.ask(key); c.tick(650)
    assert not c.reply(key, "late answer") and len(c.outputs) == 1
    results.append("late_reply_does_not_overwrite_expiration")

    c = Controller(); assert c.ask(key); assert not c.ask(key)
    c.reply(key, "commercial discussion")
    assert not c.reply(key, "replayed answer") and len(c.outputs) == 1
    results.append("replayed_call_and_reply_do_not_duplicate_completion")

    c = Controller(); c.ask(key)
    assert not c.reply(CallKey("other_session", key.turn, key.call), "wrong form")
    assert c.questions[key]["state"] == "pending"
    results.append("reply_is_bound_to_session_turn_and_call")

    c = Controller(); c.tick(300); c.save_item("completed brief", "completed", "final_answer")
    c.tick(720)  # A still-running model request cannot move this application deadline.
    assert c.deliver() == "completed brief"
    c.save_item("late replacement", "completed", "final_answer")
    assert c.saved_brief == "completed brief"
    results.append("deadline_uses_saved_completed_brief_and_rejects_late_replacement")

    c = Controller(); c.save_item("half a sentence", "in_progress", "final_answer")
    c.save_item("internal work", "completed", "analysis")
    assert c.deliver().startswith("No verified findings")
    results.append("partial_text_and_analysis_are_not_delivered_as_final")

    c = Controller(); c.ask(key); c.completed_response("response_old")
    c.completed_response("response_latest"); c.reply(key, "technical")
    request = c.ready_continuation()
    assert request["previous_response_id"] == "response_latest"
    assert request["input"][0]["call_id"] == key.call
    c.confirm_submission([key]); assert c.ready_continuation()["input"] == []
    results.append("old_call_result_continues_from_latest_response_and_is_acknowledged_once")

    c = Controller(); c.ask(key); c.tick(600)
    assert not c.can_execute_purchase()
    c.approval = True; assert c.can_execute_purchase()
    c.tick(720); assert not c.can_execute_purchase()
    results.append("question_expiration_never_grants_purchase_permission")

    c = Controller(); c.tick(599)
    displayed_utc_correction = -3600  # Does not change monotonic deadlines.
    assert displayed_utc_correction < 0 and c.delivery_cutoff == 720
    c.tick(720); assert c.delivered
    results.append("wall_clock_correction_does_not_extend_elapsed_deadline")

    print(json.dumps({"scope": "offline application rules; no SDK or model calls",
                      "passed": len(results), "scenarios": results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    run_scenarios()
