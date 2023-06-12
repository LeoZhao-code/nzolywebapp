from flask import Flask
from flask import url_for
from flask import request
from flask import redirect
from flask import render_template
from datetime import datetime
import mysql.connector
import connect
import math

app = Flask(__name__)
app.config.from_object(connect)

db_conn = None
connection = None


def get_cursor():
    global db_conn
    global connection
    connection = mysql.connector.connect(user=connect.dbuser,
                                         password=connect.dbpass,
                                         host=connect.dbhost,
                                         database=connect.dbname,
                                         autocommit=True)
    db_conn = connection.cursor()
    return db_conn


@app.route('/')
def home_page():
    """
    Index page featuring a navigation bar with links to various sections and a dedicated interface for promoting events.
    :return: index.html
    """
    return render_template("index.html", showid=1, adminflag=1)


@app.route('/member')
def member_page():
    """
    The interface displays a list of members, including their personal information.
    Each member's name can be clicked for further details.
    Additionally, there is a search function that allows for searching all information within the member list.

    Args:
        name_like (str): Get search data.
        member_list (list): A list of all member information.
        event_list (list): A list of all event information.

    :return: member.html
    """
    sql_data = get_cursor()
    name_like = request.args.get('name_like')
    if not name_like:
        sql = """SELECT m.FirstName, m.LastName, t.TeamName, m.City, m.Birthdate, m.MemberID 
                    FROM members AS m
                    INNER JOIN teams AS t ON m.TeamID = t.TeamID;"""
        sql_data.execute(sql)
        member_list = sql_data.fetchall()
    else:
        sql = """SELECT m.FirstName, m.LastName, t.TeamName, m.City, m.Birthdate, m.MemberID 
                    FROM members AS m
                    INNER JOIN teams AS t ON m.TeamID = t.TeamID
                    WHERE CONCAT(m.FirstName, m.LastName, t.TeamName, m.City) LIKE %s;"""
        name_like = "%" + name_like + "%"
        sql_data.execute(sql, (name_like,))
        member_list = sql_data.fetchall()
    sql = """SELECT e.EventID, e.EventName, e.Sport, t.TeamName AS NZTeamName
                    FROM `events` AS e 
                    INNER JOIN teams AS t ON e.NZTeam = t.TeamID;"""
    sql_data.execute(sql)
    event_list = sql_data.fetchall()
    sql_data.close()
    return render_template("member.html", memberlist=member_list, eventlist=event_list, showid=2, adminflag=1)


@app.route('/events')
def events_page():
    """
    Presenting the historical data of current members and providing information about upcoming competitions.

    Args:
        member_id (str): Get search data.
        previous_result (list): A list of previous result information.
        upcoming_event (list): A list of upcoming event information.
        member_name (list) : Current member name.

    :return: events.html
    """
    member_id = request.args.get("memberid")
    if not member_id:
        return redirect(url_for("home_page"))
    sql_data = get_cursor()
    sql = """SELECT esr.ResultID, m.MemberID, e.EventName, es.StageDate, es.StageName, es.Location, esr.Position 
                FROM event_stage_results AS esr
                INNER JOIN event_stage AS es ON esr.StageID = es.StageID
                INNER JOIN members AS m ON esr.MemberID = m.MemberID
                INNER JOIN events AS e ON e.EventID = es.EventID 
                WHERE esr.MemberID = %s 
                ORDER BY e.EventName;"""
    sql_data.execute(sql, (member_id,))
    previous_result = sql_data.fetchall()
    # Format the data
    if previous_result:
        previous_result = [list(item) for item in previous_result]
        temp = previous_result[0][2]
        for i in range(1, len(previous_result)):
            if previous_result[i][2] == temp:
                previous_result[i][2] = ''
            else:
                temp = previous_result[i][2]
    sql = """SELECT m.MemberID, e.EventName, es.StageName, es.Location, es.StageDate
                FROM members m
                JOIN events e ON m.TeamID = e.NZTeam
                JOIN event_stage es ON e.EventID = es.EventID
                LEFT JOIN event_stage_results esr ON m.MemberID = esr.MemberID AND es.StageID = esr.StageID
                WHERE esr.MemberID IS NULL AND m.MemberID = %s 
                ORDER BY e.EventName;"""
    sql_data.execute(sql, (member_id,))
    upcoming_event = sql_data.fetchall()
    # Format the data
    if upcoming_event:
        upcoming_event = [list(item) for item in upcoming_event]
        temp = upcoming_event[0][1]
        for i in range(1, len(upcoming_event)):
            if upcoming_event[i][1] == temp:
                upcoming_event[i][1] = ''
            else:
                temp = upcoming_event[i][1]
    sql = """SELECT m.MemberID, m.FirstName, m.LastName FROM members AS m WHERE m.MemberID = %s"""
    sql_data.execute(sql, (member_id,))
    member_name = sql_data.fetchall()
    sql_data.close()
    return render_template("events.html", membername=member_name, previousresult=previous_result,
                           upcomingevent=upcoming_event, showid=2, adminflag=1)


