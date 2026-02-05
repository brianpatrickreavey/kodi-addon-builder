from semantic_release.commit_parser.scipy import ScipyCommitParser


class CustomScipyCommitParser(ScipyCommitParser):
    def __init__(self, **kwargs):
        super().__init__(
            types={
                "major_tags": ["remove"],
                "minor_tags": ["add", "change", "deprecate"],
                "patch_tags": ["fix", "security"],
                "other_allowed_tags": [],
            },
            **kwargs,
        )

    LONG_TYPE_NAMES = {
        "add": "Added",
        "change": "Changed",
        "deprecate": "Deprecated",
        "remove": "Removed",
        "fix": "Fixed",
        "security": "Security",
    }
