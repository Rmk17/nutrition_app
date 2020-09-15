from flask import Flask, render_template, g, request
from datetime import datetime
from database import get_db, connect_db

app = Flask(__name__)


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/', methods=['GET', 'POST'])
def index():
    db = get_db()
    if request.method == 'POST':
        date = request.form['date']  # assuming the date is in YYYY-MM-DD format
        dt = datetime.strptime(date, '%Y-%m-%d')  # parse date from a string
        database_date = datetime.strftime(dt, '%Y%m%d')  # convert to database format
        db.execute('insert into log_date (entry_date) values (?)', [database_date])
        db.commit()

    """
    cur = db.execute('select log_date.entry_date, sum(food.protein) as protein, '
                     'sum(food.carbohydrates) as carbohydrates, sum(food.fat) as fat, sum(food.calories) as calories '
                     'from food_date join log_date on log_date.id = food_date.log_date_id '
                     'join food on food.id = food_date.food_id '
                     'group by log_date.id '
                     'union '
                     'select log_date.entry_date, 0, 0, 0, 0 from log_date '
                     'where log_date.id not in (select log_date.id from food_date join log_date on '
                     'food_date.log_date_id = log_date.id) '
                     'order by log_date.entry_date desc')
    """

    cur = db.execute('select '
                     'log_date.entry_date, '
                     'sum(food.protein) as protein, '
                     'sum(food.carbohydrates) as carbohydrates, '
                     'sum(food.fat) as fat, '
                     'sum(food.calories) as calories '
                     'from '
                     'log_date '
                     'left join food_date on food_date.log_date_id = log_date.id '
                     'left join food on food.id = food_date.food_id '
                     'group by log_date.id order by log_date.entry_date desc')

    # cur = db.execute('select entry_date from log_date order by entry_date desc')
    results = cur.fetchall()

    date_results = []
    for i in results:
        single_date = {'entry_date': i['entry_date'], 'protein': i['protein'], 'carbohydrates': i['carbohydrates'],
                       'fat': i['fat'], 'calories': i['calories']}

        d = datetime.strptime(str(i['entry_date']), '%Y%m%d')  # parse date from string
        single_date['pretty_date'] = datetime.strftime(d, '%B %d, %Y')  # format date to pretty format
        date_results.append(single_date)

    return render_template('home.html', results=date_results)


@app.route('/view/<date>', methods=['GET', 'POST'])  # date is going to be in format like 20170520
def view(date):
    db = get_db()

    cur = db.execute('select id, entry_date from log_date where entry_date = ?', [date])
    date_result = cur.fetchone()

    if request.method == 'POST':
        db.execute('insert into food_date (food_id, log_date_id) values (?, ?)',
                   [request.form['food-select'],
                    date_result['id']])
        db.commit()

    d = datetime.strptime(str(date_result['entry_date']), '%Y%m%d')
    pretty_date = datetime.strftime(d, '%B %d, %Y')

    food_cur = db.execute('select id, name from food')
    food_results = food_cur.fetchall()

    log_cur = db.execute('select food.name, food.protein, food.carbohydrates, food.fat, food.calories '
                         'from food_date join log_date on log_date.id = food_date.log_date_id '
                         'join food on food.id = food_date.food_id '
                         'where log_date.entry_date = ?', [date])
    log_results = log_cur.fetchall()

    totals = {'protein': 0, 'carbohydrates': 0, 'fat': 0, 'calories': 0}
    for food_item in log_results:
        totals['protein'] += food_item['protein']
        totals['carbohydrates'] += food_item['carbohydrates']
        totals['fat'] += food_item['fat']
        totals['calories'] += food_item['calories']

    return render_template('day.html', entry_date=date_result['entry_date'], pretty_date=pretty_date,
                           food_results=food_results, log_results=log_results, totals=totals)


@app.route('/food', methods=['GET', 'POST'])
def food():
    db = get_db()
    if request.method == 'POST':
        name = request.form['food-name']
        protein = int(request.form['protein'])
        carbohydrates = int(request.form['carbohydrates'])
        fat = int(request.form['fat'])
        calories = protein * 4 + carbohydrates * 4 + fat * 9

        db.execute('insert into food (name, protein, carbohydrates, fat, calories) values (?, ?, ?, ?, ?)',
                   [name, protein, carbohydrates, fat, calories])
        db.commit()

    cur = db.execute('select name, protein, carbohydrates, fat, calories from food')
    results = cur.fetchall()

    return render_template('add_food.html', results=results)


if __name__ == '__main__':
    app.run(debug=True)