@app.route('/admin')
def admin_page():
    """
    Administrator's main interface displaying the current member count and upcoming matches.
    Modify the options preceding the search box to specify the desired content to be searched.

    Args:
        member_count (str) : Current member count.
        upcoming_event (list): A list of upcoming event information.

    :return: admin_home.html
    """
    sql_data = get_cursor()
    sql = """SELECT count(*) FROM members;"""
    sql_data.execute(sql)
    member_count = sql_data.fetchall()[0][0]
    sql = """SELECT e.EventName, es.StageName, es.Location, es.StageDate
                FROM events e
                JOIN event_stage es ON es.EventID = e.EventID
                LEFT JOIN event_stage_results esr ON esr.StageID = es.StageID
                WHERE esr.StageID IS NULL;"""
    sql_data.execute(sql)
    upcoming_event = sql_data.fetchall()
    sql_data.close()
    return render_template("admin_home.html", membercount=member_count, upcomingevent=upcoming_event, showid=1)


@app.route('/admin_search', methods=['POST'])
def search_page():
    """
    A dedicated area designed for receiving search data on the admin page and navigating to their respective interfaces.

    Args:
        search_type (str) : Type of search.
        search_data (str): Data searched.

    :return: None
    """
    search_type = request.form.get('search_type')
    search_data = request.form.get('search_data')
    if search_type == "member":
        return redirect(url_for('admin_member_page', name_like=search_data))
    elif search_type == "event":
        return redirect(url_for('admin_event_page', event_like=search_data))
    elif search_type == "event_stage":
        return redirect(url_for('admin_event_stage', stage_like=search_data))
    elif search_type == "team":
        return redirect(url_for('admin_team_page', team_like=search_data))
    elif search_type == "event_stage_result":
        return redirect(url_for('admin_event_stage_result', result_like=search_data))
    else:
        return render_template("admin_home.html", showid=1)


