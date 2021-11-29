import praw
import random
import datetime
import time

posted_to =[]

madlibs = [
    "Bernie Sanders wants to tax the [wealthy], and cares [deeply] about [important] [issues] like [climate change]. Bernie [supports] making [colleges] tuition free to ensure [everyone] has access to education.",
    "In Congress, Bernie has fought [tirelessly] for working [families], focusing on the [shrinking] middle class and [growing] gap between the [rich] and everyone else. The [elite] have run [this country] for long enough and Bernie [supports] the issues of the working class.",
    "As mayor, Bernie�s [leadership] helped [transform] Burlington into one of the most [exciting] and [livable] small cities in [America]. Under his administration, the city made [major] strides in affordable housing, progressive taxation, environmental protection, child care, women�s rights, youth programs and the arts.",
    "Even though [this country] is already run by [old] white [guys] like Bernie, he supports the [voices] of minorities and women like [AOC]. AOC is a [congresswoman] from New York.",
    "Bernie considers [climate change] the most [important] change to national security. He opposed the [construction] of the Dakota Access Pipeline on the grounds that it will have a [significant] [impact] on the climate.",
    "Sanders focuses on a [variety] of economic [issues]. Some of these include income and wealth inequality, poverty, raising the minimum wage, [universal healthcare], [cancelling] all student debt, making public colleges and universities tuition-free by taxing financial transactions, and [expanding] Social Security benefits."
    ]

replacements = {
    'wealthy' : ['rich', 'elite', '1%','billionaires', 'millionaires'],
    'deeply' : ['passionately', 'a lot', 'very much'],
    'important' : ['valuable', 'timely', 'essential'],
    'issues' : ['causes', 'platforms', 'agendas'],
    'climate change' : ['global warming', 'climate crisis'],
    'colleges' : ['universities', 'higher education', 'education', 'academia'],
    'everyone' : ['Americans', "all people", "citizens", 'people'],
    'tirelessly' : ['relentlessly', 'hard', 'passionately', 'with determination'],
    'families' : ['people', 'Americans', 'classes'],
    'shrinking' : ['declining', 'decreasing', 'minimized', 'dwindling'],
    'growing' : ['increasing', 'expanding', 'heightening', 'enlarging', 'spreading'],
    'rich' : ['wealthy', 'elite', '1%','billionaires', 'millionaires'],
    'elite' : ['wealthy', 'rich', '1%','billionaires', 'millionaires'],
    'this country' : ['the USA', 'America', 'the United States', 'our country'],
    'supports' : ['advocates for', 'encourages', 'fights for', 'champions', 'is a supporter of'],
    'leadership' : ['guidance', 'direction', 'management', 'influence'],
    'transform' : ['change', 'shift', 'reshape', 'reconstruct', 'remodel'],
    'exciting' : ['impressive', 'beautiful', 'great'],
    'livable' : ['organized', 'cozy', 'comfortable'],
    'major' : ['impressive', 'big', 'notable', 'significant'],
    'old' : ['elderly', 'aged', 'boring', 'ancient'],
    'guys' : ['men', 'dudes', 'politicians'],
    'voices' : ['issues', 'opinions', 'causes'],
    'AOC' : ['Alexandria Ocasio-Cortez', 'Congresswoman AOC', 'representative AOC'],
    'congresswoman' : ['politician', 'representative'],
    'construction' : ['building', 'establishment', 'manufacturing'],
    'significant' : ['drastic', 'notable', 'noteworthy', 'huge', 'big'],
    'impact' : ['effect', 'result', 'influence'],
    'variety' : ['plethora', 'a lot', 'a diverse range'],
    'universal healthcare' : ['healthcare for all', 'affordable healthcare', 'free healthcare'],
    'cancelling' : ['negating', 'forgiving', 'wiping out'],
    'expanding' : ['increasing', 'growing', 'heightening', 'enlarging'],
    'America' : ['the US', 'the United States', 'the USA']
    }

