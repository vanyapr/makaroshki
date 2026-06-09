# Contributing

Macaroni Messenger is one HTML file first.

Before opening a pull request, ask:

- Can this stay inside `messenger.html`?
- Can this work without a backend?
- Can this use Git as the source of truth?
- Can this avoid a new dependency?
- Can this be understood at night without a diagram?

Preferred changes:

- small UI fixes;
- protocol-compatible `.macaroni` improvements;
- GitHub adapter hardening;
- browser storage repair tools;
- honest documentation;
- boring tests that catch real breakage.

Avoid:

- servers;
- build pipelines unless absolutely necessary;
- framework migrations;
- realtime infrastructure;
- enterprise abstractions;
- dependencies for problems that fit in a small function.

The product joke is not an excuse for broken software.

The implementation should remain readable, shippable, and cheap to maintain.

If a feature needs infrastructure comparable to a small bank, it probably does not belong here.

If it can be solved with HTML, JSON, and Git, start there.