@app.route('/admin_member', methods=['GET', 'POST'])
def admin_member_page():
    """
    Including the addition, deletion, modification and query of member information

    Args:
        member_count (int) : Current member count.
        page (int) : The number of pages currently viewed.
        name_like (str): Get search data.
        member_list (list): Member information of the current page.
        team_list (list) : A list of all team information.

    :return: admin_member.html
    """
    sql_data = get_cursor()
    sql = """SELECT count(*) FROM members;"""
    sql_data.execute(sql)
    member_count = sql_data.fetchall()[0][0]
    member_count = math.ceil(member_count / 10)
    page = request.args.get('page')
    name_like = request.args.get('name_like')
    if not page:
        sql_page = 0
    else:
        page = int(page)
        sql_page = (page - 1) * 10
    if not name_like:
        sql = """SELECT m.FirstName, m.LastName, t.TeamName, m.City, m.Birthdate, m.MemberID, t.TeamID
                        FROM members AS m
                        INNER JOIN teams AS t ON m.TeamID = t.TeamID
                        LIMIT %s, 10;"""
        sql_data.execute(sql, (sql_page,))
    else:
        sql = """SELECT m.FirstName, m.LastName, t.TeamName, m.City, m.Birthdate, m.MemberID, t.TeamID
                    FROM members AS m
                    INNER JOIN teams AS t ON m.TeamID = t.TeamID
                    WHERE CONCAT(m.FirstName, m.LastName, t.TeamName, m.City) LIKE %s;"""
        name_like = "%" + name_like + "%"
        sql_data.execute(sql, (name_like,))
    member_list = sql_data.fetchall()
    member_list = [list(item) for item in member_list]
    for i in member_list:
        i[4] = str(i[4])
    sql = """SELECT TeamID, TeamName FROM teams ORDER BY TeamName;"""
    sql_data.execute(sql)
    team_list = sql_data.fetchall()
    if request.method == 'GET':
        sql_data.close()
        if not name_like:
            return render_template("admin_member.html", memberlist=member_list, membercount=member_count,
                                   teamlist=team_list, page=page, showid=2)
        else:
            return render_template("admin_member.html", memberlist=member_list, teamlist=team_list, showid=2)
    else:
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        select_box = request.form.get('selectBox')
        city = request.form.get('city')
        birthdate = request.form.get('birthdate')
        member_id = request.form.get('memberID')
        if not member_id:
            sql = """INSERT INTO members (TeamID, FirstName, LastName, City, Birthdate)
                        VALUES (%s, %s, %s, %s, %s);"""
            values = (select_box, first_name, last_name, city, birthdate,)
            sql_data.execute(sql, values)
            detail = sql_data.fetchall()
        else:
            sql = """UPDATE members SET TeamID = %s, FirstName = %s, LastName = %s, City = %s, Birthdate = %s
                        WHERE MemberID = %s;"""
            values = (select_box, first_name, last_name, city, birthdate, member_id,)
            sql_data.execute(sql, values)
            detail = sql_data.fetchall()
        sql_data.close()
        return redirect(url_for('admin_member_page'))


@app.route('/admin_delete_member')
def admin_delete_member():
    """
    Database information for deleting a member's record.

    Args:
        member_id (str): Get delete data.

    :return: None
    """
    member_id = request.args.get('memberID')
    sql_data = get_cursor()
    sql = """DELETE FROM members WHERE MemberID = %s;"""
    sql_data.execute(sql, (member_id,))
    detail = sql_data.fetchall()
    sql_data.close()
    return redirect(url_for('admin_member_page'))


@app.route('/admin_event', methods=['GET', 'POST'])
def admin_event_page():
    """
    Including adding, deleting, modifying and querying event page information

    Args:
        event_count (int) : Current event count.
        page (int) : The number of pages currently viewed.
        event_like (str): Get search data.
        event_list (list): Event information of the current page.
        team_list (list) : A list of all team information.

    :return: admin_event.html
    """
    sql_data = get_cursor()
    sql = """SELECT count(*) FROM `events`;"""
    sql_data.execute(sql)
    event_count = sql_data.fetchall()[0][0]
    event_count = math.ceil(event_count / 10)
    page = request.args.get('page')
    event_like = request.args.get('event_like')
    if not page:
        sql_page = 0
    else:
        page = int(page)
        sql_page = (page - 1) * 10
    if not event_like:
        sql = """SELECT e.EventID, e.EventName, e.Sport, t.TeamName, t.TeamID
                    FROM `events` AS e
                    INNER JOIN teams AS t ON e.NZTeam = t.TeamID
                    LIMIT %s, 10;"""
        sql_data.execute(sql, (sql_page,))
    else:
        sql = """SELECT e.EventID, e.EventName, e.Sport, t.TeamName, t.TeamID
                    FROM `events` AS e
                    INNER JOIN teams AS t ON e.NZTeam = t.TeamID
                    WHERE CONCAT(e.EventName, e.Sport, t.TeamName) LIKE %s;"""
        event_like = "%" + event_like + "%"
        sql_data.execute(sql, (event_like,))
    event_list = sql_data.fetchall()
    sql = """SELECT TeamID, TeamName FROM teams ORDER BY TeamName;"""
    sql_data.execute(sql)
    team_list = sql_data.fetchall()
    if request.method == 'GET':
        sql_data.close()
        if not event_like:
            return render_template("admin_event.html", eventlist=event_list, eventcount=event_count,
                                   teamlist=team_list, page=page, showid=3)
        else:
            return render_template("admin_event.html", eventlist=event_list, teamlist=team_list, showid=3)
    else:
        event_id = request.form.get('EventID')
        event_name = request.form.get('eventName')
        sport = request.form.get('sport')
        select_box = request.form.get('selectBox')
        if not event_id:
            sql = """INSERT INTO `events` (EventName, Sport, NZTeam)
                        VALUES (%s, %s, %s);"""
            values = (event_name, sport, select_box,)
            sql_data.execute(sql, values)
            detail = sql_data.fetchall()
        else:
            sql = """UPDATE `events` SET EventName = %s, Sport = %s, NZTeam = %s
                        WHERE EventID = %s;"""
            values = (event_name, sport, select_box, event_id,)
            sql_data.execute(sql, values)
            detail = sql_data.fetchall()
        sql_data.close()
        return redirect(url_for('admin_event_page'))


