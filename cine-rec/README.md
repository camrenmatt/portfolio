
# cine-rec
**_cine-rec_ is a movie recommendation platform**, initially designed with a group as _PopcornPix_ in my Software Engineering I class in Fall 2024. After that group dissolved, and a brief time away, I returned to the project as a solo endeavor for my Human Computer Interaction class in Spring 2026 under its new title. Little of the initial design remained, but the principle was the same: create a piece of software to **give people accurate movie recommendations to their taste**.

<p align="center"><img width="800" height="300" alt="logowhite" src="https://github.com/user-attachments/assets/196b3599-6e31-4be1-b837-beb5b69621da" /></p>

# Background
I have always found that streaming services made it incredibly difficult to find a film to watch. They give you an overwhelming quantity of choices, categorize them vaguely, and give you little insight into why they are recommended to you in the first place. **With _cine-rec_, you will be able to select up to four movies that you like, and receive recommendations based on other users who like the same films. These recommendations will then be able to be filtered based on genre, length, release decade, director, or actor.**

After a lengthy period of gathering stakeholder requirements and generating a list of functional requirements, I was met with two major questions:
A: How will I get the data on every movie that exists?
B: How will I generate the recommendations?

The first question of the two has a significantly easier solution than the latter, that being the **TMDB API**. The Movie Database is a user-editable database for all film and TV, and the API gives you access to all data for every movie, including poster, cast and crew, length, genre, etc.

The second question on the other hand, is a tad more complicated. At the onset I knew that I wouldn't be implementing any AI into my algorithm due to the subjectivity of art. I didn't think that any amount of training I could feasibly do myself would equate to the depth that is the taste of each individual. To build an algorithm myself, I would need to get user generated data, and lots of it. This is where I decided to shape my development around the platform **_Letterboxd_**. _Letterboxd_ is a social media platform where users review and rate films, and is an easy place to pull my data from. Luckily for me it also uses The Movie Database for its movie information, so my program and database will be much easier to organize. **The algorithm would be simple: take the user-selected movies, look at users who also loved them, and recommend the most recurring films across all of these users.** _Letterboxd_ also has their own API which would allow me to use all of their data, with the big caveat being that you must apply to have access to this API, and they strictly decline its use for any projects involving movie recommendation, presumably because they aim to build their own service for that purpose. You can, however, download your own personal _Letterboxd_ data and use it for whatever you please.

It is with these two questions that I began my development, as well as my quest to receive as many _Letterboxd_ user logs as possible. Due to the limits of my reach, the recommendations could never get as accurate they would with access to all of _Letterboxd's_ data, but what I scraped together works as a proof of concept.

The entire front-end is designed in **HTML** with plenty of **JavaScript** to handle the animations and interaction with the back-end. The back-end is written in **Python**, and integrates directly with the database I designed in **PostgreSQL**. I have supplied full access to the front-end, and snippets of the back-end, with the database schema also available for view.

# Use/Implementation
Below I will outline the use of the website and all of its features, as well as any specific information worth noting along the way.

## Movie Selection and Search
The website is simple in its use. It opens with a search bar in the center, prompting you to select up to four movies that you like. 

<p align="center"><img width="700" alt="Screenshot 2026-04-21 212827" src="https://github.com/user-attachments/assets/6b94e626-1912-49d5-9077-757b9b2e65de" /></p>

Upon clicking on the bar, four empty poster slots will appear, to be filled by your selections. Just type in a film you love and select it to add it to your search.

<p align="center"><img width="500" alt="image" src="https://github.com/user-attachments/assets/daa181c9-db49-4424-8b5c-2ee2ea22cb84" />
<img width="500" alt="Screenshot 2026-04-21 212920" src="https://github.com/user-attachments/assets/b5ef7762-b890-4cea-90cc-8728475b4019" /></p>

With four films selected:

<p align="center"><img width="500" alt="image" src="https://github.com/user-attachments/assets/cea9ae64-e426-4ed6-b733-376f00a17843" /></p>

From this point, all you need to do is click the search button on the right side of the search bar to receieve your recommendations!

<p align="center"><img width="700" alt="Screenshot 2026-04-21 213022" src="https://github.com/user-attachments/assets/cf57d08c-c3ec-480f-9847-90c78aadf61c" /></p>

## Recommendation Filtering
The initial list of results is purely based on other user's general taste, rather than being restricted to recommendations purely based on specific attributes of the selected films, such as genre. This is to encourage a broader exploration of film, and in turn, a broadening of taste. If you are looking for something a little more specific though, _cine-rec_ has built in filtration options to bring you closer to your desired watch. These include toggle-boxes for genre (which can be mix and matched for further specification, such as a Horror/Comedy), text boxes to specify an actor or director you are looking for, and dropdowns for the decade of release and maximum length (90min, 120min, 150min, 180min). If you are logged into your account, you will also have an option to exclude movied you have already seen, allowing you to receive fresh options.

<p align="center"><img width="700" alt="Screenshot 2026-04-21 213211" src="https://github.com/user-attachments/assets/7cab31cc-10f1-402b-b97a-b327ae32b695" /></p>

## Account Creation/Logging in
If logged out, the top right of the page you will see a toggle-switch to Log-in, or Create an Account.
<p align="center"><img width="250" alt="Screenshot 2026-04-21 213052" src="https://github.com/user-attachments/assets/d1cce0b1-d7d5-4cd5-9a8a-19f0ea8d7456" />
<img width="250" alt="Screenshot 2026-04-21 213120" src="https://github.com/user-attachments/assets/164674b2-5d4e-4a02-bf19-770efd927db3" /></p>

After creating an account or logging in, the top right of your screen will update to reflect this new status, It will also allow you to submit your _Letterboxd_ ratings.csv file to import the films you have already watched. This will enhance the recommendations for other users, and is currently how all data intake is done, and will also allow the user to filter out already seen films as previously mentioned.

<p align="center"><img width="600" alt="Screenshot 2026-04-21 213154" src="https://github.com/user-attachments/assets/26be8bec-5d7c-4e9f-86d9-a3a1dd1607e7" /></p>


