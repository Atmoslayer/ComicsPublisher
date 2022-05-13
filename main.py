import os
import random

import requests
from dotenv import load_dotenv
from requests.exceptions import HTTPError

from vkexceptions import VkHTTPError


def download_image(url, filename):
    response = requests.get(url)
    response.raise_for_status()
    with open(f'{filename}.png', 'ab') as picture:
        picture.write(response.content)


def get_random_comics_id():
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
    download_image(picture_link, 'picture')
    comments = picture_data['alt']
    return comments


def upload_image(vk_token):
    api_url = 'https://api.vk.com/method/photos.getWallUploadServer'
    api_params = {'access_token': vk_token,
                  'v': '5.131'}
    api_response = requests.get(api_url, params=api_params)
    api_response.raise_for_status()
    api_data = api_response.json()
    raise_for_vk_status(api_data)
    upload_url = api_data['response']['upload_url']
    with open('picture.png', 'rb') as photo:
        upload_response = requests.post(upload_url, files={'photo': photo})
    upload_response.raise_for_status()
    upload_data = upload_response.json()
    return upload_data


def save_image(vk_token, upload_data):

    save_photo_url = 'https://api.vk.com/method/photos.saveWallPhoto'
    params = {'access_token': vk_token, 'v': '5.131',
              'server': upload_data['server'],
              'photo': upload_data['photo'],
              'hash': upload_data['hash']}
    response = requests.get(save_photo_url, params=params)
    response.raise_for_status()
    response_data = response.json()
    raise_for_vk_status(response_data)
    owner_id = response_data['response'][0]['owner_id']
    picture_id = response_data['response'][0]['id']
    return owner_id, picture_id


def post_image(vk_token, group_id, comments, owner_id, picture_id):
    url = 'https://api.vk.com/method/wall.post'
    params = {'access_token': vk_token, 'v': '5.131',
              'owner_id': -int(group_id),
              'from_group': '1',
              'message': comments,
              'attachments': f'photo{owner_id}_{picture_id}'}
    response = requests.post(url, params=params)
    response.raise_for_status()
    raise_for_vk_status(response.json())


def raise_for_vk_status(response_data):
    if 'error' in response_data.keys():
        error = response_data['error']['error_msg']
        raise VkHTTPError(error)


if __name__ == '__main__':

    load_dotenv()
    vk_token = os.getenv('VK_TOKEN')
    group_id = os.getenv('GROUP_ID')
    try:
        comics_id = get_random_comics_id()
        comments = fetch_comics(comics_id)
        upload_data = upload_image(vk_token)
        owner_id, picture_id = save_image(vk_token, upload_data)
        post_image(vk_token, group_id, comments, owner_id, picture_id)

    except (HTTPError, VkHTTPError) as http_error:
        print(f'HTTP error occured: {http_error}')
    finally:
        os.remove('picture.png')