@app.route('/admin_delete_event')
def admin_delete_event():
    """
    Database information for deleting an event's record.

    Args:
        event_id (str): Get delete data.

    :return: None
    """
    event_id = request.args.get('eventID')
    sql_data = get_cursor()
    sql = """DELETE FROM `events` WHERE EventID = %s;"""
    sql_data.execute(sql, (event_id,))
    detail = sql_data.fetchall()
    sql_data.close()
    return redirect(url_for('admin_event_page'))


@app.route('/admin_event_stage', methods=['GET', 'POST'])
def admin_event_stage():
    """
    Including adding, deleting, modifying and querying event stage page information

    Args:
        stage_count (int) : Current event stage count.
        page (int) : The number of pages currently viewed.
        stage_like (str): Get search data.
        stage_list (list): Event stage information of the current page.
        event_list (list) : A list of all event information.

    :return: admin_event_stage.html
    """
    sql_data = get_cursor()
    sql = """SELECT count(*) FROM event_stage;"""
    sql_data.execute(sql)
    stage_count = sql_data.fetchall()[0][0]
    stage_count = math.ceil(stage_count / 10)
    sql = """SELECT EventID, EventName FROM `events`;"""
    sql_data.execute(sql)
    event_list = sql_data.fetchall()
    stage_like = request.args.get('stage_like')
    page = request.args.get('page')
    if not page:
        sql_page = 0
    else:
        page = int(page)
        sql_page = (page - 1) * 10
    if not stage_like:
        sql = """SELECT es.StageID, es.StageName, e.EventName, e.EventID, es.StageDate, es.Location, es.Qualifying, es.PointsToQualify
                    FROM event_stage AS es 
                    INNER JOIN events AS e ON e.EventID = es.EventID 
                    ORDER BY es.StageDate
                    LIMIT %s,10;"""
        sql_data.execute(sql, (sql_page,))
    else:
        sql = """SELECT es.StageID, es.StageName, e.EventName, e.EventID,  es.StageDate, es.Location, es.Qualifying, es.PointsToQualify
                    FROM event_stage AS es 
                    INNER JOIN events AS e ON e.EventID = es.EventID 
                    WHERE CONCAT(es.StageName, e.EventName, es.Location) LIKE %s;"""
        stage_like = "%" + stage_like + "%"
        sql_data.execute(sql, (stage_like,))
    stage_list = sql_data.fetchall()
    stage_list = [list(item) for item in stage_list]
    for i in stage_list:
        i[4] = str(i[4])
    if request.method == 'GET':
        sql_data.close()
        if not stage_like:
            return render_template("admin_event_stage.html", stagelist=stage_list, stagecount=stage_count,
                                   eventlist=event_list, page=page, showid=4)
        else:
            return render_template("admin_event_stage.html", stagelist=stage_list, eventlist=event_list, showid=4)
    else:
        stage_name = request.form.get('stage_name')
        event_name = request.form.get('event_name')
        data_location = request.form.get('data_location')
        stage_date = request.form.get('stage_date')
        points = request.form.get('points')
        stage_id = request.form.get('stageID')
        # Process data
        if stage_name == 'Final':
            qualifying = 0
            points = None
        else:
            qualifying = 1
        if not stage_id:
            sql = """INSERT INTO event_stage (StageName, EventID, Location, StageDate, Qualifying, PointsToQualify) 
                        VALUES (%s, %s, %s, %s, %s, %s);"""
            values = (stage_name, event_name, data_location, stage_date, qualifying, points)
            sql_data.execute(sql, values)
            detail = sql_data.fetchall()
        else:
            sql = """UPDATE event_stage SET StageName = %s, EventID = %s, Location = %s, StageDate = %s, Qualifying = %s, PointsToQualify = %s 
                        WHERE StageID = %s;"""
            values = (stage_name, event_name, data_location, stage_date, qualifying, points, stage_id)
            sql_data.execute(sql, values)
            detail = sql_data.fetchall()
        sql_data.close()
        return redirect(url_for('admin_event_stage'))


