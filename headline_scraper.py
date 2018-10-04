import re
import glob
import newspaper
import nltk
import threading

local_path = 'C:/Users/Daniel/Desktop/Hate/'

def get_tweet_urls():
    file_path = "C:/Users/Daniel/Documents/NLP Research/"
    URLlist = []
    for infile_name in [x for x in glob.glob(file_path + '*.tsv')]:
        with open(infile_name, mode='r',encoding="utf-8",errors="replace") as infile:
            for line in infile:
                    line_fields = line.split("\t")
                    if len(line_fields) > 13:
                        tweet = line_fields[13]
                    else:
                        tweet = ''
                    urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', tweet)
                    if urls and (urls[0] not in URLlist ):
                        URLlist += urls

    return URLlist

def get_headlines(URLlist,id):
    file_name = local_path +'headlines/' + 'headline'+ id + '.csv'
    titles = []
    for url in URLlist:
        article = newspaper.Article(url,language='en')
        article.download()
        try:
            article.parse()
            article.nlp()
            titles.append(article.title)
            with open(file_name, mode='r', encoding="utf-8", errors="replace") as file:
                file.write(article.title)
            print(article.title)
        except UnicodeError:
            pass
        except Exception:
            pass
    return titles

def split_file_list(file_list, num_lists):
    length = len(file_list)
    itemsPerList = int(length /(num_lists - 1))
    return [file_list[i:i + itemsPerList] for i in range(0, length, itemsPerList)]

def deploy_threads(numberThreads):
    thread_list = [0] * numberThreads

    tweets = get_tweet_urls()
    lists = split_file_list(tweets, numberThreads)
    #initialize threads
    for i in range(numberThreads):
        thread_list[i] = threading.Thread(target=get_headlines(), args= (lists[i],i))

    #start threads
    for i in range(numberThreads):
        thread_list[i].start()
    #join threads
    for i in range(numberThreads):
        thread_list[i].join()

