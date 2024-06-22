def extract_lyrics(response):
    lines = response.split('\n')
    lines = [line.strip() for line in lines if line.strip()]
    lyrics = add_line_breaks(lines)
    return lyrics


def add_line_breaks(lines):
    section_indices = [idx for idx, line in enumerate(lines) if line.startswith('(')]
    for idx in reversed(section_indices[1:]):
        lines.insert(idx, '')
    lyrics = '\n'.join(lines)
    return lyrics