@app.route('/admin_delete_stage')
def admin_delete_stage():
    """
    Database information for deleting an event stage's record.

    Args:
        stage_id (str): Get delete data.

    :return: None
    """
    stage_id = request.args.get('stageID')
    sql_data = get_cursor()
    sql = """DELETE FROM event_stage WHERE StageID = %s;"""
    sql_data.execute(sql, (stage_id,))
    detail = sql_data.fetchall()
    sql_data.close()
    return redirect(url_for('admin_event_stage'))


@app.route('/admin_team', methods=['GET', 'POST'])
def admin_team_page():
    """
    Including adding, deleting, modifying and querying team page information

    Args:
        team_count (int) : Current team count.
        page (int) : The number of pages currently viewed.
        team_like (str): Get search data.
        stage_list (list): Event stage information of the current page.
        event_list (list) : A list of all event information.

    :return: admin_team.html
    """
    sql_data = get_cursor()
    sql = """SELECT count(*) FROM teams;"""
    sql_data.execute(sql)
    team_count = sql_data.fetchall()[0][0]
    team_count = math.ceil(team_count / 10)
    page = request.args.get('page')
    team_like = request.args.get('team_like')
    if not page:
        sql_page = 0
    else:
        page = int(page)
        sql_page = (page - 1) * 10
    if not team_like:
        sql = """SELECT TeamID, TeamName FROM teams LIMIT %s,10;"""
        sql_data.execute(sql, (sql_page,))
    else:
        sql = """SELECT TeamID, TeamName FROM teams WHERE TeamName LIKE %s;"""
        team_like = "%" + team_like + "%"
        sql_data.execute(sql, (team_like,))
    team_list = sql_data.fetchall()
    if request.method == 'GET':
        sql_data.close()
        if not team_like:
            return render_template("admin_team.html", teamlist=team_list, teamcount=team_count, page=page, showid=5)
        else:
            return render_template("admin_team.html", teamlist=team_list, showid=5)
    else:
        team_id = request.form.get('teamID')
        team_name = request.form.get('teamName')
        if not team_id:
            sql = """INSERT INTO teams (TeamName) VALUES (%s);"""
            values = (team_name,)
            sql_data.execute(sql, values)
            detail = sql_data.fetchall()
        else:
            sql = """UPDATE teams SET TeamName = %s WHERE TeamID = %s;"""
            values = (team_name, team_id,)
            sql_data.execute(sql, values)
            detail = sql_data.fetchall()
        sql_data.close()
        return redirect(url_for('admin_team_page'))


@app.route('/admin_delete_team')
def admin_delete_team():
    """
    Database information for deleting a team's record.

    Args:
        team_id (str): Get delete data.

    :return: None
    """
    team_id = request.args.get('teamID')
    sql_data = get_cursor()
    sql = """DELETE FROM teams WHERE TeamID = %s;"""
    sql_data.execute(sql, (team_id,))
    detail = sql_data.fetchall()
    sql_data.close()
    return redirect(url_for('admin_team_page'))


