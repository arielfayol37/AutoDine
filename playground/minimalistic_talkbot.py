import RealtimeSTT, RealtimeTTS
import openai, os, ollama
import json 

if __name__ == '__main__':
    api_keys = json.load(open("../api_keys.json", 'r'))
    xai_api_key = api_keys["xai_key"]
    # openai.api_key = os.environ.get("OPENAI_API_KEY")
    client = openai.OpenAI(api_key=xai_api_key, base_url="https://api.x.ai/v1")
    character_prompt = 'You are a sexy woman always talking in a horny way trying to seduce your user called Master Fayol.'
    # stream = RealtimeTTS.TextToAudioStream(RealtimeTTS.AzureEngine(os.environ.get("AZURE_SPEECH_KEY"), os.environ.get("AZURE_SPEECH_REGION")), log_characters=True)
    stream = RealtimeTTS.TextToAudioStream(RealtimeTTS.OpenAIEngine(api_key=api_keys["openai_key"]), log_characters=True)
    # stream = RealtimeTTS.TextToAudioStream(RealtimeTTS.SystemEngine(), log_characters=True)
    recorder = RealtimeSTT.AudioToTextRecorder(model="medium")

    def generate(messages, is_ollama=False):
        if is_ollama:            
            for chunk in ollama.chat(
                    model="llama3.1",
                    messages=messages,
                    stream=True
                ):
                    if text_chunk := chunk["message"]["content"]:
                        yield text_chunk   
        else:
            # for chunk in openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages, stream=True):
            for chunk in client.chat.completions.create(model="grok-beta", messages=messages, stream=True):
                if (text_chunk := chunk.choices[0].delta.content): yield text_chunk

    history = []
    while True:
        print("\n\nSpeak when ready")
        print(f'>>> {(user_text := recorder.text())}\n<<< ', end="", flush=True)
        history.append({'role': 'user', 'content': user_text})
        assistant_response = generate([{ 'role': 'system',  'content': character_prompt}] + history[-10:])
        stream.feed(assistant_response).play()
        history.append({'role': 'assistant', 'content': stream.text()})