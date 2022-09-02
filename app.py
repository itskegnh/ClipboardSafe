import flask, hashlib, pymongo, time, datetime

client = pymongo.MongoClient('mongodb+srv://kegnh:Roto2007!@cluster0.y6h0h.mongodb.net/?retryWrites=true&w=majority')
db = client['clipboard']
accounts = db['accounts']
posts = db['posts']
invites = db['invites']
tutorials = [{'title': 'Create Account', 'description': 'Learn how to sign up for an account.', 'url': 'signup'}]

def hash(string):
    return hashlib.sha256(string.encode('utf-8')).hexdigest()

app = flask.Flask(__name__)
app.secret_key = hash('ahefulkajfen aefiheaf29841')


def verify(token):
    return bool(accounts.find_one({'_id': token}))

@app.route('/')
def index():
    if not verify(flask.session.get('token')):
        return flask.redirect('/login')
    account = accounts.find_one({'_id': flask.session.get('token')})
    if not account.get('public_token'):
        accounts.update_one({'_id': flask.session.get('token')}, {'$set': {'public_token': hash(str(time.time()) + flask.session.get('token'))}})
    account = accounts.find_one({'_id': flask.session.get('token')})
    return flask.redirect('/posts/' + account.get('public_token'))

@app.route('/posts/<public_account_token>')
def public_account(public_account_token):
    widgets = []
    account = accounts.find_one({'public_token': public_account_token})
    for post in posts.find({'owner': account.get('_id')}):
        if post.get('archived'):
            continue
        widgets.append(post)
    widgets.reverse()
    acc = accounts.find_one({'_id': flask.session.get('token')})
    dark = False
    if acc: dark = acc.get('dark', False)
    return flask.render_template('index.html', widgets=widgets, dark=dark, own=account.get('_id') == flask.session.get('token'), all=False)

@app.route('/archive')
def archive():
    if not verify(flask.session.get('token')):
        return flask.redirect('/login')
    widgets = []
    for post in posts.find({'owner': flask.session.get('token'), 'archived': True}):
        widgets.append(post)
    widgets.reverse()
    return flask.render_template('archive.html', widgets=widgets, dark=accounts.find_one({'_id': flask.session.get('token')}).get('dark', False))

@app.route('/profile')
def profile():
    if not verify(flask.session.get('token')):
        return flask.redirect('/login')
    return flask.render_template('profile.html', token=flask.session.get('token'), dark=accounts.find_one({'_id': flask.session.get('token')}).get('dark', False))

@app.route('/toggle-dark')
def toggle_dark():
    if not verify(flask.session.get('token')):
        return flask.redirect('/login')
    accounts.update_one({'_id': flask.session.get('token')}, {'$set': {'dark': not accounts.find_one({'_id': flask.session.get('token')}).get('dark', False)}})
    return flask.redirect('/profile')

@app.route('/create')
def create():
    if not verify(flask.session.get('token')):
        return flask.redirect('/login')
    return flask.render_template('create.html', dark=accounts.find_one({'_id': flask.session.get('token')}).get('dark', False))

