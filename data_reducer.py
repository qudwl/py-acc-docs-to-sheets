import re


attr_arr = ["URL", "Executive Summary", "Browsers", "Tools"]


def attr_reducer(index, cur, next):
    if "Test URL" in cur:
        result = ""
        if "[_" not in cur:
            first = next.index("[_")
            last = next.index("_]")
            result = next[first + 2:last]
        else:
            first = cur.index("[_")
            last = cur.index("_]")
            result = cur[first + 2:last]
        return [True, result]
    elif attr_arr[index] in cur:
        return [True, next]
    else:
        return [False]


def data_reducer(page, title, lst):
    result = {"page": page}
    result["title"] = title[title.index(":") + 1:]
    result["desc"] = lst[0][lst[0].rfind("*") + 2:]
    result["rec"] = lst[1][lst[1].rfind("*") + 2:]
    result["succ"] = lst[2][lst[2].rfind("*") + 2:]

    return result


def reducer(body):
    data = {}

    start_index = 0
    cur_reducer_index = 0

    while start_index < len(body):
        key_cur = list(body[start_index].keys())[0]
        next_key = list(body[start_index + 1].keys())[0]
        result = attr_reducer(cur_reducer_index,
                              body[start_index][key_cur], body[start_index + 1][next_key])

        if result is not None and result[0]:
            data[attr_arr[cur_reducer_index]] = result[1]
            cur_reducer_index += 1

        if cur_reducer_index >= len(attr_arr):
            start_index += 1
            while "h1" not in body[start_index]:
                start_index += 1
            break

        start_index += 1

    arr = None
    page = None
    title = None
    findings = []
    wcag = []

    while start_index < len(body):
        if isinstance(body[start_index], dict):
            key = list(body[start_index].keys())[0]
            if key == "h1":
                page = body[start_index]["h1"]
            elif key == "ol":
                arr = body[start_index]["ol"]
            elif key == "h3":
                title = body[start_index]["h3"]

            if arr and page and title:
                data.update(data_reducer(page, title, arr))
                match = re.search(r"\d", data["succ"])
                if match:
                    index = match.start()
                    critera = data["succ"][index: index + 5]
                    data["succ"] = critera

                    if critera not in wcag:
                        wcag.append(critera)
                findings.append(data)
                arr = None
                title = None

        start_index += 1

    wcag_format = [[i] for i in wcag]

    data["findings"] = findings
    data["wcag"] = wcag_format
    return data
