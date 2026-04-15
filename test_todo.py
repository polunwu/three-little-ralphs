"""Tests for todo.py — patches TODO_FILE to a temp file for isolation."""

import sys
import unittest
from io import StringIO
from pathlib import Path
from tempfile import NamedTemporaryFile

import todo


class TodoTestCase(unittest.TestCase):
    """Base class: redirects TODO_FILE to a temp file and captures stdout/stderr."""

    def setUp(self):
        self._tmp = NamedTemporaryFile(suffix=".txt", delete=False)
        self._tmp.close()
        self._orig_file = todo.TODO_FILE
        todo.TODO_FILE = Path(self._tmp.name)
        # Start each test with an empty file
        todo.TODO_FILE.write_text("", encoding="utf-8")

    def tearDown(self):
        todo.TODO_FILE = self._orig_file
        Path(self._tmp.name).unlink(missing_ok=True)

    # ── helpers ──────────────────────────────────────────────────────────────

    def capture(self, fn, *args):
        """Run fn(*args), return (stdout, stderr) as plain strings (no ANSI)."""
        out, err = StringIO(), StringIO()
        sys.stdout, sys.stderr = out, err
        try:
            fn(*args)
        except SystemExit:
            pass
        finally:
            sys.stdout, sys.stderr = sys.__stdout__, sys.__stderr__
        return self._strip_ansi(out.getvalue()), self._strip_ansi(err.getvalue())

    @staticmethod
    def _strip_ansi(s):
        import re
        return re.sub(r"\033\[[0-9;]*m", "", s)

    def raw_lines(self):
        """Return raw lines from the todo file."""
        return todo.TODO_FILE.read_text(encoding="utf-8").splitlines()


# ── load / save ───────────────────────────────────────────────────────────────

class TestLoadSave(TodoTestCase):

    def test_load_empty_file(self):
        self.assertEqual(todo.load_todos(), [])

    def test_load_missing_file(self):
        todo.TODO_FILE.unlink()
        self.assertEqual(todo.load_todos(), [])

    def test_save_and_reload(self):
        todos = [
            {"id": 1, "done": False, "text": "任務 A"},
            {"id": 2, "done": True,  "text": "任務 B"},
        ]
        todo.save_todos(todos)
        loaded = todo.load_todos()
        self.assertEqual(len(loaded), 2)
        self.assertEqual(loaded[0], {"id": 1, "done": False, "text": "任務 A"})
        self.assertEqual(loaded[1], {"id": 2, "done": True,  "text": "任務 B"})

    def test_ids_are_sequential(self):
        todo.save_todos([
            {"id": 1, "done": False, "text": "A"},
            {"id": 2, "done": False, "text": "B"},
            {"id": 3, "done": False, "text": "C"},
        ])
        loaded = todo.load_todos()
        self.assertEqual([t["id"] for t in loaded], [1, 2, 3])


# ── add ───────────────────────────────────────────────────────────────────────

class TestAdd(TodoTestCase):

    def test_add_single(self):
        self.capture(todo.cmd_add, "買東西")
        todos = todo.load_todos()
        self.assertEqual(len(todos), 1)
        self.assertEqual(todos[0]["text"], "買東西")
        self.assertFalse(todos[0]["done"])

    def test_add_multiple_preserves_order(self):
        for t in ["A", "B", "C"]:
            self.capture(todo.cmd_add, t)
        texts = [t["text"] for t in todo.load_todos()]
        self.assertEqual(texts, ["A", "B", "C"])

    def test_add_strips_whitespace(self):
        self.capture(todo.cmd_add, "  有空白  ")
        self.assertEqual(todo.load_todos()[0]["text"], "有空白")

    def test_add_blank_prints_error(self):
        _, err = self.capture(todo.cmd_add, "   ")
        self.assertIn("不能為空", err)

    def test_add_blank_does_not_write(self):
        self.capture(todo.cmd_add, "   ")
        self.assertEqual(todo.load_todos(), [])

    def test_add_prints_confirmation(self):
        out, _ = self.capture(todo.cmd_add, "測試")
        self.assertIn("已新增", out)
        self.assertIn("測試", out)

    def test_file_format_is_plain_text(self):
        self.capture(todo.cmd_add, "格式測試")
        self.assertEqual(self.raw_lines(), ["[ ] 格式測試"])


# ── list ──────────────────────────────────────────────────────────────────────

