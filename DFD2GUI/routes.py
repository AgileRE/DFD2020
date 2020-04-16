from flask import render_template, url_for, flash, redirect, request
from DFD2GUI import app, db, project_session
from DFD2GUI.forms import RegistrationForm, LoginForm, UploadDFDFileForm
from DFD2GUI.models import User, Project
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename
from datetime import date
from itertools import count
import os
import json

def activate_link(page):
    active_link = {'dashboard':'', 'project-list':'', 'new-project':''}
    active_link[page] = 'active'
    return active_link

def reset_project_session():
    project_session = {'project_name':'', 'curr_route':'', 'path': ''}

@app.route("/", methods=["POST", "GET"])
@app.route("/login",  methods=['POST', 'GET'])
def login():
    global project_session
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and form.password.data == user.password:
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash("Your email or password is wrong", "danger")
    return render_template('login.html', title="Login", form=form)

@app.route("/register", methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('login'))
    form = RegistrationForm()
    if form.validate_on_submit():
        # Add user to database
        user = User(name=form.name.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()

        # Add user's folder
        directory = form.email.data
        parent_dir = os.path.join(app.root_path, "user_project")
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)

        # Redirect to login
        flash("Your account has been created", "success")
        return redirect(url_for('login'))
    return render_template('register.html', title="Register", form=form)

@app.route("/dashboard")
@login_required
def dashboard():
    projects = {"latest": "", "recent":""}
    # Latest Project Query
    projects["latest"] = Project.query.filter_by(user_id=current_user.id).order_by(Project.id.desc()).limit(5)
    
    # Recent Project Query
    projects["recent"] = Project.query.filter_by(user_id=current_user.id).order_by(Project.date_accessed.desc()).limit(5)

    return render_template('dashboard.html', title="Dashboard", active_link=activate_link('dashboard'), projects=projects)

@app.route("/project-list")
@login_required
def project_list():
    project_list = Project.query.filter_by(user_id=current_user.id).order_by(Project.id)
    project_list = list(enumerate(project_list, 1))
    return render_template('project_list.html', title="Project list", active_link=activate_link('project-list'), projects=project_list)

@app.route("/new-project", methods=["POST", "GET"])
@login_required
def new_project():
    form = UploadDFDFileForm()
    if form.validate_on_submit():
        project_session['curr_route'] = 'new_project'
        path = os.path.join(app.root_path, "user_project", current_user.email, form.project_name.data)
        os.mkdir(path)
        f = open(os.path.join(path, 'metadata.json'), 'w')
        print(os.path.join(path, 'metadata.json'))
        f.close()
        os.mkdir(os.path.join(path, "GUI"))
        project = Project(project_name=form.project_name.data, user_id=current_user.id)
        db.session.add(project)
        db.session.commit()
        project_session['project_name'] = form.project_name.data
        project_session['path'] = path
        return redirect(url_for("add_entity"))
    else:
        print(form.errors)
    return render_template('new_project.html', title="New Project",form=form ,active_link=activate_link('new-project'))

@app.route("/add-entity", methods=["POST", "GET"])
@login_required
def add_entity():
    global project_session
    project_session['curr_route'] = 'add_entity'
    print(project_session)
    return render_template('add_entity.html', title="Add Entity" ,active_link=activate_link('new-project'))

@app.route("/add-entity-func", methods=["POST", "GET"])
@login_required
def add_entity_func():
    global project_session
    entity = request.args.get('entity')
    lis_entity = entity.split("^")
    dic = {}
    for i in list(enumerate(lis_entity)):
        dic[ 'e-'+str(i[0]) ] = {'type': 'entity', 'name':i[1]}
    json_entity = json.dumps(dic, indent=2)
    path = os.path.join(project_session['path'], 'metadata.json')
    with open(path, 'w') as f:
        f.write(json_entity)
    return redirect(url_for("add_datastore"))

@app.route("/add-datastore", methods=["POST", "GET"])
@login_required
def add_datastore():
    return render_template('add_datastore.html', title="Add Datastore" ,active_link=activate_link('new-project'))

