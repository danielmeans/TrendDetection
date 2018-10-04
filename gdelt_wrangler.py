import requests
import os.path
import urllib.request
import zipfile
import glob
import threading
import time
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd
import numpy
import statsmodels.tsa.api

#import statsmodels.api as sm
import statsmodels.tsa.api

local_path = 'C:/Users/Daniel/Desktop/Hate/'

keyword = 'immigration'

class MyURLopener(urllib.request.FancyURLopener):
  def http_error_default(self, url, fp, errcode, errmsg, headers):
    # handle errors the way you'd like to
    #print("Errorcode: {}, message: {}".format(errcode, errmsg))
    #return 1
    urllib.request.URLopener.http_error_default(self, url, fp, errcode, errmsg, headers)

def generate_file_list():
    gdelt_base_url = 'http://data.gdeltproject.org/gdeltv2/masterfilelist.txt'

    # get the list of all the links on the gdelt file page
    page = requests.get(gdelt_base_url)
    lines = page.text.splitlines()

    # separate out those links that are gkg files
    file_list = [x.split(" ")[-1] for x in lines if 'gkg' in x]
    return file_list

def split_file_list(file_list, num_lists):
    length = len(file_list)
    itemsPerList = int(length /(num_lists - 1))
    return [file_list[i:i + itemsPerList] for i in range(0, length, itemsPerList)]

def scrape_files(file_list, id):
    count = 0
    for compressed_file in file_list:
        print(compressed_file)
        filename = compressed_file.split("/")[-1]
        # if we dont have the compressed file stored locally, go get it. Keep trying if necessary.
        error = 0
        #while not os.path.isfile(local_path + 'tmp/' + filename):
        print('downloading,')
        try:
            MyURLopener().retrieve(url=compressed_file,
                            filename=local_path + 'tmp/' + filename)
            # response = MyURLopener().open(fullurl=compressed_file)
            # with open(local_path + 'tmp/' + filename, 'wb+') as infile:
            #     infile.write(response.read())

        except urllib.error.HTTPError as e:
            print("Errorcode: {}, message: {}".format(e.code, e.msg))
            continue
        time.sleep(10)
        # urllib.request.urlretrieve(url=compressed_file,
        #                    filename=local_path + 'tmp/' +filename)

        # extract the contents of the compressed file to a temporary directory
        print('extracting,')
        z = zipfile.ZipFile(file=local_path + 'tmp/' +filename, mode='r')
        z.extractall(path=local_path + 'tmp/')
        z.close()
        del z
        os.remove(local_path + 'tmp/' +filename)
        # parse each of the csv files in the working directory,
        print('parsing,')
        # for infile_name in [x for x in glob.glob(local_path + 'tmp/*') if 'zip' not in x]:
        infile_name = os.path.splitext(local_path + 'tmp/' +filename)[0]
        outfile_name = local_path + 'export/' + keyword + 'file' +str(id) + '.tsv'

        # open the infile and outfile
        with open(infile_name, mode='r',encoding="utf-8",errors="replace") as infile, open(outfile_name, mode='a+') as outfile:
            for line in infile:
                # extract lines with our interest keyword
                for field in line.split('\t'):
                    if keyword in field.lower():
                        outfile.write(line)
                        continue
                # if keyword in line.split('\t')[23]:
                #     outfile.write(line)
        # delete the temporary file
        try:
            os.remove(infile_name)
        except OSError:
            pass
        print('done')
        count += 1
    print('files read: {}'.format(count))


def deploy_threads(numberThreads):
    thread_list = [0] * numberThreads

    file_list = generate_file_list()
    lists = split_file_list(file_list, numberThreads)
    #initialize threads
    for i in range(numberThreads):
        thread_list[i] = threading.Thread(target=scrape_files, args= (lists[i],i))

    #start threads
    for i in range(numberThreads):
        thread_list[i].start()
        time.sleep(3)
    #join threads
    for i in range(numberThreads):
        thread_list[i].join()

def aggregate_output_files():
    outfile_name = local_path + 'export/' + keyword + 'file.tsv'
    for infile_name in [x for x in glob.glob(local_path + 'export/*')]:
        print(infile_name)
        with open(infile_name, mode='r',encoding="utf-8",errors="replace") as infile,\
                open(outfile_name,encoding="utf-8", mode='a+') as outfile:
            for line in infile:
                outfile.write(line)

