from openai import OpenAI
from util.extract_lyrics import extract_lyrics


class ArtistService:
    def __init__(self, api_key):
        self.openai_client = OpenAI(api_key=api_key)

    def generate_lyrics_artist(self, prompt, artist, language):
        completion = self.openai_client.chat.completions.create(
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

