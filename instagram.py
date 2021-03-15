import json
import time
import requests
import threading
from utils import (
    net_to_cookie, dict_cookies_to_str,
    get_random_proxy, get_proxies_from_file,
    connection, err)


class InstagramSoftware:
    lock = threading.Lock()
    
    def get_info(self, link, cookie=None):
        url = link + '?__a=1'
        r = connection(obj=requests.get, url=url, proxies=proxies, 
                       proxy_type=proxy_type, cookies=cookie)
        if not r:
            return
        return r.json()


class InstagramCreate:
    def __init__(self, cookie):
        self.cookie = cookie

    def post_image(self, path_to_image, upload_link):
        upload_id = int(time.time() * 1000)
        upload_name = f"{upload_link}_{upload_id}"
        photo_data = open(path_to_image, "rb").read()
        photo_len = str(len(photo_data))
        rupload_params = {
            "media_type": "1",
            "upload_id": upload_id,
            "upload_media_height": "1080",
            "upload_media_width": "1080"
        }
        headers = {
            "Accept-Encoding": "gzip",
            "X-Instagram-Rupload-Params":
            json.dumps(rupload_params),
            "X-Entity-Type": "image/jpeg",
            "Offset": "0",
            "X-Entity-Name": upload_name,
            "X-Entity-Length": photo_len,
            "Content-Length": photo_len,
            "Accept-Encoding": "gzip",
        }
        url = f"https://www.instagram.com/rupload_igphoto/{upload_name}"
        r = connection(obj=requests.post, url=url, proxies=proxies,
                       proxy_type=proxy_type, data=photo_data,
                       cookies=self.cookie, headers=headers)
        if not r:
            return
        response_data = r.json()
        return response_data['upload_id']

    def create_post_(self, upload_id, caption):
        data = {
            "upload_id": upload_id,
            "caption": caption,
            "usertags": "",
            "custom_accessibility_caption": "",
            "retry_timeout": ""
        }
        headers = {
            'x-csrftoken': self.cookie['csrftoken'],
            'cookie': dict_cookies_to_str(self.cookie)
        }
        url = 'https://www.instagram.com/create/configure/'
        r = connection(obj=requests.post, url=url, proxies=proxies, 
                       proxy_type=proxy_type, cookies=self.cookie, 
                       data=data, headers=headers)
        if not r:
            return
        response_data = r.json()
        return response_data['status']
    
    def create_direct_img(self, upload_id, thread_id):
        mutation_id = int(time.time() * 1000)
        data = {
            'action': 'send_item',
            'allow_full_aspect_ratio': '1',
            'content_type': 'photo',
            'mutation_token': f'677543{mutation_id}',
            'sampled': '1',
            'thread_id': thread_id,
            'upload_id': upload_id
        }
        headers = {
            'x-ig-app-id': '936619743392459',
            'x-csrftoken': cookie['csrftoken'],
            'cookie': dict_cookies_to_str(self.cookie)
        }
        url = 'https://i.instagram.com/api/v1/direct_v2/threads/' \
            'broadcast/configure_photo/'
        r = connection(obj=requests.post, url=url, proxies=proxies, 
                       proxy_type=proxy_type, cookies=self.cookie, 
                       data=data, headers=headers)
        if not r:
            return
        response_data = r.json()
        return response_data['status']


