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
            title = topics["title"]
            views = topic["views"]
            
            post_url = base_post_url + data["topic_list"]["topics"][i]["slug"]
            post_res = requests.get(post_url)
            soup = BeautifulSoup(post_res.text, 'html.parser')
            for post in soup.find_all('div',attrs={'class':'post'}):
                post_text = post.p.text

    except KeyError:
        if timeout_counter >= 3:
            print("Scripts stopped at page " + str(page))
            break
        else:
            print("wait for 1 min to try again")
            time.sleep(60)
            timeout_counter = timeout_counter + 1
