import json
import yfinance as yf

import openai
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())

client = openai.Client()

ticker = 'ABEV3'

ticker_obj = yf.Ticker(f'{ticker}.SA')

print('ticker_obj ', ticker_obj)

ticker_obj.history()


def retorna_cotacao_historica(ticker, periodo):
    print('recendo ', ticker, periodo)
    ticker_obj = yf.Ticker(f'{ticker}.SA')
    hist = ticker_obj.history(period= periodo, auto_adjust=True)
    if len(hist) > 30:
        slice_size = int(len(hist)/30)
        hist = hist.iloc[::-slice_size][::-1]
    hist.index = hist.index.strftime('%m-%d-%Y')
    return hist['Close'].to_json()

funcoes_disponiveis = {
    "retorna_cotacao_historica": retorna_cotacao_historica,
}    

tools = [
    {
        "type": "function",
        "function": {
            "name": "retorna_cotacao_historica",
            "description": "Obtém a cotação de hoje e a cotação histórica de uma ação do mercado financeiro",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "O nome da ação",
                    },
                    "periodo": {
                        "type": "string", 
                        "description": "o periodo que eu gostaria de consultar, quando o periodo for hoje ou agora, use 1d"
                    },
                },
                "required": ["ticker", "periodo"],
            },
        },
    }
]


def text_generate(messages):

    new_messages = messages

    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=new_messages,
        tools=tools,
        tool_choice="auto",
    )

    mensagem_resp = response.choices[0].message
    tool_calls = mensagem_resp.tool_calls

    if tool_calls:
        new_messages.append(mensagem_resp)
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = funcoes_disponiveis[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(
                ticker=function_args.get("ticker"),
                periodo=function_args.get("periodo"),
            )
            new_messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )
    segunda_resposta = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=new_messages,
    )   

    mensagem_resp = segunda_resposta.choices[0].message
    print('Assistant: ', end='')
    print(mensagem_resp.content)
    return new_messages


if __name__ == '__main__':
    messages = []

    print('Bem-vindo ao chatbot de consulta de cotações!')
    print('Você pode me fazer perguntas como:')
    print('- Qual é a cotação da ambev agora?')
    print('- Qual a variação de preço da ação da ambev em um ano?')

    while True:
        user_input = input('User: ')
        messages.append({'role': 'user', 'content': user_input})
        complete_responses = text_generate(messages)
        messages.append({'role': 'assistant', 'content': complete_responses}) # salva o contexto para poder saber do que estamos falando