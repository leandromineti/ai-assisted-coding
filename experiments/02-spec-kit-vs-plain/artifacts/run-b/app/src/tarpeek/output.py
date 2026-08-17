"""Table and JSON renderers for archive member listings."""

import json

from tarpeek.archive import ArchiveMember

_COLUMNS = ("NAME", "TYPE", "SIZE", "LAST_MODIFIED")


def render_table(members: list[ArchiveMember]) -> str:
    """Render members as a fixed-width, left-aligned plain-text table."""
    name_width = max([len(_COLUMNS[0])] + [len(m.name) for m in members])
    type_width = max([len(_COLUMNS[1])] + [len(m.type) for m in members])
    size_width = max([len(_COLUMNS[2])] + [len(str(m.size)) for m in members])

    header = (
        f"{_COLUMNS[0]:<{name_width}}  {_COLUMNS[1]:<{type_width}}  "
        f"{_COLUMNS[2]:>{size_width}}  {_COLUMNS[3]}"
    )
    lines = [header]
    for member in members:
        lines.append(
            f"{member.name:<{name_width}}  {member.type:<{type_width}}  "
            f"{member.size:>{size_width}}  {member.last_modified}"
        )
    return "\n".join(lines)


def render_json(members: list[ArchiveMember]) -> str:
    """Render members as a JSON array of snake_case objects."""
    return json.dumps(
        [
            {
                "name": m.name,
                "type": m.type,
                "size": m.size,
                "last_modified": m.last_modified,
            }
            for m in members
        ]
    )
