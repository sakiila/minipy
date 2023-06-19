import csv
import html
import json
import os
import random

import requests
from bs4 import BeautifulSoup


def get_data(text):
    breed_name = text.find('meta', attrs={'name': 'og:breed'}).get('content')
    print(breed_name)
    return breed_name


def write_data(data, name):
    file_name = name
    if os.path.exists(name):
        os.remove(name)
    with open(file_name, 'a', errors='ignore', newline='') as f:
        f_csv = csv.writer(f)
        f_csv.writerows(data)


if __name__ == '__main__':
    header = {
        'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
    }
    timeout = random.choice(range(80, 180))

    file_path = 'url.txt'

    final = []
    with open(file_path, 'r') as file:
        file_lines = file.readlines()

    for url in file_lines:
        response = requests.get(url, headers=header, timeout=timeout)
        soup = BeautifulSoup(response.content, 'html.parser')

        temp = []

        breed_name = soup.find('meta', attrs={'name': 'og:breed'}).get('content')
        temp.append(breed_name)

        html_entity = soup.find('div', attrs={'data-js-component': 'breedPage'}).get('data-js-props')
        print(html_entity)
        decoded_text = html.unescape(html_entity)
        try:
            data = json.loads(decoded_text)
        except json.JSONDecodeError as e:
            temp.append(url)
            final.append(temp)
            print("JSON 解析错误地址:", url)
            print("JSON 解析错误:", str(e))
            continue
        current_breed = data['settings']['current_breed']
        coat_type = data['settings']['breed_data']['traits'][current_breed]['traits']['coat_type']['selected']
        for select in coat_type:
            temp.append(select)
        coat_length = data['settings']['breed_data']['traits'][current_breed]['traits']['coat_length']['selected']
        for select in coat_length:
            temp.append(select)
        final.append(temp)

    write_data(final, 'breed_to_coat.csv')
