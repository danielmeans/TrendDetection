import requests
import csv
from textblob import TextBlob

def get_articles(topic, startDate, endDate):
    url = ('https://newsapi.org/v2/everything?'
          'q=' + topic + '&'
          'from=' + startDate + '&'
          'to=' + endDate + '&'  
          'sortBy=popularity&'
          'pageSize=100&'
          'page=1&'
          'language=en&'
          'apiKey=aabe6166b8d14dc78ac236c33bf5d377')

    response = requests.get(url)
    print(response.json()["status"])
    total_results = int(response.json()["totalResults"])
    print(total_results)
    numPages = total_results//100 + 1
    articles_list = []


    #to create a loop that aggregates all articles across pages
    for pageNum in range(1,1):
        url = ('https://newsapi.org/v2/everything?'
                 'q=' + topic + '&'
                 'from=' + startDate + '&'
                 'to=' + endDate + '&' 
                 'sortBy=popularity&'
                 'pageSize=100&'
                 'page=' + str(pageNum) + '&'
                 'language=en&'
                 'apiKey=aabe6166b8d14dc78ac236c33bf5d377')
        response = requests.get(url)
        status_code = response.status_code
        if status_code != 200:
            print(response.json()["status"])
            print(response.json()["code"])
            print(response.json()["message"])
            print("HTTP response: %s"%status_code)
            return articles_list
        else:
            for article in response.json()["articles"]:
                articles_list += [article]
    return articles_list

def writeToCsv(row):
       filename = 'articles_immigration.csv'
       with open(filename, 'a+') as csvfile:
              writer = csv.writer(csvfile, delimiter=",")
              writer.writerow(row)

def store_articles(articles_list):
       headers = ["publishedAt", "source", "title", "description", "author","url", "urlToImage"]
       writeToCsv(headers)
       for article in articles_list:
              row = []
              for header in headers:
                     if header == "source":
                            row += [article[header]["name"]]
                     else:
                            row += [article[header]]
              writeToCsv(row)


      # articles_dict = {}
      #  sentiment_dict = {}
# for article in response.json()["articles"]:
#        #get article publish date
#        date = article["publishedAt"][:10]
#
#        # get sentiment of article
#        description = article["description"]
#        analysis = TextBlob(description)
#        sentiment = analysis.sentiment.polarity
#
#        if date not in articles_dict.keys():
#               articles_dict[date] = [article]
#               sentiment_dict[date] = [sentiment]
#        else:
#               articles_dict[date] += [article]
#               sentiment_dict[date] = [sentiment]
#
# print(sentiment_dict.values())
# print(sentiment_dict.keys())

def main():
    store_articles(get_articles("immigration","2018-01-01","2018-01-30"))

if __name__ == "__main__":
    main()
