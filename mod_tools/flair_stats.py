from flask import Blueprint, make_response, render_template, session, redirect, request, Response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from redditflair.reddit import Reddit
import redditflair.blizzard as blizzard
from redditflair.parse import parseOWProfile
from config import get_flairdata
from database import db, User, Specials, Database
import json, time, datetime, pygal
from pygal.style import Style

flair_stats = Blueprint('flair_stats', __name__)

OWL_TEAMS = ['boston-uprising', 'dallas-fuel', 'florida-mayhem', 'houston-outlaws', 'london-spitfire', 'los-angeles-gladiators', 'los-angeles-valiant', 'new-york-excelsior', 'philadelphia-fusion', 'san-francisco-shock', 'seoul-dynasty', 'shanghai-dragons']

custom_style = Style(
  colors=('#174B97', '#0B233F', '#FEDC01', '#96CA4E', '#59CAE8', '#381360', '#2A7230', '#181C39', '#F89D2A', '#FC4C01', '#000000', '#D22730'))


def collect_flair_stats(mod=False, time_passed = 21600):
    flairdata = get_flairdata()
    # load flair stats file
    with open('statistics/flair_stats.json', 'r') as f:
        flair_stats = json.load(f)
        
    if mod:
        # check if most recent entry is younger than 1 hour
        if (time.time() - flair_stats[-1]['timestamp']) < time_passed:
            return flair_stats
            
        new_stats = dict()
        new_stats['timestamp'] = time.time()
        new_stats['flairs'] = dict()
        
        for team_id in flairdata['flairs']:
            flair_counts = dict()
            flair_counts['primary'] = len(User.query.filter_by(flair1=team_id).all())
            flair_counts['secondary'] = len(User.query.filter_by(flair2=team_id).all())
            flair_counts['total'] = flair_counts['primary'] + flair_counts['secondary']
            new_stats['flairs'][team_id] = flair_counts
            
        flair_stats.append(new_stats)
         
        with open('statistics/flair_stats.json', 'w') as f:
            json.dump(flair_stats, f, indent=4)
    
    return flair_stats

# user verification
@flair_stats.route('/flairstats')
def flairStats():
    flairdata = get_flairdata()
    responseParams = dict()
    responseParams['redditLink'] = Reddit.auth_link('flairstats')
    
    # moderator check
    redditname = session.get('redditname')
    mod = False
    if redditname:
        if Database.check_moderator(redditname):
            mod = True
    
    flair_stats = collect_flair_stats(mod)
    
    graph = pygal.DateTimeLine(
        style=custom_style,
        x_label_rotation=35, truncate_label=-1,
        x_value_formatter=lambda dt: dt.strftime('%d %b %Y'))
    
    for team in OWL_TEAMS:
        series = []
        for stats in flair_stats:
            if team in stats['flairs']:
                dt = datetime.datetime.utcfromtimestamp(stats['timestamp'])
                count = stats['flairs'][team]['total']
                series.append((dt, count))
        graph.add(flairdata['flairs'][team]['name'], series, dots_size=1)
    
    
    #bar_chart = pygal.Bar()                                            # Then create a bar graph object
    #bar_chart.add('Fibonacci', [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55])  # Add some values
    #bar_chart.render_to_file('bar_chart.svg')    
    
    #return bar_chart.render_response()
    
    graph = graph.render_data_uri()
    #graph = graph.render()

    #return Response(response=graph.render(is_unicode=True), content_type='image/svg+xml')
    return render_template('flairstats.html', graph = graph)
    
    #response = make_response(render_template('userverification.html', **responseParams, mod = mod, verifiedUsers = verified_users))

    
@flair_stats.route('/flairstats/force')
def flairStatsForceUpdate():
    # moderator check
    redditname = session.get('redditname')
    mod = False
    if redditname:
        if Database.check_moderator(redditname):
            mod = True
            
    if not mod:
        return redirect('/flairstats')
        
    collect_flair_stats(mod, time_passed = 0)    
        
    return redirect('/flairstats')
    