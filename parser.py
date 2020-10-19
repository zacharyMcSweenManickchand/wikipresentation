import mwparserfromhell
import requests, re, json
import tools

class wikiArticle:
    def __init__(self, wikiTitle):
        self.wikiTitle = wikiTitle
        self.Image = ""
        self.Content = []
        self.Infobox = {}
        self.getImage()
        self.getContent()
        self.wiki()

    def getImage(self):
        url = "https://en.wikipedia.org/w/api.php?"
        params = {
            "action" : "query",
            "titles" : self.wikiTitle,
            "prop" : "pageimages",
            "format" : "json",
            "pithumbsize":"100" 
        }
        data = requests.get(url,params=params).json()
        pages = data["query"]["pages"]
        pageid = list(pages.keys())[0]
        #print(pageid)
        thumb = str(pages[pageid]["thumbnail"]["source"])
        imageUrl = thumb.replace("/thumb", '')
        #returns real image
        self.Image = imageUrl[:imageUrl.rindex("/")]

    def getContent(self):
        url = "https://wikipedia.org/w/api.php?"

        params = {
        "action" : "query",
        "prop" : "extracts",
        "exlimit": "1",
        "explaintext": "1",
        "formatversion": "2",
        "language" : "en",
        "format" : "json",
        "titles" : self.wikiTitle
        }

        data = requests.get(url,params=params).json()
        pages = data["query"]["pages"][0]
        contentList = re.split(r'=+\s\w+\s=+|=+\s\w+\s\w+\s=+|=+\s\w+\s\w+\s\w+\s=+|=+\s\w+\s\w+\s\w+\s\w+\s=+|=+\s\w+\s\w+\s\w+\s\w+\s\w+\s=+|=+\s\w+\s\w+\s\w+\s\w+\s\w+\s\w+\s=+', str(pages["extract"].encode('utf8')))
        #print(contentList)
        
        contentArr = []
        for x in range(len(contentList)):
            normalised = contentList[x].replace("\\n", '').replace("  ", '')
            if normalised != "":
                contentArr.append(tools.sumerize(normalised))

        #for i in contentArr:
            #print(i + "\n")
        self.Content = contentArr



    def wiki(self):
        url = "https://wikipedia.org/w/api.php?"
        params = {
        "action" : "query",
        "prop" : "revisions",
        "rvprop" : "content",
        "language" : "en",
        "format" : "json",
        "titles" : self.wikiTitle
        }
        try:
            data = requests.get(url,params=params).json()
            pages = data["query"]["pages"]
            pageid = list(pages.keys())[0]
            #print(pageid)
            page = str(pages[pageid]["revisions"][0]["*"].encode('utf8'))
            #print(page)
            self.Infobox = tools._parseInfobox(page, self.wikiTitle)
        except Exception as e:
            print('Failed to process Page -- Probably means that the wiki page was missing something important')
            print(e)
