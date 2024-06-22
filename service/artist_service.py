from openai import OpenAI

OPENAI_API_KEY = ""
openai_client = OpenAI(api_key=OPENAI_API_KEY)


def generate_lyrics_artist(prompt, artist, language):
    completion = openai_client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[
            {"role": "system", "content": ""},
            {"role": "user",
             "content": f"generate a lyrics that have song topic is {prompt} in {language} language and and in the style of {artist} artist. (just give me only lyrics)"}
        ]
    )
    response = completion.choices[0].message.content
    lyrics = extract_lyrics(response)
    return lyrics



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