
import os
import openai
from dotenv import load_dotenv, find_dotenv

# load .env file to environment
_ = load_dotenv(find_dotenv())

client = openai.Client()



def text_generate(messages):

    response = client.chat.completions.create(
        messages=messages,
        model='gpt-3.5-turbo-0125',
        max_tokens=1000,
        temperature=0,
        stream=True ## faz com que de aparencia de chat mesmo porque pega stream a stream de tokens sendo enviados
    )

    print('Assistant: ', end='')
    complete_response = ''
    for stream_response in response:
        text = stream_response.choices[0].delta.content
        if text:
            complete_response += text
            print(text, end='')
    print()
    return complete_response


if __name__ == '__main__':
    messages = []

    print('Bem-vindo ao chatbot da Amanda')
    while True:
        user_input = input('User: ')
        messages.append({'role': 'user', 'content': user_input})
        complete_responses = text_generate(messages)
        messages.append({'role': 'assistant', 'content': complete_responses}) # salva o contexto para poder saber do que estamos falando
        print('MESSAGES', messages)