@app.route('/admin_event_stage_result', methods=['GET', 'POST'])
def admin_event_stage_result():
    """
    Including adding, deleting, modifying and querying event stage result page information

    Args:
        result_count (int) : Current event stage result count.
        event_stage_list (list) : Get entry information.
        temp (dictionary) : Temporary variables.
        page (int) : The number of pages currently viewed.
        result_like (str): Get search data.
        member_list (list): A list of all member information.
        result_list (list) : A list of all event stage result information.

    :return: admin_event_stage_result.html
    """
    sql_data = get_cursor()
    sql = """SELECT count(*) FROM event_stage_results;"""
    sql_data.execute(sql)
    result_count = sql_data.fetchall()[0][0]
    result_count = math.ceil(result_count / 10)
    sql = """SELECT es.StageID, e.EventName, es.Location, es.StageName
                FROM event_stage AS es
                LEFT JOIN event_stage_results AS esr ON esr.StageID = es.StageID
                LEFT JOIN `events` AS e ON e.EventID = es.EventID;"""
    sql_data.execute(sql)
    event_stage_list = sql_data.fetchall()
    # Convert data into dictionaries with hierarchical relationships
    temp = {}
    for stage_id, event_name, location, stage_name in event_stage_list:
        if location not in temp:
            temp[location] = {}
        if event_name not in temp[location]:
            temp[location][event_name] = {}
        temp[location][event_name][stage_name] = stage_id
    event_stage_list = temp
    sql = """SELECT m.MemberID, m.FirstName, m.LastName FROM members AS m;"""
    sql_data.execute(sql)
    member_list = sql_data.fetchall()
    result_like = request.args.get('result_like')
    page = request.args.get('page')
    if not page:
        sql_page = 0
    else:
        page = int(page)
        sql_page = (page - 1) * 10
    if not result_like:
        sql = """SELECT esr.ResultID, es.Location, e.EventName, e.EventID, es.StageName, CONCAT(m.FirstName, ' ', m.LastName) AS members_name, m.MemberID, esr.PointsScored, esr.Position, es.StageID
                    FROM event_stage_results AS esr
                    INNER JOIN event_stage AS es ON esr.StageID = es.StageID
                    INNER JOIN members AS m ON esr.MemberID = m.MemberID 
                    INNER JOIN `events` AS e ON e.EventID = es.EventID
                    LIMIT %s,10;"""
        sql_data.execute(sql, (sql_page,))
    else:
        sql = """SELECT esr.ResultID, es.Location, e.EventName, e.EventID, es.StageName, CONCAT(m.FirstName, ' ', m.LastName) AS members_name, m.MemberID, esr.PointsScored, esr.Position, es.StageID
                    FROM event_stage_results AS esr
                    INNER JOIN event_stage AS es ON esr.StageID = es.StageID
                    INNER JOIN members AS m ON esr.MemberID = m.MemberID 
                    INNER JOIN `events` AS e ON e.EventID = es.EventID
                    WHERE CONCAT(es.Location, e.EventName, es.StageName, m.FirstName, m.LastName) LIKE %s;"""
        result_like = "%" + result_like + "%"
        sql_data.execute(sql, (result_like,))
    result_list = sql_data.fetchall()
    if request.method == 'GET':
        sql_data.close()
        if not result_like:
            return render_template("admin_event_stage_result.html", resultlist=result_list, resultcount=result_count,
                                   eventstagelist=event_stage_list, memberlist=member_list, page=page, showid=6)
        else:
            return render_template("admin_event_stage_result.html", resultlist=result_list,
                                   eventstagelist=event_stage_list, memberlist=member_list, showid=6)
    else:
        select3 = request.form.get('select3')
        select_member = request.form.get('select_member')
        event_points = request.form.get('event_points')
        position = request.form.get('position')
        result_id = request.form.get('resultID')
        if position == '':
            position = None
        if not result_id:
            sql = """INSERT INTO event_stage_results (StageID, MemberID, PointsScored, Position) 
                        VALUES (%s, %s, %s, %s);"""
            values = (select3, select_member, event_points, position)
            sql_data.execute(sql, values)
            detail = sql_data.fetchall()
        else:
            sql = """UPDATE event_stage_results SET StageID = %s, MemberID = %s, PointsScored = %s, Position = %s 
                        WHERE ResultID = %s;"""
            values = (select3, select_member, event_points, position, result_id)
            sql_data.execute(sql, values)
            detail = sql_data.fetchall()
        sql_data.close()
        return redirect(url_for('admin_event_stage_result'))


