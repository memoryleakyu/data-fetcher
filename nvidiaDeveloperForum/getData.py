import requests
import time
import pymongo
from bs4 import BeautifulSoup

# establish connection with local mongoDB
client = pymongo.MongoClient(host="localhost", port=27017)
db = client.seeedPM
collection = db.nvidiaForumPosts

# initialize values like url and pages
base_page_url = "https://forums.developer.nvidia.com/c/agx-autonomous-machines/jetson-embedded-systems/jetson-nano/76/l/latest.json?ascending=false&page="
base_post_url = "https://forums.developer.nvidia.com/t/"
headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36",
    "accept-encoding": "gzip, deflate, br"
}
proxy = {
    "http": "http://127.0.0.1:1087",  # 注意换成自己的代理端口
    "https": "http://127.0.0.1:1087",
}


page = 0
# set timeout counter to handle exceptions like access block from target website
timeout_counter = 1

while True:
    try:
        page_url = base_page_url + str(page)
        page_res = requests.get(page_url, headers=headers, proxies=proxy)
        data = page_res.json()
        topics = data["topic_list"]["topics"]
        for i in range(len(topics)):
            topic = topics[i]
            topic_entry = {}
            topic_entry["title"] = topic["title"]
            topic_entry["views"] = topic["views"]
            topic_entry["created_at"] = topic["created_at"]
            topic_entry["last_posted_at"] = topic["last_posted_at"]
            topic_entry["posts_count"] = topic["posts_count"]
            topic_entry["reply_count"] = topic["reply_count"]
            topic_entry["like_count"] = topic["like_count"]
            topic_entry["has_accepted_answer"] = topic["has_accepted_answer"]
            topic_entry["tags"] = topic["tags"]
            post_url = base_post_url + topic["slug"]
            post_res = requests.get(post_url)
            post_index = 1
            soup = BeautifulSoup(post_res.text, 'html.parser')
            for post in soup.find_all('div',attrs={'class':'post'}):
                post_text = post.find_all('p')
                topic_entry["post%s"%str(post_index)] = {}
                for i in range(len(post_text)):
                    topic_entry["post%s"%str(post_index)]["floor%s"%str(i)] = post_text[i].text
                post_index = post_index + 1


    except KeyError:
        if timeout_counter >= 3:
            print("Scripts stopped at page " + str(page))
            break
        else:
            print("wait for 1 min to try again")
            time.sleep(60)
            timeout_counter = timeout_counter + 1
