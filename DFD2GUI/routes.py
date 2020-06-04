from flask import render_template, url_for, flash, redirect, request, send_from_directory
from DFD2GUI import app, db, project_session
from DFD2GUI.forms import RegistrationForm, LoginForm, UploadDFDFileForm
from DFD2GUI.models import User, Project
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename
from datetime import date
from itertools import count
import os
import shutil
import json

sample_data = {
    'int': '256',
    'string': 'Boulevard st',
    'float': '12.5',
    'date': '2020-12-31',
    'boolean': 'Yes'
}

def activate_link(page):
    active_link = {'dashboard': '', 'project-list': '', 'new-project': ''}
    active_link[page] = 'active'
    return active_link

def reset_project_session():
    project_session = {'project_name': '', 'curr_route': '', 'path': ''}

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
        user = User(name=form.name.data, email=form.email.data,
                    password=form.password.data)
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
    projects = {"latest": "", "recent": ""}
    # Latest Project Query
    projects["latest"] = Project.query.filter_by(
        user_id=current_user.id).order_by(Project.id.desc()).limit(5)

    # Recent Project Query
    projects["recent"] = Project.query.filter_by(
        user_id=current_user.id).order_by(Project.date_accessed.desc()).limit(5)

    return render_template('dashboard.html', title="Dashboard", active_link=activate_link('dashboard'), projects=projects)

@app.route("/project-list")
@login_required
def project_list():
    project_list = Project.query.filter_by(
        user_id=current_user.id).order_by(Project.id)
    project_list = list(enumerate(project_list, 1))
    return render_template('project_list.html', title="Project list", active_link=activate_link('project-list'), projects=project_list)

@app.route("/new-project", methods=["POST", "GET"])
@login_required
def new_project():
    form = UploadDFDFileForm()
    if form.validate_on_submit():
        project_session['curr_route'] = 'new_project'
        path = os.path.join(app.root_path, "user_project",
                            current_user.email, form.project_name.data)
        os.mkdir(path)
        f = open(os.path.join(path, 'metadata.json'), 'w')
        print(os.path.join(path, 'metadata.json'))
        f.close()
        os.mkdir(os.path.join(path, "GUI"))
        project = Project(project_name=form.project_name.data,
                          user_id=current_user.id)
        db.session.add(project)
        db.session.commit()
        project_session['project_name'] = form.project_name.data
        project_session['path'] = path
        return redirect(url_for("add_entity"))
    else:
        print(form.errors)
    return render_template('new_project.html', title="New Project", form=form, active_link=activate_link('new-project'))

@app.route("/add-entity", methods=["POST", "GET"])
@login_required
def add_entity():
    global project_session
    project_session['curr_route'] = 'add_entity'
    print(project_session)
    return render_template('add_entity.html', title="Add Entity", active_link=activate_link('new-project'))

@app.route("/add-entity-func", methods=["POST", "GET"])
@login_required
def add_entity_func():
    global project_session
    entity = request.args.get('entity')
    lis_entity = entity.split("^")
    dic = {}
    for i in list(enumerate(lis_entity)):
        dic['e-'+str(i[0])] = {'type': 'entity', 'name': i[1]}
    json_entity = json.dumps(dic, indent=2)
    path = os.path.join(project_session['path'], 'metadata.json')
    with open(path, 'w') as f:
        f.write(json_entity)
    return redirect(url_for("add_datastore"))

@app.route("/add-datastore", methods=["POST", "GET"])
@login_required
def add_datastore():
    return render_template('add_datastore.html', title="Add Datastore", active_link=activate_link('new-project'))

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
        dic['ds-'+str(i[0])] = {'type': 'datastore', 'name': i[1]}
    json_datastore = json.dumps(dic, indent=2)
    with open(path, 'w') as f:
        f.write(json_datastore)
    return redirect(url_for("add_process"))

@app.route("/add-process", methods=["POST", "GET"])
@login_required
def add_process():
    return render_template('add_process.html', title="Add Process", active_link=activate_link('new-project'))

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
        dic['pr-'+str(i)] = {'type': 'process',
                             'name': item['name'], 'parent': item['parent']}

    process_json = json.dumps(dic, indent=2)
    with open(path, 'w') as f:
        f.write(process_json)
    return redirect(url_for("add_process_det"))

