# NZ Winter Olympics System


## routes & functions

| route                     |  method  | function                 | params                   | description                                                                                                                 |
|---------------------------|:--------:|--------------------------|--------------------------|-----------------------------------------------------------------------------------------------------------------------------|
| /                         |   Get    | home_page                |                          | the home page of the public interface                                                                                       |
| /member                   |   Get    | member_page              | name_like                | displays members list, search member, can be clicked for further details                                                    |
| /events                   |   Get    | events_page              | memberid                 | display current members' previous results and upcoming events & stages.                                                     |
| /admin                    |   Get    | admin_page               |                          | Administrator's main interface. displays member count, upcoming events & stages, and includes a search box for easy access. |
| /admin_search             |   Post   | search_page              | search_type, search_data | receiving search data on the admin page and navigating to their respective interfaces.                                      |
| /admin_member             | Get/Post | admin_member_page        | name_like, page          | implement functionality to display, add, delete, modify, and query member information.                                      |
| /admin_delete_member      |   Get    | admin_delete_member      | memberID                 | delete a member record.                                                                                                     |
| /admin_event              | Get/Post | admin_event_page         | event_like, page         | implement functionality to display, add, delete, modify, and query event information.                                       |
| /admin_delete_event       |   Get    | admin_delete_event       | eventID                  | delete a event record.                                                                                                      |
| /admin_event_stage        | Get/Post | admin_event_stage        | stage_like, page         | implement functionality to display, add, delete, modify, and query event stage information.                                 |
| /admin_delete_stage       |   Get    | admin_delete_stage       | stageID                  | delete a event stage record.                                                                                                |
| /admin_team               | Get/Post | admin_team_page          | team_like, page          | implement functionality to display, add, delete, modify, and query team information.                                        |
| /admin_delete_team        |   Get    | admin_delete_team        | teamID                   | delete a team record.                                                                                                       |
| /admin_event_stage_result | Get/Post | admin_event_stage_result | result_like, page        | implement functionality to display, add, delete, modify, and query event stage result information.                          |
| /admin_delete_result      |   Get    | admin_delete_result      | resultID                 | delete a event stage result record.                                                                                         |
| /admin_following_reports  |   Get    | admin_following_reports  |                          | display reports information                                                                                                 |
| error page                |   Get    | handle_error             | error                    | receive all unexpected errors                                                                                               |

---

## Assumptions and design decisions
### 1. Route design

The routes to this site is decided to `/` and `/admin`.  
Public users can visit interfaces start with `/` and Administrator can visit interfaces start with `/admin`.  

### 2. Page design
- The page consists of the following parts. All pages extend from `templates/base.html`

  - nav:
  
    Display different menu bars according to whether it is Administrator
  
  - main：
  
    Display different content for each web page
  
  - footer:
  
    The footer is at the bottom, showing the copyright information.
  
- For this project only need to modify the middle part. 
Create one template for the purpose.


### 3. Function design

- Most of the web pages are returned using the GET method. 
The GET method is used to display the frontend page, 
while the POST method is used to process data updates or additions.

- On pages that use the POST method, it can define the method 
using `@app.route('/page', methods=['GET', 'POST'])`. 
Then, in the function, it can use `request.method` to determine the 
- current request type and use the `request.form.get()` method to retrieve the data from the POST form. 
Finally, perform the necessary database operations.

- This approach can help reduce the number of web pages created and provide clearer code organization. 
However, web pages cannot directly send DELETE requests. Therefore, have to handle it separately from the GET and POST methods

---

## Changes to support multiple Olympic

### 1. Database changes

- Add a new table called `olympics` to store information about the Olympics.

```sql
CREATE TABLE IF NOT EXISTS olympics
(
  OlympicID INT auto_increment PRIMARY KEY NOT NULL,
  OlympicName VARCHAR(80) NOT NULL,
  Year INT NOT NULL,
  City VARCHAR(50) NOT NULL
);
```

- Add a foreign key reference in the `events` table, 
linking the `OlympicID` column to the `olympics` table. 
This association will connect each event to a specific Olympic Games.
```sql
-- add a column
ALTER TABLE `events` ADD OlympicID INT;
-- add a foreign key
ALTER TABLE `events`
ADD FOREIGN KEY (OlympicID) REFERENCES olympics(OlympicID);
```

### 2. Front end changes

- On the `/member` interface, modify the `Events List` to include the Olympic Games to which each item belongs. 
Implement a filtering mechanism based on the Olympic Games.

- On the `/admin_event` interface, add a column for Olympic Games information. 
Modify the content of the `Add Event` button accordingly.


### 3. Backend changes

- Update the SQL query statement in the `member_page()` function to include a filtering function.
- Modify the SQL query, add new statements, and make necessary modifications in the `events_page()` function.


---


## Note：

 - There is a non-team member (Nico Porteous) participating in other team projects in the database, 
 so the event stage result interface in the current project can add any member to participate in any existing project.

 - Under normal circumstances, members of the team only participate in the projects of the team, 
 and it is difficult to generate Upcoming Events & Stages without adding other tables. 
 - To modify the event stage result interface of this project, 
 each member can only participate in the competition of his own team, 
 and have to add condition restrictions on the basis of the current project