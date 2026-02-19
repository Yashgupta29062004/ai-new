from datetime import datetime,timedelta,timezone
from typing import List,Optional
import feedparser

from pydantic import BaseModel

class OpenAI_Article(BaseModel):
    title:str
    description:str
    url:str
    guid:str
    published_at:datetime
    category:Optional[str]=None

class OpenAI_Scraper :
    def __init__(self):
        self.rss_url="https://openai.com/news/rss.xml"
        
    def get_article(self,hours:int=24)->List[OpenAI_Article]:
        feed=feedparser.parse(self.rss_url)
        if not feed.entries:
            return []
        
        now=datetime.now(timezone.utc)
        cutoff_time=now-timedelta(hours=hours)
        article=[]

        for entry in feed.entries:
            published_parsed=getattr(entry,"published_parsed",None)
            if not published_parsed:
                continue
            published_time=datetime(*published_parsed[:6],tzinfo=timezone.utc)
            if published_time>=cutoff_time:
                article.append(OpenAI_Article(
                    title=entry.get("title"),
                    description=entry.get("description",""),
                    url=entry.get("link",""),
                    guid=entry.get("id",entry.get("link","")),
                    published_at=published_time,
                    category=entry.get("tags",[{}])[0].get("term") if entry.get("tags") else None



                )
    
                )
        return article
if __name__=="__main__":
    scraper=OpenAI_Scraper()
    article:List[OpenAI_Article]=scraper.get_article(hours=50)
    print(f"Total articles found: {len(article)}")