@app.route("/add-process-det")
@login_required
def add_process_det():
    global project_session
    path = os.path.join(project_session['path'], 'metadata.json')
    with open(path, 'r') as f:
        json_txt = f.read()
    dic_process = json.loads(json_txt)
    lowest_process_key = get_lowest(dic_process)
    lowest_process_list = []
    for key in lowest_process_key:
        temp = {key: {'type': 'process',
                      'name': dic_process[key]['name'], 'parent': dic_process[key]['parent']}}
        lowest_process_list.append(temp)
    return render_template('add_process_det.html', title="Add Process Detail", active_link=activate_link('new-project'), process=lowest_process_list)

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

    return redirect(url_for('add_relation'))

@app.route("/add-relation", methods=["POST", "GET"])
@login_required
def add_relation():
    global project_session
    path = os.path.join(project_session['path'], 'metadata.json')
    with open(path, 'r') as f:
        txt = f.read()
    in_dic = json.loads(txt)
    out_dic = get_rel_input_data(in_dic)
    test = json.dumps(out_dic)
    return render_template('add_relation.html', title="Add relation", active_link=activate_link('new-project'), in_data=test)

@app.route("/add-relation-func", methods=["POST", "GET"])
@login_required
def add_relation_func():
    global project_session
    # Get the json
    rel_get = request.args.get('relation')
    rel_dic = json.loads(rel_get)
    # Get the metadata.json
    path = os.path.join(project_session['path'], 'metadata.json')
    with open(path, 'r') as f:
        txt = f.read()
    metadata_dic = json.loads(txt)
    # Add relation to metadata dictionary
    for relation in rel_dic:
        id_rel = relation['id']
        name_rel = relation['name']
        type_rel = 'relation'
        from_rel = relation['from']
        to_rel = relation['to']
        attr_rel = relation['attr']

        metadata_dic[id_rel] = {
            'type': type_rel,
            'name': name_rel,
            'from': from_rel,
            'to': to_rel,
            'attr': attr_rel
        }

    # Write the dictionary back to the metadata.json file
    output_json = json.dumps(metadata_dic, indent=2)
    with open(path, 'w') as f:
        txt = f.write(output_json)

    return redirect(url_for('add_gui_attr'))

@app.route("/add-gui-attr")
@login_required
def add_gui_attr():
    global project_session

    path = os.path.join(project_session['path'], 'metadata.json')
    with open(path, 'r') as f:
        txt = f.read()
    dic_file = json.loads(txt)
    lis = []
    for i in dic_file.keys():
        if 'pr-' in i and ('gui' in dic_file[i] and dic_file[i]['gui'] != 'no_gui'):
            temp_id = i
            temp_gui_type = dic_file[i]['gui']
            temp_proc_name = dic_file[i]['name']
            lis.append({'id': temp_id, 'name': temp_proc_name,
                        'gui_type': temp_gui_type})
    lis = json.dumps(lis)
    return render_template('add_gui_attr.html', title="Add GUI atrributes", active_link=activate_link('new-project'), data=lis)

@app.route("/add-gui-attr-func")
@login_required
def add_gui_attr_func():
    global project_session

    gui_attr_get = request.args.get('gui_attr')
    gui_attr_dic = json.loads(gui_attr_get)

    path = os.path.join(project_session['path'], 'metadata.json')
    with open(path, 'r') as f:
        txt = f.read()
    metadata_dic = json.loads(txt)

    for i in gui_attr_dic:
        proc_id = i['proc_id']
        gui_attr = i['attr']
        metadata_dic[proc_id]['gui_attr'] = gui_attr
    out_json = json.dumps(metadata_dic, indent=2)
    with open(path, 'w') as f:
        f.write(out_json)

    return redirect(url_for('dashboard'))

