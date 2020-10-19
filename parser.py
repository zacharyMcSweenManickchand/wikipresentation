import mwparserfromhell
import requests, re, json, datetime

from sumerize import sumerize

def _parseDate(wikiDate):
  template = mwparserfromhell.parse("%s"%wikiDate.value)
  d = map(template.filter_templates()[0].get, [1,2,3])
  d = [int('%s'%x.value) for x in d]
  return str(datetime.date(*d))

def getImage(wikiTitle):
  url = "https://en.wikipedia.org/w/api.php?"
  params = {
    "action" : "query",
    "titles" : wikiTitle,
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
  return imageUrl[:imageUrl.rindex("/")]

def getContent(wikiTitle):
  url = "https://wikipedia.org/w/api.php?"

  params = {
  "action" : "query",
  "prop" : "extracts",
  "exlimit": "1",
  "explaintext": "1",
  "formatversion": "2",
  "language" : "en",
  "format" : "json",
  "titles" : wikiTitle
  }

  data = requests.get(url,params=params).json()
  pages = data["query"]["pages"][0]
  contentList = re.split(r'=+\s\w+\s=+|=+\s\w+\s\w+\s=+|=+\s\w+\s\w+\s\w+\s=+|=+\s\w+\s\w+\s\w+\s\w+\s=+|=+\s\w+\s\w+\s\w+\s\w+\s\w+\s=+|=+\s\w+\s\w+\s\w+\s\w+\s\w+\s\w+\s=+', str(pages["extract"].encode('utf8')))
  #print(contentList)
  
  contentArr = []
  for x in range(len(contentList)):
    normalised = contentList[x].replace("\\n", '').replace("  ", '')
    if normalised != "":
      contentArr.append(sumerize(normalised))

  #for i in contentArr:
    #print(i + "\n")
  return contentArr

def _parseInfobox(page, wikiTitle):
  try:
    code = mwparserfromhell.parse(page)
    for template in code.filter_templates():
      if 'Infobox' in template.name:
        # Found the right template -- attempting to extract data
        Infobox = {}
        for i in re.findall(r'\|\s\w+', str(template)):
          key = re.sub(r'\|\s', '', i)
          value = re.sub(r'\|\s|\\n|\s\s', '', str(template.get(key).value))
          Infobox[key] = mwparserfromhell.parse(value)
          #print(Infobox[key])
        for date in ['birth_date','death_date']:
          try:
            item = _parseDate(template.get(date))
          except ValueError as e:
            item = None
          Infobox[date] = item
        
        #Infobox['image'] = getImage(wikiTitle)
        content = getContent(wikiTitle)
        for each in range(len(content)):
            content[each] = content[each].replace("\\n", "")
        Infobox['content'] = content
        # birth = _parseDate(template.get('birth_date'))
        # death = _parseDate(template.get('death_date'))
        # Do it a bit safer by catching missing values
        """
        try: 
          output[i] = mwparserfromhell.parse(template.get(i).value)
        except Exception as e:
          print(e)
        """
        #output['content'] = getContent(page)
        # ok we are done here
        return Infobox
        
    raise ValueError('Missing Infobox')

  except Exception as e:
    print(e)



def wiki(wikiTitle):
  url = "https://wikipedia.org/w/api.php?"
  params = {
  "action" : "query",
  "prop" : "revisions",
  "rvprop" : "content",
  "language" : "en",
  "format" : "json",
  "titles" : wikiTitle
  }
  try:
    data = requests.get(url,params=params).json()
    pages = data["query"]["pages"]
    pageid = list(pages.keys())[0]
    #print(pageid)
    page = str(pages[pageid]["revisions"][0]["*"].encode('utf8'))
    #print(page)
    """
    content = getContent(wikiTitle)
    for each in range(len(content)):
      content[each] = content[each].replace("\\n", "")
    """

    Infobox = _parseInfobox(page, wikiTitle)
    return Infobox
  except Exception as e:
    print('Failed to process Page -- Probably means that the wiki page was missing something important')
    print(e)

Data = wiki("Srinivasa_Ramanujan")
print(Data)
#print(getContent("Srinivasa_Ramanujan"))