@app.route('/create/<tab>', methods=['GET', 'POST'])
def create_post(tab):
    if tab not in ['fa', 'ba', 'tr']:
        return flask.redirect('/create')
    if not verify(flask.session.get('token')):
        return flask.redirect('/login')
    if flask.request.method == 'GET':
        return flask.render_template('create' + tab + '.html', dark=accounts.find_one({'_id': flask.session.get('token')}).get('dark', False))

    pretify = {
        "fa": "Front Area",
        "ba": "Back Area",
        "tr": "Training"
    }

    # POST
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    date = datetime.datetime.utcnow()
    date = f"{months[date.month - 1]} {date.day}"

    post = {
        '_id': hash(str(time.time()) + flask.session.get('token')),
        'owner': flask.session.get('token'),
        'date': date,
        'managers': flask.request.form.get('managers'),
        'type': pretify[tab],

        'oepe': flask.request.form.get('oepe'),
        'mfy': flask.request.form.get('mfy'),
        'sta': flask.request.form.get('sta'),
        'waste': flask.request.form.get('waste'),

        'running': flask.request.form.get('running'),
        'presenting': flask.request.form.get('presenting'),
        'ot': flask.request.form.get('ot'),
        'cod2': flask.request.form.get('cod2'),
        'cash': flask.request.form.get('cash'),
        'fries': flask.request.form.get('fries'),
        'counter': flask.request.form.get('counter'),
        'dd-dt': flask.request.form.get('dd-dt'),
        'dd-fc': flask.request.form.get('dd-fc'),
        'cafe': flask.request.form.get('cafe'),
        'host': flask.request.form.get('host'),

        'grilled': flask.request.form.get('grilled'),
        'fried': flask.request.form.get('fried'),
        'initiator1': flask.request.form.get('initiator1'),
        'initiator2': flask.request.form.get('initiator2'),
        'assembler1': flask.request.form.get('assembler1'),
        'assembler2': flask.request.form.get('assembler2'),

        'trainee1': flask.request.form.get('trainee1'),
        'strengths1': flask.request.form.get('strengths1'),
        'weaknesses1': flask.request.form.get('weaknesses1'),
        'feedback1': flask.request.form.get('feedback1'),

        'trainee2': flask.request.form.get('trainee2'),
        'strengths2': flask.request.form.get('strengths2'),
        'weaknesses2': flask.request.form.get('weaknesses2'),
        'feedback2': flask.request.form.get('feedback2'),

        'highlights': flask.request.form.get('highlights'),
        'feedback': flask.request.form.get('feedback'),
        'overview': flask.request.form.get('overview'),
    }
    posts.insert_one(post)
    return flask.redirect('/')

@app.route('/view/<post>')
def view(post):
    post = posts.find_one({'_id': post})
    if not post: 
        return """<h1>Invalid Post Link!</h1>"""
    acc = accounts.find_one({'_id': flask.session.get('token')})
    dark = False
    if acc:
        dark = acc.get('dark', False)
    return flask.render_template('view.html', post=post, visitor=flask.session.get('token'), owner=accounts.find_one({'_id': post['owner']}), dark=dark, post_id=post['_id'], archive=False)

@app.route('/archive/view/<post_id>')
def archive_view(post_id):
    if not verify(flask.session.get('token')): return flask.redirect('/login')
    post = posts.find_one({'_id': post_id, 'archived': True})
    if not post: return flask.redirect('/')
    if post['owner'] != flask.session.get('token'): return flask.redirect('/')
    return flask.render_template('view.html', post=post, visitor='', owner=accounts.find_one({'_id': post['owner']}), dark=accounts.find_one({'_id': flask.session.get('token')}).get('dark', False), post_id=post['_id'], archive=True)

@app.route('/archive/restore/<post_id>')
def archive_restore(post_id):
    if not verify(flask.session.get('token')): return flask.redirect('/login')
    post = posts.find_one({'_id': post_id, 'archived': True})
    if not post: return flask.redirect('/')
    if post['owner'] != flask.session.get('token'): return flask.redirect('/')
    posts.update_one({'_id': post_id}, {'$set': {'archived': False}})
    return flask.redirect('/archive')

@app.route('/delete/post/<post_id>')
def delete_post(post_id):
    if not verify(flask.session.get('token')):
        return flask.redirect('/login')
    post = posts.find_one({'_id': post_id})
    if not post: return flask.redirect('/')
    if post['owner'] != flask.session.get('token'): return flask.redirect('/')
    posts.update_one({'_id': post_id}, {'$set': {'archived': True}})
    return flask.redirect('/')

@app.route('/delete/account/<account_id>')
def delete_account(account_id):
    if not verify(flask.session.get('token')):
        return flask.redirect('/login')
    account = accounts.find_one({'_id': account_id})
    if not account: return flask.redirect('/')
    if account['_id'] != flask.session.get('token'): return flask.redirect('/')
    posts.delete_many({'owner': account_id})
    accounts.delete_one({'_id': account_id})
    return flask.redirect('/')