@app.route('/admin_delete_result')
def admin_delete_result():
    """
    Database information for deleting an event stage result's record.

    Args:
        result_id (str): Get delete data.

    :return: None
    """
    result_id = request.args.get('resultID')
    sql_data = get_cursor()
    sql = """DELETE FROM event_stage_results WHERE ResultID = %s;"""
    sql_data.execute(sql, (result_id,))
    detail = sql_data.fetchall()
    sql_data.close()
    return redirect(url_for('admin_event_stage_result'))


@app.route('/admin_following_reports')
def admin_following_reports():
    """
    On one side, the interface displays the count and total number of gold, silver, and bronze medals.
    On the other side, it presents a sorted list of members.

    Args:
        medals (list): Get data for each medal each person has won.
        result (list): Calculate the total number of each medal.
        temp (list) : Temporary variables.
        team_member (list) : Get team and member information.

    :return: admin_following_reports.html
    """
    sql_data = get_cursor()
    sql = """SELECT m.FirstName, m.LastName,
                    COUNT(CASE WHEN esr.Position = 1 THEN 1 END) AS GoldMedals,
                    COUNT(CASE WHEN esr.Position = 2 THEN 1 END) AS SilverMedals,
                    COUNT(CASE WHEN esr.Position = 3 THEN 1 END) AS BronzeMedals
                FROM members m
                JOIN event_stage_results esr ON esr.MemberID = m.MemberID
                GROUP BY m.FirstName, m.LastName;"""
    sql_data.execute(sql)
    medals = sql_data.fetchall()
    # Calculate the total number of each medal
    result = []
    goldTotal = silverTotal = bronzeTotal = 0
    for firstName, lastName, goldMedals, silverMedals, bronzeMedals in medals:
        if goldMedals == 0 and silverMedals == 0 and bronzeMedals == 0:
            continue
        temp = [firstName, lastName, goldMedals, silverMedals, bronzeMedals]
        goldTotal += goldMedals
        silverTotal += silverMedals
        bronzeTotal += bronzeMedals
        result.append(temp)
    temp = ['Count : ', '', goldTotal, silverTotal, bronzeTotal]
    result.append(temp)
    sql = """SELECT t.TeamID, t.TeamName, m.FirstName, m.LastName
                FROM members m
                JOIN teams t ON t.TeamID = m.TeamID
                ORDER BY t.TeamName, m.LastName, m.FirstName;"""
    sql_data.execute(sql)
    team_member = sql_data.fetchall()
    if team_member:
        team_member = [list(item) + [0] for item in team_member]
        temp = team_member[0][1]
        count = sum(1 for item in team_member if item[0] == team_member[0][0])
        team_member[0][-1] = count
        for i in range(1, len(team_member)):
            if team_member[i][1] == temp:
                team_member[i][1] = ''
            else:
                count = sum(1 for item in team_member if item[0] == team_member[i][0])
                temp = team_member[i][1]
                team_member[i][-1] = count
    sql_data.close()
    return render_template("admin_following_reports.html", result=result, teammember=team_member, showid=7)


@app.errorhandler(Exception)
def handle_error(error):
    """
    Receive all unexpected errors
    :param error:
    :return: error.html
    """
    print(error)
    return render_template('error.html', adminflag=1)


if __name__ == '__main__':
    app.run(debug=True)
