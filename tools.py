import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from heapq import nlargest

import mwparserfromhell
import re, datetime

def sumerize(text):
    stopwords = list(STOP_WORDS)
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(text)
    tokens = [token.text for token in doc]
    word_frequencies = {}
    for word in doc:
        if word.text.lower() not in stopwords:
            if word.text.lower() not in punctuation:
                if word.text not in word_frequencies.keys():
                    word_frequencies[word.text] = 1
                else:
                    word_frequencies[word.text] += 1
    #print(word_frequencies)
    max_frequency = max(word_frequencies.values())
    
    #Normalized frequency
    for word in word_frequencies.keys():
        word_frequencies[word] = word_frequencies[word]/max_frequency
        
    sentence_tokens = {sent for sent in doc.sents}
    #print(sentence_tokens)
    sentence_scores = {}
    for sent in sentence_tokens:
        for word in sent:
            if word.text.lower() in word_frequencies.keys():
                if sent not in sentence_scores.keys():
                    if sent not in sentence_scores.keys():
                        sentence_scores[sent] = word_frequencies[word.text.lower()]
                    else:
                        sentence_scores[sent] += word_frequencies[word.text.lower()]
        
    # 30%
    select_length = int(len(sentence_tokens)*0.3)
    summary = nlargest(select_length, sentence_scores, key = sentence_scores.get)
    #print(summary)
    return summary
    #return ' '.join([word.text for word in summary])

def _parseDate(wikiDate):
    template = mwparserfromhell.parse("%s"%wikiDate.value)
    d = map(template.filter_templates()[0].get, [1,2,3])
    d = [int('%s'%x.value) for x in d]
    return str(datetime.date(*d))

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
                return Infobox
            
        raise ValueError('Missing Infobox')

    except Exception as e:
        print(e)