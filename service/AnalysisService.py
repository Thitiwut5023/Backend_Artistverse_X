from openai import OpenAI


class AnalysisService:
    def __init__(self, api_key):
        self.openai_client = OpenAI(api_key=api_key)

    def analysis_lyrics(self, lyrics):
        completion = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=[
                {"role": "system", "content": ""},
                {"role": "user",
                 "content": f" based on my lyrics {lyrics} can you provide a suggestion of chord,keys,time signature,tempo and extract musical information for me that related with my lyrics"}
            ]
        )

        response = completion.choices[0].message.content
        analysis = response

        return analysis

