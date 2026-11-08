"""Tests for Timeline entity, TimelineEvent, add/remove/reorder events."""

from __future__ import annotations

from app.simulation.domain.entities.timeline import BranchPath, Timeline, TimelineEvent


class TestTimelineEvent:
    def test_default_values(self):
        e = TimelineEvent()
        assert e.event_type == ""
        assert e.milestone is False
        assert e.replay_marker is False
        assert e.order == 0

    def test_custom_event(self):
        e = TimelineEvent(event_type="login", timestamp_offset_ms=1000, milestone=True)
        assert e.event_type == "login"
        assert e.timestamp_offset_ms == 1000
        assert e.milestone is True

    def test_to_dict_structure(self):
        e = TimelineEvent(id="e1", event_type="test", data={"key": "val"})
        d = e.to_dict()
        assert d["id"] == "e1"
        assert d["event_type"] == "test"
        assert d["data"]["key"] == "val"


class TestTimeline:
    def test_defaults(self):
        t = Timeline()
        assert t.name == ""
        assert t.total_duration_ms == 0
        assert len(t.events) == 0

    def test_add_event(self):
        t = Timeline(name="Test")
        e1 = TimelineEvent(event_type="A", timestamp_offset_ms=100)
        e2 = TimelineEvent(event_type="B", timestamp_offset_ms=200)
        t.add_event(e1)
        t.add_event(e2)
        assert len(t.events) == 2
        assert t.events[0].order == 0
        assert t.events[1].order == 1

    def test_add_event_sorts_by_offset(self):
        t = Timeline()
        e1 = TimelineEvent(event_type="A", timestamp_offset_ms=300)
        e2 = TimelineEvent(event_type="B", timestamp_offset_ms=100)
        t.add_event(e1)
        t.add_event(e2)
        assert t.events[0].event_type == "B"
        assert t.events[1].event_type == "A"

    def test_remove_event(self):
        t = Timeline()
        e = TimelineEvent(event_type="X")
        t.add_event(e)
        assert t.remove_event(e.id) is True
        assert len(t.events) == 0

    def test_remove_nonexistent_event(self):
        t = Timeline()
        assert t.remove_event("nonexistent") is False

    def test_reorder_events(self):
        t = Timeline()
        e1 = TimelineEvent(event_type="A", timestamp_offset_ms=300)
        e2 = TimelineEvent(event_type="B", timestamp_offset_ms=100)
        e3 = TimelineEvent(event_type="C", timestamp_offset_ms=200)
        t.add_event(e1)
        t.add_event(e2)
        t.add_event(e3)
        t.reorder_events([e3.id, e1.id, e2.id])
        assert t.events[0].event_type == "C"
        assert t.events[1].event_type == "A"
        assert t.events[2].event_type == "B"

    def test_get_milestones(self):
        t = Timeline()
        e1 = TimelineEvent(event_type="Start", milestone=True)
        e2 = TimelineEvent(event_type="Mid")
        e3 = TimelineEvent(event_type="End", milestone=True)
        t.add_event(e1)
        t.add_event(e2)
        t.add_event(e3)
        milestones = t.get_milestones()
        assert len(milestones) == 2
        assert milestones[0].event_type == "Start"

    def test_get_checkpoints(self):
        t = Timeline()
        e1 = TimelineEvent(event_type="Check", learner_checkpoint=True)
        t.add_event(e1)
        checkpoints = t.get_checkpoints()
        assert len(checkpoints) == 1

    def test_calculate_duration(self):
        t = Timeline()
        t.add_event(TimelineEvent(timestamp_offset_ms=500))
        t.add_event(TimelineEvent(timestamp_offset_ms=1500))
        assert t.calculate_duration() == 1500

    def test_get_events_in_window(self):
        t = Timeline()
        t.add_event(TimelineEvent(timestamp_offset_ms=100))
        t.add_event(TimelineEvent(timestamp_offset_ms=200))
        t.add_event(TimelineEvent(timestamp_offset_ms=300))
        result = t.get_events_in_window(150, 250)
        assert len(result) == 1
        assert result[0].timestamp_offset_ms == 200

    def test_add_and_remove_branch(self):
        t = Timeline()
        e1 = TimelineEvent(event_type="A")
        e2 = TimelineEvent(event_type="B")
        t.add_event(e1)
        t.add_event(e2)
        branch = BranchPath(source_event_id=e1.id, target_event_id=e2.id, condition="x > 5")
        t.add_branch(branch)
        assert len(t.branches) == 1
        assert t.remove_branch(branch.id) is True
        assert len(t.branches) == 0

    def test_to_dict_includes_events_and_branches(self):
        t = Timeline(name="Main")
        e = TimelineEvent(event_type="Start")
        t.add_event(e)
        d = t.to_dict()
        assert d["name"] == "Main"
        assert len(d["events"]) == 1
