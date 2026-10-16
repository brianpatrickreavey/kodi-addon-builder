from dataclasses import field

from semantic_release.commit_parser.conventional import (
    ConventionalCommitParser,
    ConventionalCommitParserOptions,
)
from semantic_release.enums import LevelBump


class CustomConventionalCommitParserOptions(ConventionalCommitParserOptions):
    major_tags = ("remove",)
    minor_tags = ("add", "change", "deprecate")
    patch_tags = ("fix", "security")
    other_allowed_tags = ()
    allowed_tags = ("remove", "add", "change", "deprecate", "fix", "security")
    category_map: dict[str, str] = field(
        default={
            "feat": "feature",
            "fix": "bug fix",
            "perf": "performance",
            "refactor": "refactor",
            "docs": "documentation",
            "test": "test",
            "build": "build",
            "ci": "continuous integration",
            "chore": "chore",
            "style": "style",
            "revert": "revert",
            "breaking change": "breaking",
            "add": "feature",
            "change": "enhancement",
            "deprecate": "deprecation",
            "remove": "removal",
            "security": "security",
        }
    )

    def __post_init__(self):
        # Set the tag_to_level mapping
        self._tag_to_level = {tag: LevelBump.MAJOR for tag in self.major_tags}
        self._tag_to_level.update({tag: LevelBump.MINOR for tag in self.minor_tags})
        self._tag_to_level.update({tag: LevelBump.PATCH for tag in self.patch_tags})
        self._tag_to_level.update({tag: LevelBump.NO_RELEASE for tag in self.other_allowed_tags})
        # Set the category_map
        self.category_map = {
            "feat": "feature",
            "fix": "bug fix",
            "perf": "performance",
            "refactor": "refactor",
            "docs": "documentation",
            "test": "test",
            "build": "build",
            "ci": "continuous integration",
            "chore": "chore",
            "style": "style",
            "revert": "revert",
            "breaking change": "breaking",
            "add": "feature",
            "change": "enhancement",
            "deprecate": "deprecation",
            "remove": "removal",
            "security": "security",
        }


class CustomConventionalCommitParser(ConventionalCommitParser):
    def get_default_options(self) -> ConventionalCommitParserOptions:
        return ConventionalCommitParserOptions(
            minor_tags=("add", "change", "deprecate"),
            patch_tags=("fix", "security"),
            major_tags=("remove",),
            other_allowed_tags=(),
        )

    def get_category(self, commit_type: str) -> str:
        mapping = {
            "feat": "feature",
            "fix": "bug fix",
            "perf": "performance",
            "refactor": "refactor",
            "docs": "documentation",
            "test": "test",
            "build": "build",
            "ci": "continuous integration",
            "chore": "chore",
            "style": "style",
            "revert": "revert",
            "breaking change": "breaking",
            "add": "feature",
            "change": "enhancement",
            "deprecate": "deprecation",
            "remove": "removal",
            "security": "security",
        }
        return mapping.get(commit_type.lower(), "unknown")

    LONG_TYPE_NAMES = {
        "add": "Added",
        "change": "Changed",
        "deprecate": "Deprecated",
        "remove": "Removed",
        "fix": "Fixed",
        "security": "Security",
    }
