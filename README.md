# bus-client

Stdlib Python client for an **append-only TSV coordination log** — a minimal
message bus with columns `timestamp<TAB>sender<TAB>recipient<TAB>type<TAB>message`.

Dependency-free, local-file backed, and generic: it carries no fleet-specific
identity or bridge configuration. Message fields are escaped on write and
unescaped on read.

## Usage

```python
from bus_client import append_row, tail, search, status

append_row("log.tsv", "agent-a", "all", "STATUS", "hello")
tail("log.tsv", 10)
search("log.tsv", "hello")
status("log.tsv")
```

## License

MIT.