def plot_time_series():
    file_name = local_path + 'export/' + keyword + 'file.tsv'
    date_dict = {}
    with open(file_name, mode='r', encoding="utf-8", errors="replace") as file:
        for line in file:
            line_fields = line.split("\t")
            date = line_fields[0][0:8]
            if (int(date) > 20150000):
                dateobj = datetime(year=int(date[0:4]), month=int(date[4:6]), day=int(date[6:8]))
                if dateobj in date_dict.keys():
                    date_dict[dateobj] += 1
                else:
                    date_dict[dateobj] = 1
        dates = []
        counts = []
        for key in sorted(date_dict.keys()):
            dates.append(key)
            counts.append(date_dict[key])
        plt.plot(dates, counts)
        plt.show()
    return date_dict

def get_immigration_articles():
    file_name = "Immigration_Normalized.csv"
    date_dict = {}
    with open(local_path + file_name, mode='r', encoding="utf-8", errors="replace") as infile:
        count = 0
        for line in infile:
            if count > 0:
                line_fields = line.split(",")
                date = line_fields[0][0:8]
                dateobj = datetime(year=int(date[0:4]), month=int(date[4:6]), day=int(date[6:8]))
                line_fields[2] = line_fields[2].strip("\n")
                if dateobj in date_dict.keys():
                    date_dict[dateobj].append(line_fields[1:])
                else:
                    date_dict[dateobj] = [line_fields[1:]]
            count += 1
        immi_dict = {}
        for key in date_dict.keys():
            for value in date_dict[key]:
                    if key in immi_dict.keys():
                        immi_dict[key] += int(value[1])
                    else:
                        immi_dict[key] = int(value[1])

        # for key in date_dict.keys():
        #     for value in date_dict[key]:
        #         if key in immi_dict.keys():
        #             immi_dict[key][0] += int(value[0])
        #             immi_dict[key][1] += int(value[1])
        #         else:
        #             immi_dict[key] = [int(value[0]),int(value[1])]
        # for key in date_dict.keys():
        #     immi_dict[key] = immi_dict[key][1]/ immi_dict[key][0]
        immi_series = pd.Series(immi_dict)
        immi_reindex = reindex_series(immi_series, '2015-01-01', '2017-12-30')
        return immi_reindex

def get_immi_US_articles():
    date_dict = {}
    for infile_name in [x for x in glob.glob(local_path + 'immi_us_trump.csv')]:
        with open(infile_name, mode='r',encoding="utf-8",errors="replace") as infile:
            count = 0
            for line in infile:
                if count > 0:
                    line_fields = line.split(",")
                    date = line_fields[0][0:8]
                    dateobj = datetime(year=int(date[0:4]), month=int(date[4:6]), day=int(date[6:8]))
                    if dateobj in date_dict.keys():
                        date_dict[dateobj] += 1
                    else:
                        date_dict[dateobj] = 1
                count += 1

        immi_series = pd.Series(date_dict)
        immi_reindex = reindex_series(immi_series, '2015-01-01', '2017-12-30')
        return immi_reindex

def reindex_series(series, start, end):
    idx = pd.date_range(start, end)
    series.index = pd.DatetimeIndex(series.index)
    series = series.reindex(idx, fill_value=0)
    return series

def get_immigration_tweets():
    file_path = "C:/Users/Daniel/Documents/NLP Research/"
    date_dict = {}
    for infile_name in [x for x in glob.glob(file_path + '*.tsv')]:
        with open(infile_name, mode='r',encoding="utf-8",errors="replace") as infile:
            count = 0
            for line in infile:
                if count > 0:
                    line_fields = line.split("\t")
                    date = line_fields[0][0:4] + line_fields[0][5:7] + line_fields[0][8:10]
                    if date.isdigit() and (int(date) > 20150000):
                        dateobj = datetime(year=int(date[0:4]), month=int(date[4:6]), day=int(date[6:8]))
                        if dateobj in date_dict.keys():
                            date_dict[dateobj] += 1
                        else:
                            date_dict[dateobj] = 1
                count += 1
        dates = []
        counts = []
        for key in sorted(date_dict.keys()):
            dates.append(key)
            counts.append(date_dict[key])
        tweet_series = pd.Series(date_dict)
        tweet_reindex = reindex_series(tweet_series,'2015-01-01', '2017-12-30')
    return tweet_reindex

def correlate_series(dict1, dict2):
    series1 = pd.Series(dict1)
    series2 = pd.Series(dict2)
    idx = pd.date_range('2015-01-01', '2017-12-01')
    series1.index = pd.DatetimeIndex(series1.index)
    series2.index = pd.DatetimeIndex(series2.index)
    series1 = series1.reindex(idx, fill_value=0)
    series2 = series2.reindex(idx, fill_value=0)
    series1 = series1[idx]
    series2 = series2[idx]
    return series1, series2

def main():
    deploy_threads(32)

if __name__ == "__main__":
    main()