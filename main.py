import os
import random

import requests
from dotenv import load_dotenv


def save_image(url, filename):
    response = requests.get(url)
    response.raise_for_status()
    with open(f'{filename}.png', 'ab') as picture:
        picture.write(response.content)


def get_comics_id():
    url = 'https://xkcd.com/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    comics_quantity = response.json()['num']
    comics_id = random.randint(1, comics_quantity)
    return comics_id


def fetch_comics(comics_id):
    url = f'https://xkcd.com/{comics_id}/info.0.json'
    response_picture = requests.get(url)
    response_picture.raise_for_status()
    picture_data = response_picture.json()
    picture_link = picture_data['img']
    save_image(picture_link, 'picture')
    comments = picture_data['alt']
    return comments


def post_image(vk_token, group_id, comments):
    api_url = f'https://api.vk.com/method/photos.getWallUploadServer'
    api_params = {'access_token': vk_token,
                            'v': '5.131'}
    api_response = requests.get(api_url, params=api_params)
    api_response.raise_for_status()
    api_data = api_response.json()

    upload_url = api_data['response']['upload_url']
    with open('picture.png', 'rb') as photo:
        upload_response = requests.post(upload_url, files={'photo': photo})
    upload_data = upload_response.json()
    os.remove('picture.png')

    save_photo_url = f'https://api.vk.com/method/photos.saveWallPhoto'
    params = {'access_token': vk_token,
              'v': '5.131',
            'server': upload_data['server'],
              'photo': upload_data['photo'],
              'hash': upload_data['hash']}
    response = requests.get(save_photo_url, params=params)
    response_data = response.json()
    owner_id = response_data['response'][0]['owner_id']
    id = response_data['response'][0]['id']
    url = f'https://api.vk.com/method/wall.post'
    params = {'access_token': vk_token,
              'v': '5.131',
            'owner_id': -int(group_id),
              'from_group': '1',
              'message': f'{comments}',
              'attachments': f'photo{owner_id}_{id}'}
    requests.post(url, params=params)


if __name__ == '__main__':

    load_dotenv()
    vk_token = os.getenv('VK_TOKEN')
    group_id = os.getenv('GROUP_ID')
    comics_id = get_comics_id()
    comments = fetch_comics(comics_id)
    post_image(vk_token, group_id, comments)
