# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/00_nb2bear.ipynb (unless otherwise specified).

__all__ = ['italics_regex', 'bold_regex', 'header_regex', 'header_starts', 'code_start', 'list_start', 's4', 'indents',
           'quote_start', 'img_start', 'xcall_path', 'load_nb', 'parse_nb', 'convert_nb_to_markdown', 'get_nb_images',
           'convert_to_pb_markup', 'are_empty', 'is_header', 'is_indented', 'is_code_marker',
           'is_empty_line_after_header', 'quote_if_code_output', 'format_markdown', 'convert_markdown_to_html',
           'add_images_to_html', 'get_nb_title', 'trash_existing_note', 'add_to_bear', 'convert_nb_to_bear']

# Cell
# hide
from bs4 import BeautifulSoup
from fastcore.test import *
from nbconvert import MarkdownExporter
from urllib.request import urlopen
from urllib.parse import quote
from typing import Union

import bs4
import json
import markdown2
import nbformat
import os
import re

# Cell
# italics_regex: re.Pattern = re.compile(r"(\*)([^\s]*?)(\*)")
italics_regex: re.Pattern = re.compile(r"\*(?=\S)(.+?)(?<=\S)\*")
bold_regex: re.Pattern = re.compile(r"(\*\*)([^\s]*?)(\*\*)")
header_regex: re.Pattern = re.compile(r"(#+)\s")
header_starts: tuple = ("# ", "## ", "### ", "#### ", "##### ", "###### ")
code_start: str = "```"
list_start: str = "* "
s4: str = " " * 4
indents: tuple = ("\t", s4)
quote_start: str = "> "
img_start: str = "!["
xcall_path: str = "./libs/xcall.app/Contents/MacOS/xcall"

# Cell
def load_nb(nb_fn: str) -> str:
    """Read a Jupyter notebook."""
    return urlopen(f"file://{nb_fn}").read().decode()

# Cell
def parse_nb(nb_contents: str) -> nbformat.notebooknode.NotebookNode:
    """Convert a Jupyter notebook to a dictionary-like format."""
    return nbformat.reads(nb_contents, as_version=4)

# Cell
def convert_nb_to_markdown(nb_contents: nbformat.notebooknode.NotebookNode) -> list:
    """Convert a Jupyter notebook to Markdown."""
    md_exporter = MarkdownExporter()
    nbc_out: str
    nbc_out, _ = md_exporter.from_notebook_node(nb_contents)

    return nbc_out.splitlines()

# Cell
def get_nb_images(nb_contents: nbformat.notebooknode.NotebookNode) -> list:
    """Extract base64 representations of images in notebook."""
    nb_images: list = []
    for nb_cell in nb_contents.cells:
        if "attachments" not in nb_cell.keys():
            continue
        for _, attachment in nb_cell["attachments"].items():
            if "image/png" not in attachment.keys():
                continue
            img_base64: str = attachment["image/png"]
            nb_images.append(img_base64)

    return nb_images

# Cell
def convert_to_pb_markup(line: str) -> str:
    """Transform specific Markdown syntax to compatible Polar Bear markup."""
    line = italics_regex.sub(r"/\1/", line)
    line = bold_regex.sub(r"\*\1\*", line)

    return line

# Cell
def are_empty(lines: list) -> bool:
    return all([(not x) for x in lines])

def is_header(line: str) -> bool:
    return bool(re.match(header_regex, line))

def is_indented(line: str) -> bool:
    return line.startswith(indents)

def is_code_marker(line: str) -> bool:
    return line.startswith(code_start)

def is_empty_line_after_header(line, last_line) -> bool:
    return is_header(last_line) and (not line)

def quote_if_code_output(line, last_two_lines) -> str:
    if (not last_two_lines[-1]) and is_code_marker(last_two_lines[-2]):
        return f"> {line}"
    else:
        return line

# Cell
def format_markdown(contents: list) -> str:
    """Format Jupyter exported Markdown to Bear-compatible format."""
    formatted_contents: list = [contents[0]]
    line: str
    for line in contents[1:]:
        last_line: str = formatted_contents[-1]
        last_two_lines: list = formatted_contents[-2:]

        # Skip more than one empty line.
        if are_empty([line, last_line]): continue
        if is_empty_line_after_header(line, last_line): continue

        if is_indented(line):
            line = quote_if_code_output(line, last_two_lines)

        line = convert_to_pb_markup(line)
        formatted_contents.append(line)

    return "\n".join(formatted_contents)

# Cell
def convert_markdown_to_html(contents: list) -> str:
    """Wrap markdown text in HTML tags."""
    md: str = "\n".join(contents)
    return markdown2.markdown(md, extras=["fenced-code-blocks", "cuddled-lists"])

# Cell
def add_images_to_html(html: str, imgs: list) -> str:
    """Embed images in base64 representation. (Currently not supported by Bear)"""
    html_soup: BeautifulSoup = BeautifulSoup(html)
    for i, img in enumerate(html_soup.findAll("img")):
        img["src"] = f"data:image/png;base64, {imgs[i]}"

    return str(html_soup)

# Cell
def get_nb_title(text: str) -> str:
    """Get note title."""
    heading: Union[bs4.element.Tag, None] = BeautifulSoup(text, "html.parser").h1
    if heading is None:
        # Content is markdown, assume the first line to be the heading.
        return re.sub(header_regex, "", text.splitlines()[0])
    else:
        return heading.string

# Cell
def trash_existing_note(title: str, api_token: str):
    """Delete an existing note with the same title to avoid duplicates."""
    search_output: dict = json.loads(os.popen(f"{xcall_path} -url 'bear://x-callback-url/search?term={quote(title)}"
                                              f"&show_window=no&token={api_token}'").read())
    current_notes: list = json.loads(search_output["notes"])
    note: dict
    for note in current_notes:
        if note["title"] == title:
            note_id: str = note["identifier"]
            os.popen(f"{xcall_path} -url 'bear://x-callback-url/trash?show_window=no&id={note_id}'")

# Cell
def add_to_bear(text: str, api_token: str, layout: str = "compact"):
    """Create a new Bear note."""
    title: str = get_nb_title(text)
    trash_existing_note(title, api_token)
    if layout == "comfortable":
        os.system(f"{xcall_path} -url 'bear://x-callback-url/create?type=html&url=&text={quote(text)}'")
    else:
        os.system(f"{xcall_path} -url 'bear://x-callback-url/create?text={quote(text)}'")

# Cell
def convert_nb_to_bear(nb_fn: str, api_token: str, layout: str = "compact"):
    """Convert a Jupyter notebook to a Bear page."""
    nb_raw: str = load_nb(nb_fn)
    nb_parsed: nbformat.notebooknode.NotebookNode = parse_nb(nb_raw)
    md_text: list = convert_nb_to_markdown(nb_parsed)
    if layout == "comfortable":
        nb_imgs: list = get_nb_images(nb_parsed)
        formatted_html: str = convert_markdown_to_html(md_text)
        html_with_images: str = add_images_to_html(formatted_html, nb_imgs)
        add_to_bear(html_with_images, api_token, layout)
    else:
        formatted_md: str = format_markdown(md_text)
        add_to_bear(formatted_md, api_token)