class InstagramCookie(InstagramSoftware):
    def __init__(self):
        self.posts_created = 0
        self.privacy_changed = 0
        self.disabled_notifications = 0
        self.direct_img_created = 0
    
    def create_post(self, cookie, path_to_image, caption):
        inst_create_post = InstagramCreate(cookie=cookie)
        upload_id = inst_create_post.post_image(
            path_to_image=path_to_image,
            upload_link='fb_uploader')
        if not upload_id:
            return
        status_code = inst_create_post.create_post_(upload_id, caption)
        if not status_code:
            return
        if status_code == 'ok':
            with self.lock:
                self.posts_created += 1
            print('Post created.')
    
    def change_account_privacy(self, cookie, privacy_status):
        url = 'https://www.instagram.com/accounts/set_private/'
        headers = {'x-csrftoken': cookie['csrftoken']}
        data = {'is_private': privacy_status}
        r = connection(obj=requests.post, url=url,
                       proxies=proxies, proxy_type=proxy_type,
                       cookies=cookie, headers=headers,
                       data=data)
        if not r:
            return
        response_data = r.json()
        if response_data['status'] == 'ok':
            with self.lock:
                self.privacy_changed += 1
            print('Privacy changed.')
    
    def account_info(self, cookie):
        url = 'https://www.instagram.com/accounts/edit/'
        r = connection(obj=requests.get, url=url,
                       proxies=proxies, proxy_type=proxy_type,
                       cookies=cookie)
        if not r:
            return
        user_data = self.get_info(url, cookie=cookie)
        del user_data['form_data']['profile_edit_params']
        return user_data['form_data']
    
    def turn_off_push_notifications(self, cookie):
        url = 'https://www.instagram.com/push/web/update_settings/'
        headers = {'x-csrftoken': cookie['csrftoken']}
        data = {
            'likes': '1',
            'comments': '1',
            'comment_likes': '1',
            'like_and_comment_on_photo_user_tagged': '1',
            'follow_request_accepted': '1',
            'pending_direct_share': '1',
            'direct_share_activity': '1',
            'notification_reminders': '1',
            'first_post': '1',
            'view_count': '1',
            'report_updated': '1',
            'live_broadcast': '1'
        }
        r = connection(obj=requests.post, url=url, proxies=proxies,
                        proxy_type=proxy_type, cookies=cookie, 
                        headers=headers, data=data)
        if not r:
            return
        response_data = r.json()
        if response_data['status'] == 'ok':
            with self.lock:
                self.disabled_notifications += 1
            print('Notifications are disabled.')
    
    def get_direct_threads(self, cookie):
        headers = {'x-ig-app-id': '936619743392459'}
        url = 'https://i.instagram.com/api/v1/direct_v2/inbox/?persist' \
            'entBadging=true&folder=&limit=10&thread_message_limit=1000'
        r = connection(obj=requests.get, url=url, proxies=proxies,
                       proxy_type=proxy_type, headers=headers,
                       cookies=cookie)
        if not r:
            return
        response_data = r.json()
        direct_threads = response_data['inbox']['threads']
        thread_ids = [thread['thread_id'] for thread in direct_threads]
        return thread_ids
    
    def direct_img(self, cookie, path_to_image):
        thread_ids = self.get_direct_threads(cookie)
        if not thread_ids:
            return
        for thread_id in thread_ids:
            inst_create_post = InstagramCreate(cookie=cookie)
            upload_id = inst_create_post.post_image(
                path_to_image=path_to_image,
                upload_link='direct')
            if not upload_id:
                return
            status_code = inst_create_post.create_direct_img(
                upload_id=upload_id,
                thread_id=thread_id)
            if not status_code:
                return
            if status_code == 'ok':
                with self.lock:
                    self.direct_img_created += 1
                print('Image to direct sent.')


