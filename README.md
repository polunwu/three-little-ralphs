# CLI Todo List

A minimal command-line todo list written in Python. Data is stored in `~/.todos.txt` as plain text — no database, no dependencies.

## Requirements

- Python 3.6+

## Usage

```bash
python3 todo.py <command> [args]
```

### Commands

| Command | Description |
|---|---|
| `python3 todo.py` | List all todos (same as `list`) |
| `python3 todo.py list` | List all todos |
| `python3 todo.py add "<text>"` | Add a new todo |
| `python3 todo.py done <id>` | Mark a todo as complete |
| `python3 todo.py delete <id>` | Delete a todo (`del` and `rm` also work) |
| `python3 todo.py clear` | Remove all completed todos |

### Examples

```bash
# Add tasks
python3 todo.py add "Buy groceries"
python3 todo.py add "Call dentist"
python3 todo.py add "Write report"

# List tasks
python3 todo.py list
#   1  [ ]  Buy groceries
#   2  [ ]  Call dentist
#   3  [ ]  Write report

# Mark task 2 as done
python3 todo.py done 2

# Delete task 1
python3 todo.py delete 1

# Remove all completed tasks
python3 todo.py clear
```

### Data file

Todos are stored in `~/.todos.txt`. Each line is one task:

```
[ ] Buy groceries
[x] Call dentist
[ ] Write report
```

You can open and edit this file directly in any text editor.

## Running Tests

```bash
python3 -m unittest test_todo -v
```

Expected output:

```
test_add_blank_does_not_write (test_todo.TestAdd) ... ok
test_add_blank_prints_error (test_todo.TestAdd) ... ok
...
----------------------------------------------------------------------
Ran 30 tests in 0.002s

OK
```

The tests use a temporary file for isolation — your `~/.todos.txt` is never touched.