#select a 'BotTown' submission randomly from the 10 hottest submissions
def get_random_submission(reddit) :
    submissions = reddit.subreddit('BotTown2').hot(limit=25)

    #I am choosing to skip 'Main Discussion Thread' and anything else I want later
    my_favourite_top_submissions = []
    for sub in list(submissions):
        if(sub.title not in ["Main Discussion Thread", "Dammit! Not you as well Mick"]):
            my_favourite_top_submissions.append(sub)
    return random.choice(my_favourite_top_submissions)

def generate_comment():
    '''
    This function generates random comments according to the patterns specified in the `madlibs` variable.

    To implement this function, you should:
    1. Randomly select a string from the madlibs list.
    2. For each word contained in square brackets `[]`:
        Replace that word with a randomly selected word from the corresponding entry in the `replacements` dictionary.
    3. Return the resulting string.

    For example, if we randomly seleected the madlib "I [LOVE] [PYTHON]",
    then the function might return "I like Python" or "I adore Programming".
    Notice that the word "Programming" is incorrectly capitalized in the second sentence.
    You do not have to worry about making the output grammatically correct inside this function.
    '''
    #1. Randomly select a string from the madlibs list.
    madlib_str = random.choice(madlibs)
    
    #2. For each word contained in square brackets `[]`:
    #    Replace that word with a randomly selected word from the corresponding entry in the `replacements` dictionary.
    for k in replacements.keys():
        madlib_str = madlib_str.replace('['+k+']',random.choice(replacements[k]))

    #3. Return the resulting string
    return(madlib_str)


def get_comment_text_with_sig():
    comment=generate_comment()
    sig="\n___\nBernie Bot -" + current_username
    return (comment + sig)

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

def post_comment(submission):
    comment_text=get_comment_text_with_sig()
    try:
        # When we get the comments from a submission and flatten it out we 
        # are dealing with a static list that doesn't have infor about
        # the comments we just made. I am keeping a local history of this
        # to filter further
        if submission.id in posted_to:
            print("We have already posted to this parent. Skipping ", submission.id)
        else:
            submission.reply(comment_text)
            posted_to.append(submission.id)
            print("Posting to :" , submission.id)
    except praw.exceptions.RedditAPIException  as e:
        if e.items[0].error_type == 'RATELIMIT':
            print(
                'Ratelimit - artificially limited by Reddit.'
                'Sleeping for requested time!'
            )
            handle_rate_limit(e)
        else:
          print("something else went wrong: ", e.message)

# connect to reddit 
reddit = praw.Reddit("Bernie_Bot_00")
current_username = reddit.user.me().name

# select a "home" submission in the /r/BotTown subreddit to post to,
# and put the url below
#submission_url = 'https://www.reddit.com/r/BotTown/comments/qx3ryd/goodoldnerdbot_home_submission/'
#submission_url = 'https://www.reddit.com/r/BotTown/comments/r0pana/male_inmate_sexually_assaulted_female_in/'
#submission = reddit.submission(url=submission_url)

# pick a random submission to the "home" submission
submission = get_random_submission(reddit)

# (Optional task Number 6) : Instead of having your bot reply randomly to posts, 
# make your bot reply to the most highly upvoted comment
submission.comment_sort = 'best'

