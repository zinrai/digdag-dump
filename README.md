# digdag-dump

A command-line tool to fetch [Digdag](https://www.digdag.io/) resources via the Web API and save them as JSON files.

Built with Python 3 standard library only — no external dependencies.

## Requirements

- Python 3.6+

## Usage

```
python3 digdag_dump.py [OPTIONS] --resource RESOURCE
```

### Options

| Option       | Default                    | Description                                       |
|--------------|----------------------------|---------------------------------------------------|
| `--url`      | `http://localhost:65432`   | Digdag server URL                                 |
| `--resource` | *(required)*               | Resource to fetch (`projects`, `workflows`, `sessions`, `attempts`, `schedules`) |
| `--count`    | `100`                      | Number of records per API request                 |
| `--limit`    | `1000`                     | Maximum total records to fetch (`0` for no limit) |

### Examples

```bash
# Fetch projects (up to 1000 by default)
python3 digdag_dump.py --resource projects

# Fetch from a remote server
python3 digdag_dump.py --url http://digdag.example.com:65432 --resource workflows

# Fetch all sessions with no limit
python3 digdag_dump.py --limit 0 --resource sessions

# Fetch the latest 500 attempts
python3 digdag_dump.py --limit 500 --resource attempts
```

### Output

Each run creates `{resource}_list.json` in the current directory.

## License

This project is licensed under the [MIT License](./LICENSE).