@app.route("/project/<int:project_id>", methods=["POST", "GET"])
@login_required
def project(project_id):
    project_info = Project.query.filter_by(id=project_id).first()
    # Check ownership
    if current_user.id == project_info.user_id:
        # Load metadata .json file
        metadata_path = os.path.join(
            app.root_path, 'user_project', current_user.email, project_info.project_name, 'metadata.json')
        with open(metadata_path, 'r') as f:
            txt = f.read()
        metadata_dic = json.loads(txt)
        # Preparing the data to be displayed
        entity_lis = []
        datastore_lis = []
        process_lis = []
        relation_lis = []
        gui_attr = []
        for key in metadata_dic:
            # Get Entity
            if 'e-' in key:
                id_entity = key
                name_entity = metadata_dic[key]['name']
                out = {'id': id_entity, 'name': name_entity}
                entity_lis.append(out)
            # Get Datastore
            elif 'ds-' in key:
                id_datastore = key
                name_datastore = metadata_dic[key]['name']
                out = {'id': id_datastore, 'name': name_datastore}
                datastore_lis.append(out)
            elif 'pr-' in key:
                id_process = key
                name_process = metadata_dic[key]['name']
                parent_process = metadata_dic[key]['parent']
                if 'gui' in metadata_dic[key]:
                    gui_process = metadata_dic[key]['gui']
                    attr = metadata_dic[key]['gui_attr']
                    out_attr = {
                        'proc_name': name_process,
                        'gui_type': gui_process,
                        'gui_attr': list(enumerate(attr, 1))
                    }
                    gui_attr.append(out_attr)
                else:
                    gui_process = None
                out_process = {'id': id_process, 'name': name_process,
                               'parent': parent_process, 'gui': gui_process}
                process_lis.append(out_process)
            elif 'rl-' in key:
                id_relation = key
                name_relation = metadata_dic[key]['name']
                from_relation = metadata_dic[key]['from']
                to_relation = metadata_dic[key]['to']
                attr_relation = metadata_dic[key]['attr']
                out = {
                    "id": id_relation,
                    "name": name_relation,
                    "from": from_relation,
                    "to": to_relation,
                    "attr": list(enumerate(attr_relation, 1))
                }
                relation_lis.append(out)

        # Enumerating the list to be displayed as table
        entity_lis = list(enumerate(entity_lis, 1))
        datastore_lis = list(enumerate(datastore_lis, 1))
        process_lis = list(enumerate(process_lis, 1))

        return render_template('view_project.html', title="View Project", active_link=activate_link('project-list'), project_info=project_info,
                               entity=entity_lis,
                               datastore=datastore_lis,
                               process=process_lis,
                               relation=relation_lis,
                               gui_attr=gui_attr
                               )
    else:
        return redirect(url_for('dashboard'))

# @app.route("/project/<int:project_id>/edit")
# @login_required
# def project_edit(project_id):
#     return f"<h1>Project id: {project_id} </h1>"

def generate_gui(project_id):
    # Check ownership
    project_info = Project.query.filter_by(id=project_id).first()
    if current_user.id != project_info.user_id:
        return redirect(url_for('dashboard'))
    # Delete existing generated GUI
    from shutil import copytree
    path = os.path.join(app.root_path, 'user_project',current_user.email, project_info.project_name)
    os.chdir(os.path.join(path, 'GUI'))
    for i in os.listdir(os.path.join(path,'GUI')):
        if os.path.isdir(i):
            shutil.rmtree(i)
        else:
            os.remove(i)
    src = os.path.join(app.root_path, 'gui_template', 'assets')
    dst = os.path.join(path, 'GUI', 'assets')
    copytree(src, dst)
    os.chdir(app.root_path)
    # Generate sidebar nav link
    side_bar_link = '''
    <li class="nav-item">
        <a href="{link}.html" class="nav-link">
            {process_name}
        </a>
    </li>
    '''
    # get metadata
    with open(os.path.join(path,'metadata.json'), 'r') as f:
        txt = f.read()
    json_dic = json.loads(txt)
    sidebar = []
    # get html template
    html_output = {}
    with open(os.path.join(app.root_path, 'gui_template', 'template.html'), 'r') as f:
        html = f.read()
    # get gui process
    process_gui = []
    for i in json_dic:
        if 'pr-' in i and 'gui' in json_dic[i]:
            process_gui.append(json_dic[i])
    # add sidebar template
    for i in process_gui:
        proc_name = i['name']
        link = proc_name.replace(' ', '')
        sidebar.append(side_bar_link.format(link=link, process_name=proc_name))
    html = html.format(sidebar=''.join(sidebar), project_name='Test 1', process_name='{process_name}', gui_type='{gui_type}', content='{content}')
    # Generate html page for every process gui
    for i in process_gui:
        link = f"{i['name'].replace(' ','')}.html"
        path = os.path.join(app.root_path, 'project_output sample', link)
        temp_template = html.format(process_name=i['name'], gui_type= gui_type_name_tranf(i['gui']), content='{content}')
        html_output[i['name']] = temp_template
    # Generate Content
    for i in process_gui:
        if i['gui'] == 'master_data':
            content = create_md_template(i['gui_attr'])
            html_output[i['name']] = html_output[i['name']].format(content=content)
        elif i['gui'] == 'grid':
            content = create_grid_template(i['gui_attr'])
            html_output[i['name']] = html_output[i['name']].format(content=content)
        elif i['gui'] == 'input':
            content = create_input_template(i['gui_attr'])
            html_output[i['name']] = html_output[i['name']].format(content=content)
    # Write to HTML
    for name, html in html_output.items():
        path = os.path.join(app.root_path, 'user_project',current_user.email, project_info.project_name, 'GUI', '{}.html'.format(name))
        with open(path, 'w') as f:
            f.write(html)

