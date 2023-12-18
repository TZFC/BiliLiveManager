async def update_page(target, checkin_days, content):
    highest_count = content[0][-1]
    new_content = []
    for rank, (uid, username, count) in enumerate(content):
        top_class = 'top' if count == highest_count else 'not_top'
        count_class = f"_{count}"
        id = f"_{rank + 1}"
        name = username if username else str(uid)
        new_content.append(f'<p id={id} class="{top_class} {count_class}">{name} {count}/{checkin_days}</p>')
    new_paragraphs = "\n".join(new_content)
    with open("web/ROOM_ID.html") as file:
        template = file.read()
    before, after = template.split("<p>")
    page = before + new_paragraphs + after
    with open(target, "w") as file:
        file.write(page)
