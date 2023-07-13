import os
import requests
import json

FUN_RESPONSE = {
    'statusCode': 200, 
                'body': ''
}

TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
API_KEY = os.environ['API_KEY']
AUTH_HEADER = f'Api-Key {API_KEY}'


def send_message(text, message):
    message_id = message['message_id']
    chat_id = message['chat']['id']
    reply_message = {
        'chat_id': chat_id,
        'text': text,
        'reply_to_message_id': message_id
    }

    requests.post(url=f'{TELEGRAM_API_URL}/sendMessage', json=reply_message)

def get_file(file_id):
    resp = requests.post(url=f'{TELEGRAM_API_URL}/getFile', json={'file_id': file_id})
    return resp.json()['result']

def handler(event, context):
    if TELEGRAM_BOT_TOKEN is None:
        return FUN_RESPONSE
    
    update = json.loads(event['body'])

    if 'message' not in update:
        return FUN_RESPONSE
    
    message_in = update['message']
    
    if 'voice' not in message_in:
        return FUN_RESPONSE

    voice = message_in['voice']

    duration = voice['duration']

    if duration > 30:
        send_message("Длительность записи не должна превышать 30 секунд", message_in)
        return FUN_RESPONSE

    file_id = voice['file_id']
    tg_file = get_file(file_id)
    tg_file_path = tg_file['file_path']

    file_resp = requests.get(url=f'https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{tg_file_path}')
    audio = file_resp.content

    stt_resp = requests.post(url='https://stt.api.cloud.yandex.net/speech/v1/stt:recognize', 
                            headers={'Authorization': AUTH_HEADER},
                            data=audio)

    if stt_resp.ok:
        send_message(stt_resp.json()['result'], message_in)
    else:
        send_message(f'Ошибка распознавания {stt_resp.text}', message_in)

    return FUN_RESPONSE
    