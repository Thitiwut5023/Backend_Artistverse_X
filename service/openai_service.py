from openai import OpenAI
from breaklinefunction import extract_lyrics

OPENAI_API_KEY = ""
openai_client = OpenAI(api_key=OPENAI_API_KEY)


def generate_lyrics_genre(prompt, genre, language):
    completion = openai_client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[
            {"role": "system", "content": ""},
            {"role": "user",
             "content": f"generate a lyrics that have song topic is {prompt} in {language} language and the genre is {genre}. (just give me only lyrics)"}
        ]
    )
    response = completion.choices[0].message.content
    lyrics = extract_lyrics(response)
    return lyrics


def generate_lyrics_mood(prompt, mood, language):
    completion = openai_client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[
            {"role": "system", "content": ""},
            {"role": "user",
             "content": f"generate a lyrics that have song topic is {prompt} in {language} language and the mood is {mood}. (just give me only lyrics)"}
        ]
    )
    response = completion.choices[0].message.content
    lyrics = extract_lyrics(response)
    return lyrics


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