@app.route("/add-datastore-func")
@login_required
def add_datastore_func():
    global project_session
    datastore = request.args.get('datastore')
    path = os.path.join(project_session['path'], 'metadata.json')
    lis_datastore = datastore.split("^")
    with open(path, 'r') as f:
        dic = json.loads(f.read())
    for i in list(enumerate(lis_datastore)):
        dic[ 'ds-'+str(i[0]) ] = {'type': 'datastore', 'name':i[1]}
    json_datastore = json.dumps(dic, indent=2)
    with open(path, 'w') as f:
        f.write(json_datastore)
    return redirect(url_for("add_process"))

@app.route("/add-process", methods=["POST", "GET"])
@login_required
def add_process():
    return render_template('add_process.html', title="Add Process" ,active_link=activate_link('new-project'))

@app.route("/add-process-func")
@login_required
def add_process_func():
    global project_session
    path = os.path.join(project_session['path'], 'metadata.json')
    process = request.args.get('process')
    process_list = json.loads(process)
    with open(path, 'r') as f:
        dic = json.loads(f.read())

    for i, item in enumerate(process_list):
        dic[ 'pr-'+str(i) ] = {'type':'process', 'name':item['name'], 'parent':item['parent']}
   
    process_json = json.dumps(dic, indent=2)
    with open(path, 'w') as f:
        f.write(process_json)
    return redirect(url_for("add_process_det"))

@app.route("/add-relation")
@login_required
def add_relation():
    return render_template('add_relation.html', title="Add relation" ,active_link=activate_link('new-project'))

@app.route("/add-process-det")
@login_required
def add_process_det():
    global project_session
    def check_lowest(key, dic):
        for k in dic:
            if dic[k]['parent'] == dic[key]['name']:
                return False
        return True

    def get_lowest(dic):
        output = []
        temp_process = {}
        for i in dic:
            if 'pr' in i:
                temp_process[i] = dic[i]
        for key in temp_process:
            if check_lowest(key, temp_process):
                output.append(key)
        return output

    
    path = os.path.join(project_session['path'], 'metadata.json')
    with open(path, 'r') as f:
        json_txt = f.read()
    dic_process = json.loads(json_txt)
    lowest_process_key = get_lowest(dic_process)
    lowest_process_list = []
    for key in lowest_process_key:
        temp = {key:{'type':'process', 'name':dic_process[key]['name'], 'parent':dic_process[key]['parent']}}
        lowest_process_list.append(temp)
    return render_template('add_process_det.html', title="Add Process Detail" ,active_link=activate_link('new-project'), process=lowest_process_list)

@app.route('/add-process-det-func')
@login_required
def add_process_det_func():
    global project_session
    path = os.path.join(project_session['path'], 'metadata.json')
    gui_json = request.args.get('process_det')
    gui_list = json.loads(gui_json)
    with open(path, 'r') as f:
        dic = json.loads(f.read())
    for gui in gui_list:
        key = gui['id_process']
        dic[key]['gui'] = gui['gui_type']

    output = json.dumps(dic, indent=2)
    with open(path, 'w') as f:
        f.write(output)

    return redirect(url_for('dashboard'))
     

@app.route("/fuck-this-shit")
def fuck_this_shit():
    import shutil
    user_project = os.path.join(app.root_path, 'user_project')
    os.chdir(user_project)
    for i in os.listdir(user_project):
        if os.path.isdir(i):
            shutil.rmtree(i)
        else:
            os.remove(i)

    db.drop_all()
    db.create_all()
    return redirect(url_for('logout'))

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))


# import json

# def check_lowest(key, dic):
#   for k in dic:
#     if dic[k]['parent'] == dic[key]['name']:
#       return False
#   return True

# def get_lowest(dic):
#   output = []
#   temp_process = {}
#   for i in dic:
#     if 'pr' in i:
#       temp_process[i] = dic[i]
#   for key in temp_process:
#     if check_lowest(key, temp_process):
#       output.append(key)
#   return output

# with open('test.json', 'r') as f:
#   json_txt = f.read()

# dic_process = json.loads(json_txt)
# print(get_lowest(dic_process))

