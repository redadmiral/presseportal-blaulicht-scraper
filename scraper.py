import datetime
import os
from bs4 import BeautifulSoup
import requests
from datastructures import Article
import scraperwiki

BASE_URL = "https://www.presseportal.de/text/polizei.htx"
offset = 0
date = datetime.datetime.now()
threshold_date = datetime.datetime.now() - datetime.timedelta(days=2)

while date > datetime.datetime.now() - datetime.timedelta(hours=25):

    print(f"Scraping page {int(offset/30)}.")

    soup = BeautifulSoup(requests.get(BASE_URL + f"?langid=1&start={offset}").text, features="html.parser")
    police_stories = soup.findAll("div", {"class": "storylist_item"})

    for story in police_stories:
        date_raw: str = ":".join(story.contents[0].text.split(":")[:2])
        date = datetime.datetime.strptime(date_raw, "%d.%m.%Y - %H:%M")

        article_link = story.contents[2].a["href"]
        print(f"Retrieving article {article_link}.")
        full_article = BeautifulSoup(
            requests.get(article_link).text, features="html.parser"
        )

        paragraphs = full_article.find(id="story_container").find(id="story").find_all("p")
        id = "pp_" + article_link.split("=")[-1]
        title = full_article.find(id="story").find("div", {"class": "story_title"}).h1.text

        content = []

        for p in paragraphs:
            if "class" not in p:
                content.append(p.text)

        content = " ".join(content)

        location = (
            full_article.find(id="story_logo")
            .find("strong", {"class": "companyname"})
            .text.strip()
        )

        article = Article(
            id=id,
            date=date,
            title=title,
            content=content,
            location=location,
            source=article_link,
        )

        scraperwiki.sqlite.save(unique_keys=["id"], data=article.dict())
    offset += 30


os.rename("scraperwiki.sqlite", "data.sqlite")