# each iteration of this loop will post a single comment;
# since this loop runs forever, your bot will continue posting comments forever;
# (this is what makes it a deamon);
# recall that you can press CTRL-C in the terminal to stop your bot
#
# HINT:
# while you are writing and debugging your code, 
# you probably don't want it to run in an infinite loop;
# you can change this while loop to an if statement to make the code run only once
while True:

    # printing the current time will help make the output messages more informative
    # since things on reddit vary with time
    print()
    print('new iteration at:',datetime.datetime.now())
    print('submission.title=',submission.title)
    print('submission.url=',submission.url)

    # (task 0): get a list of all of the comments in the submission
    # HINT: this requires using the .list() and the .replace_more() functions  
    # Flatten the comment tree  
    submission.comments.replace_more(limit=None)
    all_comments = submission.comments.list()

    # Remove all the deleted comments from circulation 
    # Asking for permission rather than asing for forgiveness
    all_non_deleted_comments = []
    for comment in all_comments:
        if ( comment.body is None and comment.author is None) or comment.body in ("[deleted]", "[removed]"):
            continue
        else: 
            all_non_deleted_comments.append(comment)


    # HINT: 
    # we need to make sure that our code is working correctly,
    # and you should not move on from one task to the next until you are 100% sure that 
    # the previous task is working;
    # in general, the way to check if a task is working is to print out information 
    # about the results of that task, 
    # and manually inspect that information to ensure it is correct; 
    # in this specific case, you should check the length of the all_comments variable,
    # and manually ensure that the printed length is the same as the length displayed on reddit;
    # if it's not, then there are some comments that you are not correctly identifying,
    # and you need to figure out which comments those are and how to include them.
    print('len(all_comments)=',len(all_comments))
    print('len(all_non_deleted_comments)=',len(all_non_deleted_comments))

    # (task 1): filter all_comments to remove comments that were generated by your bot
    # HINT: 
    # use a for loop to loop over each comment in all_comments,
    # and an if statement to check whether the comment is authored by you or not
    not_my_comments = []
    for comment in all_non_deleted_comments:  
        if comment.author.name != current_username:
            not_my_comments.append(comment)

    # HINT:
    # checking if this code is working is a bit more complicated than in the previous tasks;
    # reddit does not directly provide the number of comments in a submission
    # that were not gerenated by your bot,
    # but you can still check this number manually by subtracting the number
    # of comments you know you've posted from the number above;
    # you can use comments that you post manually while logged into your bot to know 
    # how many comments there should be. 
    print('len(not_my_comments)=',len(not_my_comments))

    # if the length of your all_comments and not_my_comments lists are the same,
    # then that means you have not posted any comments in the current submission;
    # (your bot may have posted comments in other submissions);
    # your bot will behave differently depending on whether it's posted a comment or not
    has_not_commented = len(not_my_comments) == len(all_non_deleted_comments)
    print("has_not_commented=", has_not_commented)

    if has_not_commented:
        # (task 2)
        # if you have not made any comment in the thread, then post a top level comment
        #
        # HINT:
        # use the generate_comment() function to create the text,
        # and the .reply() function to post it to reddit;
        # a top level comment is created when you reply to a post instead of a message
        print("Posting to - has not commented")
        post_comment(submission)
    else:
        # (task 3): filter the not_my_comments list to also remove comments that 
        # you've already replied to
        # HINT:
        # there are many ways to accomplish this, but my solution uses two nested for loops
        # the outer for loop loops over not_my_comments,
        # and the inner for loop loops over all the replies of the current comment from the outer loop,
        # and then an if statement checks whether the comment is authored by you or not
        comments_without_replies = []
       
        for comment in not_my_comments:
            replies = comment.replies
            reply_author_list =[]

            #get the top level replies and see if I have replied
            for reply in replies:
                reply_author_list.append(str(reply.author))
            
            if current_username in reply_author_list:
                continue
            
            comments_without_replies.append(comment)

        # HINT:
        # this is the most difficult of the tasks,
        # and so you will have to be careful to check that this code is in fact working correctly
        print('len(comments_without_replies)=',len(comments_without_replies))

        # (task 4): randomly select a comment from the comments_without_replies list,
        # and reply to that comment
        #
        # HINT:
        # use the generate_comment() function to create the text,
        # and the .reply() function to post it to reddit;
        # these will not be top-level comments;
        # so they will not be replies to a post but replies to a message
        if len(comments_without_replies) > 0 :
            comment = random.choice(comments_without_replies)
            print("posting to - comment without replies")
            post_comment(comment)

    # (task 5): select a new submission for the next iteration;
    # your newly selected submission should be randomly selected from the 5 hottest submissions
    submission = get_random_submission(reddit)
    #print("New submission url = ", submission.url)

    # We sleep just for 1 second at the end of the while loop.
    # This doesn't avoid rate limiting
    # (since we're not sleeping for a long period of time),
    # but it does make the program's output more readable.
    time.sleep(1)