class TestList(TodoTestCase):

    def test_list_empty(self):
        out, _ = self.capture(todo.cmd_list)
        self.assertIn("沒有任何", out)

    def test_list_shows_all_items(self):
        for t in ["A", "B", "C"]:
            self.capture(todo.cmd_add, t)
        out, _ = self.capture(todo.cmd_list)
        self.assertIn("A", out)
        self.assertIn("B", out)
        self.assertIn("C", out)

    def test_list_shows_ids(self):
        self.capture(todo.cmd_add, "只有一個")
        out, _ = self.capture(todo.cmd_list)
        self.assertIn("1", out)

    def test_list_shows_done_marker(self):
        self.capture(todo.cmd_add, "完成任務")
        todo.cmd_done(1)
        out, _ = self.capture(todo.cmd_list)
        self.assertIn("✓", out)


# ── done ──────────────────────────────────────────────────────────────────────

class TestDone(TodoTestCase):

    def test_done_marks_item(self):
        self.capture(todo.cmd_add, "待完成")
        self.capture(todo.cmd_done, 1)
        self.assertTrue(todo.load_todos()[0]["done"])

    def test_done_prints_confirmation(self):
        self.capture(todo.cmd_add, "待完成")
        out, _ = self.capture(todo.cmd_done, 1)
        self.assertIn("已完成", out)

    def test_done_invalid_id_prints_error(self):
        _, err = self.capture(todo.cmd_done, 999)
        self.assertIn("找不到", err)

    def test_done_already_done_prints_notice(self):
        self.capture(todo.cmd_add, "已完成項目")
        self.capture(todo.cmd_done, 1)
        out, _ = self.capture(todo.cmd_done, 1)
        self.assertIn("已經是完成狀態", out)

    def test_done_does_not_affect_other_items(self):
        for t in ["A", "B", "C"]:
            self.capture(todo.cmd_add, t)
        self.capture(todo.cmd_done, 2)
        todos = todo.load_todos()
        self.assertFalse(todos[0]["done"])
        self.assertTrue(todos[1]["done"])
        self.assertFalse(todos[2]["done"])


# ── delete ────────────────────────────────────────────────────────────────────

class TestDelete(TodoTestCase):

    def test_delete_removes_item(self):
        self.capture(todo.cmd_add, "刪除我")
        self.capture(todo.cmd_delete, 1)
        self.assertEqual(todo.load_todos(), [])

    def test_delete_prints_confirmation(self):
        self.capture(todo.cmd_add, "刪除我")
        out, _ = self.capture(todo.cmd_delete, 1)
        self.assertIn("已刪除", out)

    def test_delete_invalid_id_prints_error(self):
        _, err = self.capture(todo.cmd_delete, 42)
        self.assertIn("找不到", err)

    def test_delete_reindexes_remaining(self):
        for t in ["A", "B", "C"]:
            self.capture(todo.cmd_add, t)
        self.capture(todo.cmd_delete, 2)       # remove "B"
        todos = todo.load_todos()
        self.assertEqual(len(todos), 2)
        self.assertEqual([t["text"] for t in todos], ["A", "C"])
        self.assertEqual([t["id"] for t in todos], [1, 2])

    def test_delete_done_item(self):
        self.capture(todo.cmd_add, "完成再刪")
        self.capture(todo.cmd_done, 1)
        self.capture(todo.cmd_delete, 1)
        self.assertEqual(todo.load_todos(), [])


# ── clear ─────────────────────────────────────────────────────────────────────

class TestClear(TodoTestCase):

    def test_clear_removes_done_items(self):
        for t in ["A", "B", "C"]:
            self.capture(todo.cmd_add, t)
        self.capture(todo.cmd_done, 1)
        self.capture(todo.cmd_done, 3)
        self.capture(todo.cmd_clear)
        todos = todo.load_todos()
        self.assertEqual(len(todos), 1)
        self.assertEqual(todos[0]["text"], "B")

    def test_clear_prints_count(self):
        self.capture(todo.cmd_add, "X")
        self.capture(todo.cmd_done, 1)
        out, _ = self.capture(todo.cmd_clear)
        self.assertIn("1", out)
        self.assertIn("已清除", out)

    def test_clear_nothing_to_clear(self):
        self.capture(todo.cmd_add, "未完成")
        out, _ = self.capture(todo.cmd_clear)
        self.assertIn("沒有已完成", out)

    def test_clear_empty_list(self):
        out, _ = self.capture(todo.cmd_clear)
        self.assertIn("沒有已完成", out)

    def test_clear_all_done(self):
        for t in ["A", "B"]:
            self.capture(todo.cmd_add, t)
        self.capture(todo.cmd_done, 1)
        self.capture(todo.cmd_done, 2)
        self.capture(todo.cmd_clear)
        self.assertEqual(todo.load_todos(), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
