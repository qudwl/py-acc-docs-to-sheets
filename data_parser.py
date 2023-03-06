def get_paragraph_tag(p):
    tags = {
        "NORMAL_TEXT": "p",
        "SUBTITLE": "blockquote",
        "HEADING_1": "h1",
        "HEADING_2": "h2",
        "HEADING_3": "h3",
        "HEADING_4": "h4",
        "HEADING_5": "h5",
    }
    if p is not None:
        if p.get("paragraphStyle") is not None:
            return tags.get(p.get("paragraphStyle").get("namedStyleType"))
    return None


def get_list_tag(list):
    if list is not None:
        list_prop = list.get("listProperties")
        if list_prop is not None:
            nesting_levels = list_prop.get("nestingLevels")
            if nesting_levels is not None:
                if nesting_levels[0] is not None:
                    glygh_type = nesting_levels[0].get("glyphType")

                    if glygh_type is not None:
                        return "ol"
                    else:
                        return "ul"
    return None


def clean_text(text):
    result = text.replace("\n", "")
    result = result.strip()

    return result


def get_nested_list_indent(level, list_tag):
    indent_type = "1." if (list_tag == "ol") else "-"
    return "{}{} ".format("\t" * level, indent_type)


def get_text_from_paragraph_filter(item):
    if item is not None and item.get("content") != "\n":
        return True
    return False


def get_text_from_paragraph_map(item):
    if item.get("elements") is not None:
        return get_text(item)
    else:
        return ""


def get_text_from_paragraph(p):
    elements = p.get("elements")

    if elements is not None:
        result = filter(get_text_from_paragraph_filter, elements)
        result = map(get_text_from_paragraph_map, result)
        return "".join(result)

    return ""


def get_table_cell_content(content):
    if len(content) == 0:
        return ""
    return "".join([clean_text(get_text_from_paragraph(c['paragraph'])) for c in content])


def get_image(document, element):
    inline_objects = document.get("inlineObjects")

    if not inline_objects or not element.get("inlineObjectElement"):
        return None

    inline_object = inline_objects[element["inlineObjectElement"]
                                   ["inlineObjectId"]]
    embedded_object = inline_object["inlineObjectProperties"]["embeddedObject"]

    if embedded_object and embedded_object.get("imageProperties"):
        return {
            "source": embedded_object["imageProperties"]["contentUri"],
            "title": embedded_object.get("title", ""),
            "alt": embedded_object.get("description", ""),
        }

    return None


def get_bullet_content(document, element):
    if element.get("inlineObjectElement"):
        image = get_image(document, element)
        if image is not None:
            return f"![{image.get('alt')}]({image.get('source')} '{image.get('title')}')"

    return get_text(element)


def get_text(element, is_header=False):
    text = clean_text(element.get("textRun").get("content"))
    link = element.get("textRun").get("textStyle").get("link")
    underline = element["textRun"]["textStyle"].get("underline")
    strikethrough = element["textRun"]["textStyle"].get("strikethrough")
    bold = element["textRun"]["textStyle"].get("bold")
    italic = element["textRun"]["textStyle"].get("italic")

    text = text.replace("*", "\\*")
    text = text.replace("_", "\\_")

    if underline:
        # Underline isn't supported in markdown so we'll use emphasis
        text = f"_{text}_"

    if italic:
        text = f"_{text}_"

    # Set bold unless it's a header
    if bold and not is_header:
        text = f"**{text}**"

    if strikethrough:
        text = f"~~{text}~~"

    if link:
        return f"[{text}]({link['url']})"

    return text


def get_cover(document):
    headers = document['headers']
    document_style = document.get('documentStyle')

    if not document_style or not document_style.get('firstPageHeaderId') or not headers.get(document_style['firstPageHeaderId']):
        return None

    header_element = headers[document_style['firstPageHeaderId']
                             ]['content'][0]['paragraph']['elements'][0]
    image = get_image(document, header_element)

    return {'image': image['source'], 'title': image['title'], 'alt': image['alt']} if image else None


def convert_google_document_to_json(document):
    body = document.get("body", {})
    footnotes = document.get("footnotes", {})
    cover = get_cover(document)

    content = []
    footnoteIDs = {}

    for i, element in enumerate(body.get("content", [])):
        paragraph = element.get("paragraph")
        table = element.get("table")

        if paragraph:
            tag = get_paragraph_tag(paragraph)

            if "bullet" in paragraph:
                listId = paragraph["bullet"]["listId"]
                list = document.get("lists", {}).get(listId, {})
                listTag = get_list_tag(list)

                bulletContent = " ".join(
                    [
                        get_bullet_content(document, el)
                        for el in paragraph.get("elements", [])
                    ]
                ).replace(" .", ".").replace(" ,", ",")

                prev = body.get("content", [])[i - 1]
                prevListId = None
                if "bullet" in prev["paragraph"]:
                    prevListId = prev["paragraph"]["bullet"]["listId"]

                if prevListId == listId:
                    content[-1][listTag].append(
                        f"\n{get_nested_list_indent(paragraph['bullet'].get('nestingLevel', 0), listTag)} {bulletContent}"
                        if paragraph['bullet'].get('nestingLevel') is not None
                        else bulletContent
                    )
                else:
                    content.append({listTag: [bulletContent]})

            elif tag:
                tagContent = []

                for el in paragraph.get("elements", []):
                    if el.get("inlineObjectElement"):
                        image = get_image(document, el)

                        if image:
                            tagContent.append({"img": image})

                    elif el.get("textRun") and el["textRun"].get("content") != "\n":
                        tagContent.append(
                            {
                                tag: get_text(
                                    el, tag != "p"
                                )
                            }
                        )

                    elif el.get("footnoteReference"):
                        tagContent.append(
                            {
                                tag: f"[^{el['footnoteReference']['footnoteNumber']}]"
                            }
                        )
                        footnoteIDs[el["footnoteReference"]["footnoteId"]] = el[
                            "footnoteReference"
                        ]["footnoteNumber"]

                if all(tag in item for item in tagContent for tag in item):
                    content.append(
                        {
                            tag: " ".join(
                                [item[tag] for item in tagContent]
                            ).replace(" .", ".").replace(" ,", ",")
                        }
                    )
                else:
                    content.extend(tagContent)

        elif table and table.get("tableRows", []):
            thead, *tbody = table["tableRows"]
            content.append(
                {
                    "table": {
                        "headers": [
                            get_table_cell_content(cell.get("content"))
                            for cell in thead.get("tableCells", [])
                        ],
                        "rows": [
                            [
                                get_table_cell_content(cell.get("content"))
                                for cell in row.get("tableCells", [])
                            ]
                            for row in tbody
                        ],
                    }
                }
            )
    formatedFootnotes = [
        {
            "footnote": {
                "number": footnoteIDs[value["footnoteId"]],
                "text": " ".join(
                    [
                        get_text(element)
                        for element in value.get("content", [])[0]
                        .get("paragraph", {})
                        .get("elements", [])
                    ]
                ).replace(" .", ".").replace(" ,", ","),
            }
        }
        for _, value in footnotes.items()
    ]
    formatedFootnotes.sort(
        key=lambda item: int(item["footnote"]["number"])
    )

    content.append(formatedFootnotes)

    return content  # type: ignore