@app.route('/invite')
def invite():
    if not verify(flask.session.get('token')):
        return flask.redirect('/login')
    acc = accounts.find_one({'_id': flask.session.get('token')})
    if time.time() - acc.get("code-gen", 0) < 3600:  
        code = "This reasource is being rate-limited. Codes can be generated a max of 1 time per hour."
        return flask.render_template('invite.html', valid=False, code=code, dark=accounts.find_one({'_id': flask.session.get('token')}).get('dark', False))
    code = hash(str(time.time()) + flask.session.get('token'))
    accounts.update_one({'_id': flask.session.get('token')}, {'$set': {'code-gen': time.time()}})
    invites.insert_one({'_id': code, 'owner': flask.session.get('token'), 'uses': 100, 'timeout': time.time() + 172800})

    return flask.render_template('invite.html', valid=True, code=code, dark=accounts.find_one({'_id': flask.session.get('token')}).get('dark', False))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if verify(flask.session.get('token')):
        return flask.redirect('/')
    if flask.request.method == 'GET':
        return flask.render_template('signup.html')
    else:
        full_name = flask.request.form['full-name']
        username = flask.request.form['username']
        password = hash(flask.request.form['password'])
        confirm_password = hash(flask.request.form['confirm-password'])
        invite_code = flask.request.form['invite-code']
        # validate invite code
        invite = invites.find_one({'_id': invite_code})
        if not invite:
            return flask.render_template('signup.html', error='Invalid invite code.')
        if invite['uses'] != -1 and invite['uses'] <= 0:
            return flask.render_template('signup.html', error='Invite code cannot be used anymore.')
        if invite['timeout'] < time.time() and invite['timeout'] != -1:
            return flask.render_template('signup.html', error='Invite code has expired.')
        invites.update_one({'_id': invite_code}, {'$inc': {'uses': -1}})

        if len(username) < 4:
            return flask.render_template('signup.html', error='Username must be at least 4 characters long.')
        if len(password) < 4:
            return flask.render_template('signup.html', error='Password must be at least 4 characters long.')
        if full_name == '':
            return flask.render_template('signup.html', error='You must fill in all sections.')
        if accounts.find_one({'username': username}):
            return flask.render_template('signup.html', error='Username already exists.')
        if password != confirm_password:
            return flask.render_template('signup.html', error='Passwords do not match.')
        token = hash(username + password + str(time.time()))
        accounts.insert_one({'_id': token, 'full_name': full_name, 'username': username, 'password': password})
        flask.session['token'] = token
        if invite_code == "maccasmanagement":
            accounts.update_one({'_id': token}, {'$set': {'admin': True}})
        # redirect
        return flask.redirect('/')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if verify(flask.session.get('token')):
        return flask.redirect('/')
    if flask.request.method == 'GET':
        return flask.render_template('login.html')
    else:
        username = flask.request.form['username']
        password = hash(flask.request.form['password'])
        account = accounts.find_one({'username': username, 'password': password})
        if account:
            flask.session['token'] = account['_id']
            return flask.redirect('/')
        else:
            return flask.render_template('login.html', error='Invalid username or password.')

@app.route('/logout')
def logout():
    flask.session.pop('token', None)
    return flask.redirect('/')

@app.route('/posts/all')
def all_posts():
    if not verify(flask.session.get('token')): return flask.redirect('/login')
    account = accounts.find_one({'_id': flask.session.get('token')})
    if not account.get('admin', False):
        return flask.redirect('/')
    widgets = []
    for post in posts.find({'archived': {'$ne': True}}):
        post['name'] = accounts.find_one({'_id': post['owner']}).get('full_name', post.get('type', 'Unknown'))
        widgets.append(post)
    widgets.reverse()
    return flask.render_template('index.html', widgets=widgets, dark=accounts.find_one({'_id': flask.session.get('token')}).get('dark', False), own=False, all=True)

@app.route('/reset-token')
def reset_token():
    if not verify(flask.session.get('token')): return flask.redirect('/login')
    accounts.update_one({'_id': flask.session.get('token')}, {'$set': {'public_token': hash(str(time.time()) + flask.session.get('token'))}})
    return flask.redirect('/')

@app.route('/tutorials')
def tutorials_route():
    return flask.render_template('tutorials.html', widgets=
        tutorials
    )

@app.route('/view/<post_id>/')
def alt_view_post(post_id):
    return flask.redirect('/view/' + post_id)


@app.route('/tutorials/<url>')
def tutorial(url):
    for tutorial in tutorials:
        if tutorial['url'] == url:
            return flask.render_template('tutorials/' + tutorial['url'] + '.html', title=tutorial['title'], description=tutorial['description'])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5080, debug=True)