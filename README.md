# Herbal List

### App Summary
Ever felt sick but wanted an alternative to Western medicine? Insert Herbal List, an app where users can find herbs to help them with whatever symptoms they are experiencing. Users can search for herbal remedies based on symptoms and can save herbs on their user profile page.


I am creating this app for a round of #100DaysOfCode challenge on twitter.

### User Flow
![User flow](https://github.com/adinahhh/herballist/blob/master/images/herballist_user_flow.png)

### Wireframes
Current wireframes are:
![Homepage](https://github.com/adinahhh/herballist/blob/master/images/wireframes_homepage.png)

![Search results](https://github.com/adinahhh/herballist/blob/master/images/search_results.png)

![Individual herb page](https://github.com/adinahhh/herballist/blob/master/images/individual_herb.png)

![User profile page](https://github.com/adinahhh/herballist/blob/master/images/user_profile_page.png)

### Data Models
-TBD

### Features
#### Login:
- homepage with login, with routes to handle login/logout 
- session to store user info for logged in user
- database query to confirm user as existing user, registration to create new user

#### Herbal search:
- checkboxes for common symptoms, autocomplete search for other symptoms
- search results will show a quick view of information about each herb
    - pagination
    - if an herb is selected, will route user to individual herb page.
    - user can save herb to their profile page, if user is not logged in, will route user to create an account before saving herb.
