The project consists of web application, rest api, bot, parsing
 
## WEB APP (BLOG)
PostgreSQL is used to store data.

The main page contains 2 transitions: authorization and registration.  
The login page contains:
- two login and password fields and a login button;
- button to go to registration page;
- password recovery button.

The password reset page contains an input field - email and a button to send an email.
The letter contains a transition to a page with fields for new password and password confirmation
and a button to change password.

The registration page contains the fields username, email_address, avatar, password, repeat_password
and button create_account.

After successful registration or authorization, you will be redirected to the article page.
A list of articles from all users is displayed. You can view them by clicking on the title of the article.
If this is an article by the current user, then the edit and delete article buttons are available.

The article page in the header contains a profile change button and logout.

There is a button to add an article.
You can see your articles by clicking on  my_articles button.

## DATA PARSING

  In folder blog/web lays script 'parsing.py' for parsing data  from the site https://news.ycombinator.com/.  

Script Tasks:
- Collecting headlines and URLs of news articles.
- Saving this data in a database( using database from blog).   

BeautifulSoup library is using for parsing.  
The script running by using django-crontab.


## REST API for managing articles (protected by token authentication).

| HTTP Method | Endpoints               | Action                                                                                              |
|-------------|-------------------------|-----------------------------------------------------------------------------------------------------|
|             |                         |                                                                                                     |
| POST        | /login                  | Implementing User Login (pass username and password and get token).                                 |
| POST        | /logout                 | Implementing User Logout.                                                                           |
|             |                         |                                                                                                     |
| GET, POST   | articles/               | Show all articles or Create new article.                                                            |
| GET, PUT    | article/<pk>/           | Retrieve(or update) article about indicated id. The user can only edit and delete his own articles. |
|             |                         |                                                                                                     |
| GET         | latest_web_article/     | Retrieve latest article from web application.                                                       |
| GET         | latest_parsing_article/ | Retrieve latest article from parsing table.                                                         |
 

## TELEGRAM BOT

The bot communicates with the Django application API to receive data.  
The bot uses a SQLite database, which stores the telegram_id of all users who connected to the bot and
the identifiers of the latest articles received from the blog and analysis.

#### Interactive features:
Users receives notifications in Telegram (links to articles) when a new article is added.  
New articles are sent to the user from both the blog and parsing_articles.  

#### Bot Commands:

*/start* - welcome message.  
*/help* - list of available commands and their descriptions.  
*/latest* - get the latest article from the blog (web application).   

  ## Quick Start  
#### Clone the repo:  
* $ git clone git@github.com:OlyaNesvitskaya/blog-parsing-bot.git  
* $ cd blog-parsing-bot/  

#### Run the project:

В файл **./bot/.env.dev** необходимо добавить TELEGRAM_TOKEN !!!!!

* docker-compose build
* docker-compose up

Navigate to http://127.0.0.1:8000/web/ to see the main page.  
Navigate to http://127.0.0.1:8000/api/ + endpoint(from table) to access the api.

#### Run tests:
* docker exec -it django /bin/bash
* python manage.py test