@app.route('/download-gui/<int:project_id>')
@login_required
def download_gui(project_id):
    # Get project info
    project_info = Project.query.filter_by(id=project_id).first()
    # Generate HTML
    generate_gui(project_id)
    # Delete existing .zip file if available
    os.chdir(os.path.join(app.root_path, 'user_project', current_user.email, project_info.project_name))
    if 'GUI.zip' in os.listdir():
        os.remove('GUI.zip')
    # Make archive .zip
    from shutil import make_archive
    make_archive('GUI', 'zip', root_dir=os.path.join(os.getcwd(), 'GUI'))
    return send_from_directory(directory=os.getcwd(), filename='GUI.zip', as_attachment=True)
    # return os.getcwd()
    

@app.route('/test')
def test():
    return send_from_directory(directory=app.root_path, filename='test.json', as_attachment=True)

@app.route("/fuck-this-shit")
def fuck_this_shit():
    user_project = os.path.join(app.root_path, 'user_project')
    folder = user_project
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

    db.drop_all()
    db.create_all()
    return redirect(url_for('logout'))

@app.route("/logout")
def logout():
    logout_user()
    os.chdir(app.root_path)
    return redirect(url_for('login'))

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

def get_rel_input_data(input_dic):
    rel_input_key = []
    en_ds_key = []
    pr_low_key = get_lowest(input_dic)

    for key in input_dic:
        if 'e-' in key or 'ds-' in key:
            en_ds_key.append(key)

    rel_input_key.extend(en_ds_key)
    rel_input_key.extend(pr_low_key)

    rel_input_dic = {'entity': [], 'datastore': [], 'process': []}

    for key in rel_input_key:
        type_obj = None
        if 'pr-' in key:
            type_obj = 'process'
        elif 'ds-' in key:
            type_obj = 'datastore'
        else:
            type_obj = 'entity'

        temp = {
            'name': input_dic[key]['name'],
            'id': key
        }
        rel_input_dic[type_obj].append(temp)

    return rel_input_dic

def gui_type_name_tranf(name):
    if name == 'master_data':
        return 'Master Data'
    elif name == 'grid':
        return 'Grid'
    elif name == 'input':
        return 'Input'

def create_md_template(attr):
    # Get Template file
    template_path = os.path.join(app.root_path, 'gui_template', 'master-data-content.html')
    with open(template_path, 'r') as f:
        html = f.read()
    # output template
    head_template = '''
    <th>{column_name}</th>
    '''
    body_template = '''
    <td>{data}</td>
    '''
    # Writing to HTML template
    out_head = ''
    out_body = ''

    for i in attr:
        out_head += head_template.format(column_name="{name} ({type})".format(name=i['attr_name'], type=i['attr_type']))
        out_body += body_template.format(data=sample_data[i['attr_type']])

    html = html.format(column_name=out_head, blank_table=out_body)

    return html

def create_grid_template(attr):
    # Get Template file
    template_path = os.path.join(app.root_path, 'gui_template', 'grid-data-content.html')
    with open(template_path, 'r') as f:
        html = f.read()
    # Split into 2 section
    n_data = len(attr)//2
    remainder = len(attr) % 2
    middle_section = n_data + remainder
    left_section = attr[:middle_section]
    right_section = attr[middle_section:]
    # section template
    section_template = '''
    <tr>
        <td>
            <h4 class="font-weight-light">{key}</h4>
        </td>
        <td class="pl-2 pr-3">
            <h4>:</h4>
        </td>
        <td>
            <h4>{value}</h4>
        </td>
    </tr>
    ''' 
    # add left section data
    left_content = ''
    for i in left_section:
        key = '{name} ({attr_type})'.format(name=i['attr_name'], attr_type=i['attr_type'])
        value = sample_data[i['attr_type']]
        left_content += section_template.format(key=key, value=value)
    # add right section data
    right_content = ''
    for i in right_section:
        key = '{name} ({attr_type})'.format(name=i['attr_name'], attr_type=i['attr_type'])
        value = sample_data[i['attr_type']]
        right_content += section_template.format(key=key, value=value)
    # Fill data
    html_output = html.format(left_section=left_content, right_section=right_content)
    return html_output