class InstagramPost(InstagramSoftware):
    def __init__(self, post_url):
        self.post_info = self.get_info(post_url)
        self.post_id = self.post_info['graphql']['shortcode_media']['id']
        self.posts_liked = 0
        self.posts_commented = 0
        self.comments_liked = 0
    
    def send_like(self, cookie):
        url = f'https://www.instagram.com/web/likes/{self.post_id}/like/'
        headers = {'X-CSRFToken': cookie['csrftoken']}
        r = connection(obj=requests.post, url=url, proxies=proxies,
                       proxy_type=proxy_type, cookies=cookie,
                       headers=headers)
        if not r:
            return
        response_data = r.json()
        if response_data['status'] == 'ok':
            with self.lock:
                self.posts_liked += 1
            print('Like sent.')
    
    def send_comment(self, cookie, text):
        url = f'https://www.instagram.com/web/comments/{self.post_id}/add/'
        headers = {'x-csrftoken': cookie['csrftoken']}
        data = {
            'comment_text': text,
            'replied_to_comment_id': ''
        }
        r = connection(obj=requests.post, url=url, proxies=proxies,
                       proxy_type=proxy_type, cookies=cookie,
                       headers=headers, data=data)
        if not r:
            return
        response_data = r.json()
        if response_data['status'] == 'ok':
            with self.lock:
                self.posts_commented += 1
            print('Comment sent.')
            
    def get_comment_id(self, usertext):
        comments = self.post_info['graphql']['shortcode_media'] \
            ['edge_media_preview_comment']['edges']
        filtered_comments = [comment['node']['id'] for comment in comments 
                             if comment['node']['text'] == usertext]
        if not filtered_comments:
            return
        return filtered_comments[0]
            
    def send_like_to_comment(self, cookie, usertext):
        comment_id = self.get_comment_id(username, usertext)
        print(comment_id)
        if not comment_id:
            return
        url = f'https://www.instagram.com/web/comments/like/{comment_id}/'
        headers = {'x-csrftoken': cookie['csrftoken']}
        r = connection(obj=requests.post, url=url, proxies=proxies,
                       proxy_type=proxy_type, cookies=cookie,
                       headers=headers)
        if not r:
            return
        response_data = r.json()
        if response_data['status'] == 'ok':
            with self.lock:
                self.comments_liked += 1
            print('Like to comment sent.')


class InstagramProfile(InstagramSoftware):
    def __init__(self, profile_url):
        user_info = self.get_info(profile_url)
        self.user_id = user_info['graphql']['user']['id']
        self.followed = 0
    
    def follow(self, cookie):
        headers = {
            'x-instagram-ajax': '894dd5337020',
            'x-csrftoken': cookie['csrftoken']
        }
        url = f"https://www.instagram.com/web/friendships/{self.user_id}/follow/"
        r = connection(obj=requests.post, url=url,
                       proxies=proxies, proxy_type=proxy_type,
                       cookies=cookie, headers=headers)
        if not r:
            return
        response_data = r.json()
        if response_data['status'] == 'ok':
            with self.lock:
                self.followed += 1
            print('Subscribed.')


if __name__ == '__main__':
    # PROXY
    file_with_proxies = 'proxies.txt'
    proxies = get_proxies_from_file(file_name=file_with_proxies)
    proxy_type = 'http'
    
    # COOKIES
    cookie = net_to_cookie('cookie.txt', 'instagram')
    
    # -- LIKE COMMENT CREATE_POST SEND_LIKE_TO_COMMENT --
    # post_url = 'https://www.instagram.com/p/BkhB0xCAVuO/'
    # instagram_post = InstagramPost(post_url=post_url)
    # instagram_post.send_like(cookie=cookie)
    # instagram_post.send_comment(cookie=cookie, text='holop let me get a story')
    # instagram_post.create_post(cookie=cookie, path_to_image='img.jpg', caption='levi shmevi')
    # instagram_post.send_like_to_comment(cookie, usertext='321')
    
    # -- FOLLOW --
    # profile_url = 'https://www.instagram.com/ggbic123'
    # instagram_profile = InstagramProfile(profile_url=profile_url)
    # instagram_profile.follow(cookie=cookie)
    
    # -- CHANGE_PRIVACY TURN_OFF_PUSH_NOTIFICATIONS DIRECT_IMAGE --
    instagram_cookie = InstagramCookie()
    # instagram_cookie.change_account_privacy(cookie=cookie, privacy_status='false')
    # instagram_cookie.turn_off_push_notifications(cookie=cookie)
    instagram_cookie.direct_img(cookie=cookie, path_to_image='img.jpg')
