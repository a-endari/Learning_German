"""Small object-oriented Wiktionary API client for German words.

Examples:
    python examples/wiktionary_german_client.py gehen
    python examples/wiktionary_german_client.py Name --json
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class WiktionarySection:
    """A section extracted from the German part of a Wiktionary page."""

    title: str
    body: str


@dataclass(frozen=True)
class WiktionaryMeaning:
    """One definition with one example sentence when Wiktionary provides it."""

    definition: str
    example: str | None = None


@dataclass(frozen=True)
class WiktionaryEntry:
    """Dictionary-like information collected for one Wiktionary page."""

    query: str
    title: str
    page_id: int | None
    exists: bool
    url: str | None = None
    extract: str | None = None
    german_wikitext: str | None = None
    sections: list[WiktionarySection] = field(default_factory=list)
    meanings: list[WiktionaryMeaning] = field(default_factory=list)
    pronunciations: list[str] = field(default_factory=list)
    synonyms: list[str] = field(default_factory=list)
    antonyms: list[str] = field(default_factory=list)
    raw_wikitext: str | None = None


class WiktionaryApiError(RuntimeError):
    """Raised when the MediaWiki API request fails."""


class WiktionaryClient:
    """Read-only client for the English Wiktionary MediaWiki Action API."""

    API_URL = "https://en.wiktionary.org/w/api.php"
    ARTICLE_URL = "https://en.wiktionary.org/wiki/{title}"

    def __init__(self, user_agent: str = "GermanWiktionaryClient/1.0") -> None:
        self.user_agent = user_agent

    def lookup(self, term: str, *, include_raw: bool = False) -> WiktionaryEntry:
        """Fetch a page and extract German dictionary information.

        Wiktionary stores all languages for a spelling on one page. This method
        keeps the full article extract, then isolates the "German" section when
        it is present.
        """

        term = term.strip()
        if not term:
            raise ValueError("term cannot be empty")

        page = self._get_page(term)
        page_id = page.get("pageid")
        title = str(page.get("title", term))

        if "missing" in page:
            suggestion = self.search(term, limit=1)
            suggested_title = suggestion[0] if suggestion else title
            return WiktionaryEntry(
                query=term,
                title=suggested_title,
                page_id=None,
                exists=False,
                url=self.ARTICLE_URL.format(title=suggested_title.replace(" ", "_")),
            )

        raw_wikitext = self._extract_revision_text(page)
        german_wikitext = self._extract_language_section(raw_wikitext, "German")
        sections = self._split_subsections(german_wikitext)
        meanings = self._extract_meanings(german_wikitext)
        pronunciations = self._extract_pronunciations(sections)
        synonyms = self._dedupe(
            self._extract_named_section_items(sections, "Synonyms")
            + self._extract_relation_template_items(german_wikitext, "syn")
        )
        antonyms = self._dedupe(
            self._extract_named_section_items(sections, "Antonyms")
            + self._extract_relation_template_items(german_wikitext, "ant")
        )
        extract = self._get_plain_article(title)

        return WiktionaryEntry(
            query=term,
            title=title,
            page_id=int(page_id) if page_id is not None else None,
            exists=True,
            url=self.ARTICLE_URL.format(title=title.replace(" ", "_")),
            extract=extract,
            german_wikitext=german_wikitext,
            sections=sections,
            meanings=meanings,
            pronunciations=pronunciations,
            synonyms=synonyms,
            antonyms=antonyms,
            raw_wikitext=raw_wikitext if include_raw else None,
        )

    def search(self, term: str, *, limit: int = 10) -> list[str]:
        """Return page title suggestions from Wiktionary search."""

        data = self._request(
            {
                "action": "opensearch",
                "search": term,
                "limit": str(limit),
                "namespace": "0",
            }
        )
        if isinstance(data, list) and len(data) >= 2 and isinstance(data[1], list):
            return [str(item) for item in data[1]]
        return []

    def _get_page(self, title: str) -> dict[str, Any]:
        data = self._request(
            {
                "action": "query",
                "prop": "revisions",
                "titles": title,
                "rvslots": "main",
                "rvprop": "content",
                "redirects": "1",
                "formatversion": "2",
            }
        )
        pages = data.get("query", {}).get("pages", [])
        if not pages:
            raise WiktionaryApiError(f"No page data returned for {title!r}")
        return pages[0]

    def _get_plain_article(self, title: str) -> str | None:
        data = self._request(
            {
                "action": "parse",
                "page": title,
                "prop": "text",
                "formatversion": "2",
                "redirects": "1",
            }
        )
        rendered = data.get("parse", {}).get("text")
        if not isinstance(rendered, str):
            return None
        return self._html_to_text(rendered)

    def _request(self, params: dict[str, str]) -> Any:
        query = {"format": "json", **params}
        url = f"{self.API_URL}?{urlencode(query)}"
        request = Request(url, headers={"User-Agent": self.user_agent})
        try:
            with urlopen(request, timeout=20) as response:
                payload = response.read().decode("utf-8")
        except HTTPError as exc:
            raise WiktionaryApiError(f"Wiktionary returned HTTP {exc.code}") from exc
        except URLError as exc:
            raise WiktionaryApiError(f"Could not reach Wiktionary: {exc.reason}") from exc

        data = json.loads(payload)
        if isinstance(data, dict) and "error" in data:
            message = data["error"].get("info", "unknown API error")
            raise WiktionaryApiError(message)
        return data

    @staticmethod
    def _extract_revision_text(page: dict[str, Any]) -> str:
        revisions = page.get("revisions", [])
        if not revisions:
            return ""
        slots = revisions[0].get("slots", {})
        main = slots.get("main", {})
        return str(main.get("content", ""))

    @staticmethod
    def _extract_language_section(wikitext: str, language: str) -> str:
        pattern = re.compile(rf"^==\s*{re.escape(language)}\s*==\s*$", re.MULTILINE)
        match = pattern.search(wikitext)
        if not match:
            return ""

        next_language = re.search(r"^==[^=].*?==\s*$", wikitext[match.end() :], re.MULTILINE)
        end = match.end() + next_language.start() if next_language else len(wikitext)
        return wikitext[match.end() : end].strip()

    @staticmethod
    def _split_subsections(wikitext: str) -> list[WiktionarySection]:
        sections: list[WiktionarySection] = []
        matches = list(re.finditer(r"^(={3,6})\s*(.*?)\s*\1\s*$", wikitext, re.MULTILINE))
        for index, match in enumerate(matches):
            start = match.end()
            end = matches[index + 1].start() if index + 1 < len(matches) else len(wikitext)
            title = WiktionaryClient._clean_markup(match.group(2))
            body = wikitext[start:end].strip()
            if title and body:
                sections.append(WiktionarySection(title=title, body=body))
        return sections

    @staticmethod
    def _extract_meanings(wikitext: str) -> list[WiktionaryMeaning]:
        meanings: list[WiktionaryMeaning] = []
        current_definition: str | None = None
        current_example: str | None = None

        for line in wikitext.splitlines():
            if line.startswith("#") and not line.startswith(("#*", "#:", "##")):
                if current_definition:
                    meanings.append(
                        WiktionaryMeaning(
                            definition=current_definition,
                            example=current_example,
                        )
                    )

                current_definition = WiktionaryClient._clean_markup(line.lstrip("# ").strip())
                current_example = None
                continue

            if current_definition and current_example is None and line.startswith(("#*", "#:")):
                if re.search(r"\{\{(?:syn|ant)\|de\|", line):
                    continue

                cleaned = WiktionaryClient._clean_markup(line.lstrip("#*: ").strip())
                if cleaned:
                    current_example = cleaned

        if current_definition:
            meanings.append(
                WiktionaryMeaning(
                    definition=current_definition,
                    example=current_example,
                )
            )

        return meanings

    @staticmethod
    def _extract_pronunciations(sections: list[WiktionarySection]) -> list[str]:
        pronunciations: list[str] = []
        for section in sections:
            if section.title.casefold() != "pronunciation":
                continue

            for line in section.body.splitlines():
                cleaned = WiktionaryClient._clean_markup(line.lstrip("*: ").strip())
                if "IPA" in cleaned or cleaned.startswith(("/", "[")):
                    pronunciations.append(cleaned)

        return WiktionaryClient._dedupe(pronunciations)

    @staticmethod
    def _extract_named_section_items(
        sections: list[WiktionarySection],
        wanted_title: str,
    ) -> list[str]:
        items: list[str] = []
        for section in sections:
            if section.title.casefold() != wanted_title.casefold():
                continue

            for line in section.body.splitlines():
                stripped = line.strip()
                if not stripped.startswith("*"):
                    continue

                cleaned = WiktionaryClient._clean_markup(stripped.lstrip("* ").strip())
                if cleaned:
                    items.append(cleaned)

        return WiktionaryClient._dedupe(items)

    @staticmethod
    def _extract_relation_template_items(wikitext: str, relation: str) -> list[str]:
        items: list[str] = []
        pattern = re.compile(rf"\{{\{{{re.escape(relation)}\|de\|([^{{}}]+?)\}}\}}")
        for match in pattern.finditer(wikitext):
            for item in WiktionaryClient._clean_template_terms(match).split(","):
                cleaned = item.strip()
                if cleaned:
                    items.append(cleaned)
        return WiktionaryClient._dedupe(items)

    @staticmethod
    def _dedupe(items: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for item in items:
            key = item.casefold()
            if key in seen:
                continue
            seen.add(key)
            result.append(item)
        return result

    @staticmethod
    def _clean_markup(text: str) -> str:
        text = re.sub(r"\{\{IPA\|de\|([^{}]+?)\}\}", WiktionaryClient._clean_template_terms, text)
        text = re.sub(r"\{\{syn\|de\|([^{}]+?)\}\}", WiktionaryClient._clean_template_terms, text)
        text = re.sub(r"\{\{ant\|de\|([^{}]+?)\}\}", WiktionaryClient._clean_template_terms, text)
        text = re.sub(r"\{\{uxi?\|de\|([^}|]+).*?\}\}", r"\1", text)
        text = re.sub(r"\{\{m\|de\|([^}|]+).*?\}\}", r"\1", text)
        text = re.sub(r"\{\{l\|de\|([^}|]+).*?\}\}", r"\1", text)
        text = re.sub(r"\{\{q\|([^{}]+?)\}\}", r"(\1)", text)
        while re.search(r"\{\{[^{}]*\}\}", text):
            text = re.sub(r"\{\{q\|([^{}]+?)\}\}", r"(\1)", text)
            text = re.sub(r"\{\{[^{}]*\}\}", "", text)
        text = re.sub(r"\[\[([^]|]+)\|([^]]+)\]\]", r"\2", text)
        text = re.sub(r"\[\[([^]]+)\]\]", r"\1", text)
        text = text.replace("'''", "").replace("''", "")
        return html.unescape(re.sub(r"\s+", " ", text)).strip()

    @staticmethod
    def _clean_template_terms(match: re.Match[str]) -> str:
        terms = []
        for part in match.group(1).split("|"):
            if "=" in part:
                continue
            cleaned = part.strip()
            if cleaned:
                terms.append(cleaned)
        return ", ".join(terms)

    @staticmethod
    def _html_to_text(rendered_html: str) -> str:
        text = re.sub(r"(?is)<(script|style).*?>.*?</\1>", "", rendered_html)
        text = re.sub(r"(?i)<br\s*/?>", "\n", text)
        text = re.sub(r"(?i)</(p|div|li|h[1-6]|tr)>", "\n", text)
        text = re.sub(r"<[^>]+>", "", text)
        lines = [html.unescape(line).strip() for line in text.splitlines()]
        return "\n".join(line for line in lines if line)


def print_entry(entry: WiktionaryEntry) -> None:
    if not entry.exists:
        print(f"No exact Wiktionary page found for {entry.query!r}.")
        print(f"Closest article candidate: {entry.title}")
        print(f"URL: {entry.url}")
        return

    print(f"{entry.title}")
    print(f"URL: {entry.url}")
    print()

    if entry.meanings:
        print("German meanings:")
        for index, meaning in enumerate(entry.meanings, start=1):
            print(f"{index}. {meaning.definition}")
            if meaning.example:
                print(f"   Example: {meaning.example}")
        print()
    else:
        print("No German definition lines were found on this page.")
        print()

    if entry.pronunciations:
        print("Pronunciation:")
        for pronunciation in entry.pronunciations:
            print(f"- {pronunciation}")
        print()

    if entry.synonyms:
        print("Synonyms:")
        for synonym in entry.synonyms:
            print(f"- {synonym}")
        print()

    if entry.antonyms:
        print("Antonyms:")
        for antonym in entry.antonyms:
            print(f"- {antonym}")
        print()

    if entry.sections:
        print("German sections:")
        for section in entry.sections:
            print(f"- {section.title}")
        print()

    if entry.extract:
        print("Article preview:")
        print(entry.extract[:1500])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Look up German entries on English Wiktionary.")
    parser.add_argument("term", help="German word/name/verb to look up, for example 'gehen'.")
    parser.add_argument("--json", action="store_true", help="Print the complete result as JSON.")
    parser.add_argument("--raw", action="store_true", help="Include raw page wikitext in JSON output.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    client = WiktionaryClient()

    try:
        entry = client.lookup(args.term, include_raw=args.raw)
    except (ValueError, WiktionaryApiError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(asdict(entry), ensure_ascii=False, indent=2))
    else:
        print_entry(entry)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
