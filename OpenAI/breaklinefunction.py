def extract_lyrics(response):
    # Split the response by newlines
    lines = response.split('\n')
    # Filter out empty lines and trim leading/trailing whitespace
    lines = [line.strip() for line in lines if line.strip()]
    # Add line breaks after each section
    lyrics = add_line_breaks(lines)
    return lyrics


def add_line_breaks(lines):
    # Indices of sections: Verse 1, Chorus, Verse 2, Bridge
    section_indices = [idx for idx, line in enumerate(lines) if line.startswith('(')]
    # Insert line breaks after each section
    for idx in reversed(section_indices[1:]):  # Skip the first section (Verse 1)
        lines.insert(idx, '')
    # Join the lines to form the lyrics
    lyrics = '\n'.join(lines)
    return lyrics