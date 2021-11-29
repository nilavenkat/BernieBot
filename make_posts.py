import praw
import time


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

num_posts_to_make = 30

# connect to reddit 
reddit = praw.Reddit("Bernie_Bot_Make_Post")
current_username = reddit.user.me().name

#BotTown subreddit
bottown = reddit.subreddit("BotTown2")

#get existing submissions from bottwon so we don't duplicate
bottown_submissions = bottown.new()
bottown_submission_list = []
print("len(bottown_submission_list)", len(bottown_submission_list))
for s in list(bottown_submissions):
    bottown_submission_list.append(s.title)

bernie_subreddits = ["WayOfTheBern","bernieblindness", "bernie", "BernieSanders"]

for bernie_subreddit in bernie_subreddits:
    print ("***Duplicating posts from - /r/",bernie_subreddit) 
    #get submissions from r/bernie/
    submissions = reddit.subreddit(bernie_subreddit).hot()

    submission_list = list(submissions)
    print("len(submission_list) = ", len(submission_list))
    for sub in submission_list:
        author = sub.author
        title = sub.title + " (Originally posted by - " + author.name +")"
        # if this title already exists in bottown, skip
        if title in bottown_submission_list:
            print("Skipping: " , title )
            continue

        selftext = sub.selftext
        url = sub.url
        print()
        print("title = ", title)
        print("selftext = ", selftext)
        print("url = ", url)
        try:
            if selftext == "" and url != "":
                bottown.submit(title=title, url=url)
                print("posting with url")
            elif selftext != "" and url == "":
                bottown.submit(title=title, selftext=selftext)
                print("posting with selftext")
        except praw.exceptions.RedditAPIException  as e:
            if e.items[0].error_type == 'RATELIMIT':
                print(
                    'Ratelimit - artificially limited by Reddit.'
                    'Sleeping for requested time!'
                )
                handle_rate_limit(e)
            else:
                print("something else went wrong: ", e.message)    