def create_input_template(attr):
    # Get Template
    template_path = os.path.join(app.root_path, 'gui_template', 'input-data-content.html')
    with open(template_path, 'r') as f:
        html = f.read()
    # Input type template
    input_type_template = {
        'text': '''
        <div class="form-group">
            <label class="col-form-label">{attr_name} ({attr_type})</label>
            <input type="text" class="form-control">
        </div>
        ''',
        'password':'''
        <div class="form-group">
            <label>{attr_name} ({attr_type})</label>
            <input type="password" placeholder="Password" class="form-control">
        </div>
        ''',
        'date':'''
        <div class="form-group">
            <label>{attr_name} ({attr_type})</label>
            <div class="form-group">
                <div class="input-group date" id="{id_attr}" data-target-input="nearest">
                    <input type="text" class="form-control datetimepicker-input" data-target="#{id_attr}">
                    <div class="input-group-append" data-target="#{id_attr}" data-toggle="datetimepicker">
                        <div class="input-group-text"><i class="far fa-calendar-alt"></i></div>
                    </div>
                </div>
            </div>
        </div>
        ''',
        'radio':'''
        <div class="form-group">
            <label>{attr_name} ({attr_type})</label>
            <div>
                <label class="custom-control custom-radio custom-control-inline">
                    <input type="radio" name="{attr_name}" checked="" class="custom-control-input"><span
                        class="custom-control-label">Option 1</span>
                </label>
                <label class="custom-control custom-radio custom-control-inline">
                    <input type="radio" name="{attr_name}" class="custom-control-input"><span
                        class="custom-control-label">Option 2</span>
                </label>
                <label class="custom-control custom-radio custom-control-inline">
                    <input type="radio" name="{attr_name}" class="custom-control-input"><span
                        class="custom-control-label">Option 3</span>
                </label>
            </div>
            <div>
                <label class="custom-control custom-radio custom-control-inline">
                    <input type="radio" name="{attr_name}" checked="" class="custom-control-input"><span
                        class="custom-control-label">Option 4</span>
                </label>
                <label class="custom-control custom-radio custom-control-inline">
                    <input type="radio" name="{attr_name}" class="custom-control-input"><span
                        class="custom-control-label">Option 5</span>
                </label>
            </div>
        </div>
        ''',
        'checkbox':'''
        <div class="form-group">
            <label>{attr_name} ({attr_type})</label>
            <div>
                <label class="custom-control custom-checkbox custom-control-inline">
                    <input type="checkbox" checked="" class="custom-control-input"><span class="custom-control-label">Option
                        1</span>
                </label>
                <label class="custom-control custom-checkbox custom-control-inline">
                    <input type="checkbox" class="custom-control-input"><span class="custom-control-label">Option 2</span>
                </label>
                <label class="custom-control custom-checkbox custom-control-inline">
                    <input type="checkbox" class="custom-control-input"><span class="custom-control-label">Option 3</span>
                </label>
            </div>
            <div>
                <label class="custom-control custom-checkbox custom-control-inline">
                    <input type="checkbox" checked="" class="custom-control-input"><span class="custom-control-label">Option
                        4</span>
                </label>
                <label class="custom-control custom-checkbox custom-control-inline">
                    <input type="checkbox" class="custom-control-input"><span class="custom-control-label">Option 5</span>
                </label>
            </div>
        </div>
        ''',
        'number':'''
        <div class="form-group">
            <label class="col-form-label">{attr_name} ({attr_type})</label>
            <input type="number" class="form-control" placeholder="Numbers">
        </div>            
        ''',
        'select':'''
        <div class="form-group">
            <label for="input-select">{attr_name} ({attr_type})</label>
            <select class="form-control">
                <option>Option 1</option>
                <option>Option 2</option>
                <option>Option 3</option>
            </select>
        </div>
        '''
    }
    script_template = '''
    jQuery(document).ready(function($) {
    'use strict';
        %s
    });
    '''
    # Add data
    form_output = ''
    script_output = ''
    script_if = ''
    for i in attr:
        attr_type = i['attr_type']
        attr_name = i['attr_name']
        if attr_type != 'date':
            form_output += input_type_template[attr_type].format(attr_name=attr_name, attr_type=attr_type)
        else:
            id_attr = attr_name.replace(' ','-')
            script = "if ($('%s').length) { $('#%s').datepicker({ format: 'L'});}" % (id_attr, id_attr)
            script_if += script
            print('\n'*5, script, '\n'*5)
            form_output += input_type_template[attr_type].format(attr_name=attr_name, attr_type=attr_type, id_attr=id_attr)
    # render to template
    script_output += script_template % (script_if)
    html_out = html.format(form=form_output, script=script_output)
    return html_out