import praw
import time
#python3 -m pip install -U textblob
from textblob import TextBlob

# connect to reddit 
reddit = praw.Reddit("Bernie_Up_Down_Vote")
current_username = reddit.user.me().name
submission_up_votes = 0
submission_down_votes = 0
submissions_skipped = 0 
comment_up_votes = 0 
comment_down_votes = 0 
comments_skipped = 0

def handle_rate_limit(exc: praw.exceptions.RedditAPIException) -> None:
    error_words = str(exc).lower().split()
    if 'minutes' in error_words:
        sleepy_time = error_words[error_words.index('minutes')-1]
        print("Sleeping for " + str(sleepy_time) + " minutes")
        time.sleep(60 * float(sleepy_time) + 59)
    elif 'seconds' in error_words:
        sleepy_time = error_words[error_words.index('seconds')-1]
        print("Sleeping for " + str(sleepy_time) + " seconds")
        time.sleep(float(sleepy_time) + 1)

def vote_up_down(submission, text):
    #Check if the text mentions Bernie
    text_word_list = text.lower().split()
    if (not "bernie" in text_word_list)  and (not "sanders" in text_word_list) :
        return(0)

    #Convert to Blob
    blob = TextBlob(text)

    #get sentiment polarity
    polarity = blob.sentiment.polarity

    #Up down vote only if I am not the author
    if submission.author is None:
        return(0)
    if submission.author.name == current_username:
        return(0)

    if polarity > 0 :
        submission.upvote()
        return (+1)           
    elif polarity < 0 :
        submission.downvote()
        return (-1)
    else:
        return(0)
    

#BotTown subreddit
bottown = reddit.subreddit("BotTown2")        

#get existing submissions from bottown
bottown_submissions = bottown.new()
bottown_submission_list = list(bottown_submissions)

#Loop through each submission
for submission in bottown_submission_list:
    try:
        #get the text in submission (title and self text)
        submission_text = submission.title + submission.selftext
        
        #vote the submission up or down
        up_or_down = 0        
        up_or_down = vote_up_down(submission, submission_text)
        if up_or_down > 0:
            submission_up_votes += 1
        elif up_or_down < 0:
            submission_down_votes += 1
        else:
            submissions_skipped += 1

        #Flatten the comment tree
        submission.comments.replace_more(limit=None)
        
        #Get all comments in submission
        all_comments = submission.comments.list()
    except praw.exceptions.RedditAPIException  as e:
        print ("Exception caught when handling a submission ", e.message)
        continue

    #Loop through each comment
    for comment in all_comments:     
        # if this is a deleted comment , skip
        if ( comment.body is None and comment.author is None) or comment.body in ("[deleted]", "[removed]"):
            continue

        #get the text in comment (body)
        comment_text = comment.body

        #vote the comment up or down
        up_or_down = 0        
        up_or_down = vote_up_down(comment, comment_text)
        if up_or_down > 0:
            comment_up_votes += 1
        elif up_or_down < 0: 
            comment_down_votes += 1
        else: 
            comments_skipped += 1

print("Statistics ****")            
print ("submission_up_votes = ", submission_up_votes)
print ("submission_down_votes = ", submission_down_votes)
print ("submissions_skipped = ", submissions_skipped)
print ("comment_up_votes = ", comment_up_votes)
print ("comment_down_votes = ", comment_down_votes)
print ("comments_skipped = ", comments_skipped)
