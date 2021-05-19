from textblob import TextBlob
import tweepy
import matplotlib.pyplot as plt
import pandas as pd
import re
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import plotly.express as px

# Twitter Authentication
twitterAuth = {
   'consumerKey': 'xxxx',
   'consumerSecret': 'xxxx',
   'accessToken':  "xxxx",
   'accessTokenSecret': "xxxx"
}
auth = tweepy.OAuthHandler(twitterAuth['consumerKey'], twitterAuth['consumerSecret'])
auth.set_access_token(twitterAuth['accessToken'], twitterAuth['accessTokenSecret'])
api = tweepy.API(auth)

# Scrap Wikipedia for Contestants names
df = pd.read_html("https://en.wikipedia.org/wiki/The_Bachelor_(American_season_25)")[2]
pd.set_option('display.max_columns', None)
names = ["Bachelorettes"]
df = df.loc[:,names]

# Remove rows with NAN
df.drop(df.tail(2).index,inplace=True);
df.head()

# Rename headers
df.columns = ['contestants']

# Clean up names extracted from Wikipedia
df['contestants'] = df['contestants'].str.strip('[c]').str.strip('.').str.lower()


## Function recieves tweets for a given name passed in and returns attributes for each contestan 
def getTweets(name): 
   
    # Helper function 
    def _getPercentage(part,whole):
        return 100 * float(part)/float(whole)
    
    keyword = 'the bachelor ' + name
    noOfTweet = 50
    
    # Gather tweets
    tweets = tweepy.Cursor(api.search, q=keyword).items(noOfTweet)

    tweetsTotal = [];
    positiveTotal = [];
    negativeTotal = [];
    neutralTotal = [];
    
    posTotal = 0;
    negTotal = 0;
    neuTotal = 0;
        
    for item in tweets:
     tweetsTotal.append(item.text)
     analysis = TextBlob(item.text)
     score = SentimentIntensityAnalyzer().polarity_scores(item.text)
     
     # Scores
     postiveScore = score['pos']
     negativeScore = score['neg']
     neutralScore = score['neu']
     
     if postiveScore > negativeScore:
        positiveTotal.append(item.text)
        
        posTotal += 1
     
     elif negativeScore > postiveScore:
        negativeTotal.append(item.text)
        
        negTotal += 1
     
     elif postiveScore == negativeScore:
        negativeTotal.append(item.text)
        neuTotal += 1
    

    posTotalPercentage = _getPercentage(posTotal, noOfTweet)
    negTotalPercentage = _getPercentage(negTotal, noOfTweet)
    neuTotalPercentage = _getPercentage(neuTotal, noOfTweet)
    
   
        
    maxValue = max(posTotalPercentage,negTotalPercentage,neuTotalPercentage);
    
    if maxValue > 0: 
        # Pie chart visulization
        labels = ['Positive ['+str(posTotalPercentage)+'%]' , 'Neutral ['+str(neuTotalPercentage)+'%]','Negative ['+str(negTotalPercentage)+'%]']
        sizes = [posTotalPercentage, neuTotalPercentage, negTotalPercentage]
        colors = ['pink', 'blue','red']
        patches, texts = plt.pie(sizes,colors=colors, startangle=90, normalize=True)
        plt.legend(labels)
        plt.title("Public Perception of: "+keyword+ "" )
        plt.show()
        
    # Remove duplicate tweets
    tweetsTotal = list(dict.fromkeys(tweetsTotal))

    if maxValue == posTotalPercentage: 
        sentiVal = 'Positive '
        magnitude =  maxValue
        
    elif maxValue == negTotalPercentage:
        sentiVal =  ''
        magnitude =  maxValue
       
    else:
        sentiVal =  0
        magnitude =  maxValue
        
    return posTotalPercentage, neuTotalPercentage, negTotalPercentage, sentiVal, magnitude, len(tweetsTotal)


# Populate the dataframe with results returned from the getTweets function 
df['positive%'], df['neutral%'], df['negative%'], df['sentiment'], df['magnitude'], df['lengthTweets'] = zip(*df.contestants.apply(getTweets))

# Sort df by magnitude 
df = df.sort_values('magnitude', ascending=False)
print(df)
