# Contributing

Macaroni Messenger is one HTML file first.

At this stage, code is not the only useful contribution.

Honestly, it may not even be the most useful one.

The project already has enough JavaScript to make a browser briefly reconsider its life choices.

What helps a lot:

- documentation;
- examples;
- clearer warnings;
- better jokes that still explain the architecture;
- sarcastic notes that make a serious point;
- small corrections that make the project easier to understand.

The repository should not become Encyclopedia Dramatica.

It can, however, borrow the useful part: a contributor may add style, edge, and ridicule, as long as the result still helps the reader understand what is going on.

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
- documentation that is funny because it is accurate;
- boring temporary checks that catch real breakage and do not have to live in the repo forever.

Especially welcome:

- Russian and English documentation kept in sync;
- shorter explanations of existing decisions;
- sharper phrasing for boring limitations;
- real-world examples of weird git-host behavior;
- notes that explain why a thing is funny without turning the repo into stand-up.

Avoid:

- servers;
- build pipelines unless absolutely necessary;
- framework migrations;
- realtime infrastructure;
- enterprise abstractions;
- dependencies for problems that fit in a small function.
- adding new code because writing prose felt too honest.

The product joke is not an excuse for broken software.

The implementation should remain readable, shippable, and cheap to maintain.

If a feature needs infrastructure comparable to a small bank, it probably does not belong here.

If it can be solved with HTML, JSON, and Git, start there.

If it can be solved by documenting the existing weirdness better, start there even earlier.
