import ckan.plugins.toolkit as toolkit
import ckan.logic as logic
import ckan.model as model
from ckan.common import _, c
import ckan.lib.helpers as h
import json
import os
import logging
import ckan.lib.dictization.model_dictize as model_dictize

from ckanext.doat.model.opend import OpendModel
import requests
from datetime import datetime as dt
from six import text_type

import ckan.plugins as p
from ckan.common import request

get_action = logic.get_action
opend_model = OpendModel()

def doat_hello():
    return "Hello, doat!"


def get_helpers():
    return {
        "doat_hello": doat_hello,
    }


log = logging.getLogger(__name__)

def get_user_display_name(user):
    if not isinstance(user, model.User):
        user_name = text_type(user)
        user = model.User.get(user_name)
        if not user:
            return user_name
    if user:
        displayname = user.display_name
    return displayname

def dataset_bulk_import_log(import_id):
    logs = opend_model.get_dataset_bulk_import_log(import_id)
    return logs

def dataset_bulk_import_status(import_id):
    try:
        context = {'model': model,
                    'user': c.user, 'auth_user_obj': c.userobj}

        like_q1 = u'%' + import_id + u'%'
        like_q2 = u'%Finished%'

        q = model.Session.query(model.Activity).filter(model.Activity.activity_type == 'changed user').filter(model.Activity.data.ilike(like_q1)).filter(model.Activity.data.ilike(like_q2))
        activities = q.all()
    except:
        return []

    return model_dictize.activity_list_dictize(
        activities, context,
        include_data=True)

def dataset_bulk_import_count(log_contents):
    complete = 0
    for log_item in log_contents:
        complete = complete + log_item['log_content'].count('package_create')
    return complete

def get_group_color(group_id):

    first_char = group_id[0]

    color = {
        '0': 'firebrick',
        '1': 'darkorange',
        '2': 'darkkhaki',
        '3': 'olivedrab',
        '4': 'teal',
        '5': 'royalblue',
        '6': 'slateblue',
        '7': 'purple',
        '8': 'mediumvioletred',
        '9': 'darkslategray',
        'a': 'saddlebrown',
        'b': 'green',
        'c': 'firebrick',
        'd': 'darkorange',
        'e': 'darkkhaki',
        'f': 'olivedrab',
        'g': 'teal',
        'h': 'royalblue',
        'i': 'slateblue',
        'j': 'purple',
        'k': 'mediumvioletred',
        'l': 'darkslategray',
        'm': 'saddlebrown',
        'n': 'green',
        'o': 'firebrick',
        'p': 'darkorange',
        'q': 'darkkhaki',
        'r': 'olivedrab',
        's': 'teal',
        't': 'royalblue',
        'u': 'slateblue',
        'v': 'purple',
        'w': 'mediumvioletred',
        'x': 'darkslategray',
        'y': 'saddlebrown',
        'z': 'green'
    }

    return first_char in color and color[first_char] or 'gray'

def get_site_statistics():
    stats = {}
    stats['dataset_count'] = logic.get_action('package_search')(
        {}, {"rows": 1,"include_private":True})['count']
    query = model.Session.query(model.Group) \
            .filter(model.Group.state == 'active') \
            .filter(model.Group.type != 'organization') \
            .filter(model.Group.type != 'group')
    
    resultproxy = model.Session.execute(query).fetchall()
    stats['group_count'] = len(resultproxy)

    stats['organization_count'] = len(
        logic.get_action('organization_list')({}, {}))
    return stats

def convert_string_todate(str_date, format):
    return dt.strptime(str_date, format)

def get_opend_playground_url():
    return 'https://opend.data.go.th/playground'

def get_catalog_org_type():
    return 'organization'

def get_is_as_a_service():
    return 'false'

def get_gdcatalog_status_show():
    return 'true'

def get_gdcatalog_portal_url():
    return 'https://gdcatalog.go.th'

def get_gdcatalog_apiregister_url():
    return 'https://apiregister.gdcatalog.go.th'

def get_gdcatalog_version_update():
    gdcatalog_harvester_url = 'https://harvester.gdcatalog.go.th'
    request_proxy = 'true'
    if request_proxy:
        proxies = {
            'http': 'http://proxyout.inet.co.th:8080',
            'https': 'http://proxyout.inet.co.th:8080'
        }
    else:
        proxies = None

    state = 'connection error'
    gdcatalog_version = 'gdcatalog'
    local_version = 'local'
    try:
        with requests.Session() as s:
            s.verify = False
            url = gdcatalog_harvester_url+'/base/admin/thai-gdc-update.json'
            headers = {'Content-type': 'application/json', 'Authorization': ''}
            res = s.get(url, headers = headers, proxies=proxies)
            log.info(res.text)
            gdcatalog_version = json.loads(res.text)['version']
            local_version = get_extension_version('version')
        if gdcatalog_version != local_version:
            state = gdcatalog_version
        else:
            state = 'updated'
    except:
        return state
    
    return state

def get_gdcatalog_state(zone, package_id):
    state = []
    gdcatalog_status_show = get_gdcatalog_status_show()
    gdcatalog_harvester_url = 'https://harvester.gdcatalog.go.th'
    site_url = 'https://data.go.th'
    request_proxy = 'true'
    if request_proxy:
        proxies = {
            'http': 'http://proxyout.inet.co.th:8080',
            'https': 'http://proxyout.inet.co.th:8080'
        }
    else:
        proxies = None
    if gdcatalog_status_show == 'true':
        try:
            with requests.Session() as s:
                s.verify = False
                if zone == 'published':
                    url = gdcatalog_harvester_url+'/api/3/action/gdcatalog_published_state'
                elif zone == 'nonpublish':
                    url = gdcatalog_harvester_url+'/api/3/action/gdcatalog_nonpublish_state'
                myobj = {"site_url": site_url.split("//")[1].split("/")[0], "package": package_id}
                myobj['site_url'] = myobj['site_url'].encode('ascii','ignore')
                myobj['package'] = myobj['package'].encode('ascii','ignore')
                log.info(json.dumps(myobj))
                headers = {'Content-type': 'application/json', 'Authorization': ''}
                res = s.post(url, data = json.dumps(myobj), headers = headers, proxies=proxies)
                log.info(res.json())
                state = res.json()
        except:
            return state
    return state

def get_users_non_member():
    users = opend_model.get_users_non_member()
    return [d['id'] for d in users]

def get_users_deleted():
    query = model.Session.query(model.User.name)
    query = query.filter_by(state='deleted')
    users_list = []
    for user in query.all():
        users_list.append(user[0])
    return users_list

def get_extension_version(attr):
    dirname, filename = os.path.split(os.path.abspath(__file__))
    f = open(dirname+'/public/base/admin/thai-gdc-update.json',) 
    data = json.load(f)
    return data[attr]

def get_action(action_name, data_dict=None):
    '''Calls an action function from a template. Deprecated in CKAN 2.3.'''
    if data_dict is None:
        data_dict = {}
    return logic.get_action(action_name)({}, data_dict)

def get_organizations(all_fields=False, include_dataset_count=False, sort="name asc"):
    context = {'user': c.user}
    data_dict = {
        'all_fields': all_fields,
        'include_dataset_count': include_dataset_count,
        'sort': sort}
    return logic.get_action('organization_list')(context, data_dict)


def get_groups(all_fields=False, include_dataset_count=False, sort="name asc"):
    context = {'user': c.user}
    data_dict = {
        'all_fields': all_fields,
        'include_dataset_count': include_dataset_count,
        'sort': sort}
    return logic.get_action('group_list')(context, data_dict)


def get_resource_download(resource_id):
    return opend_model.get_resource_download(resource_id)

def get_stat_all_view():
    num = opend_model.get_all_view()
    return num

def get_last_update_tracking():
    last_update = opend_model.get_last_update_tracking()
    return last_update

def day_thai(t):
    month = [
        _('January'), _('February'), _('March'), _('April'),
        _('May'), _('June'), _('July'), _('August'),
        _('September'), _('October'), _('November'), _('December')
    ]

    raw = str(t)
    tmp = raw.split(' ')
    dte = tmp[0]

    tmp = dte.split('-')
    m_key = int(tmp[1]) - 1

    if h.lang() == 'th':
        dt = u"{} {} {}".format(int(tmp[2]), month[m_key], int(tmp[0]) + 543)
    else:
        dt = u"{} {}, {}".format(month[m_key], int(tmp[2]), int(tmp[0]))

    return dt

def facet_chart(type, limit):
    items = h.get_facet_items_dict(type, limit)
    i = 1
    data = []
    context = {'model': model}
    for item in items:
        my_dict = {column: value for column, value in item.items()}
        item['rownum'] = i
        if type == 'groups':
            group_dict = logic.get_action('group_show')(context, {'id': item['name']})
            item['image_url'] = group_dict['image_url']
        data.append(item)
        i += 1

    return data

def get_recent_view_for_package(package_id):
    rs = model.TrackingSummary.get_for_package(package_id)
    return rs['recent']

def get_featured_pages(per_page):
    pages = opend_model.get_featured_pages(per_page)
    return pages

def get_page(name):
    #if db.pages_table is None:
    #    db.init_db(model)
    page = opend_model.get_page(name)
    return page

def is_user_sysadmin(user=None):
    """Returns True if authenticated user is sysadmim
    :rtype: boolean
    """
    if user is None:
        user = toolkit.c.userobj
    return user is not None and user.sysadmin


def user_has_admin_access(include_editor_access=False):
    user = toolkit.c.userobj
    # If user is "None" - they are not logged in.
    if user is None:
        return False
    if is_user_sysadmin(user):
        return True

    groups_admin = user.get_groups('organization', 'admin')
    groups_editor = user.get_groups('organization', 'editor') if include_editor_access else []
    groups_list = groups_admin + groups_editor
    organisation_list = [g for g in groups_list if g.type == 'organization']
    return len(organisation_list) > 0

def get_all_groups():
    groups = toolkit.get_action('group_list')(
        data_dict={'include_dataset_count': False, 'all_fields': True})
    pkg_group_ids = set(group['id'] for group
                        in c.pkg_dict.get('groups', []))
    return [[group['id'], group['display_name']]
            for group in groups if
            group['id'] not in pkg_group_ids]

def get_all_groups_all_type(type=None):    
    user_groups = opend_model.get_groups_all_type(type)

    pkg_group_ids = set(group['id'] for group
                            in c.pkg_dict.get('groups', []))
    return [[group['id'], group['display_name']]
                            for group in user_groups if
                            group['id'] not in pkg_group_ids]

def users_in_organization(organization_id):
    ''' users in organization '''
    query = model.Session.query(model.Member) \
        .filter(model.Member.state == 'active') \
        .filter(model.Member.table_name == 'user') \
        .filter(model.Member.group_id == organization_id)
    users = query.all()
    context = {'model': model,
                    'user': c.user, 'auth_user_obj': c.userobj}
    users_list = []
    for user in users:
        users_list.append(model_dictize.member_dictize(user, context))
    return users_list

def get_suggest_view(resources):
    suggest_view_list = []
    for rs in resources:
        if rs.get('resource_private','') != "True":
            view_list = toolkit.get_action('resource_view_list')(data_dict={'id': rs['id']})

            for v in view_list:
                v_des = v['description'].strip()

                if len(v_des) > 0 and v_des[0] == '*':
                    suggest_view_list.append({
                        'title': v['title'],
                        'resource_id': v['resource_id'],
                        'view_id': v['id']
                    })

    return suggest_view_list


def get_conf_group(conf_group):
    try:
        conf = toolkit.get_action('gdc_agency_get_conf_group')(data_dict={'conf_group': conf_group})
        if 'EVENT_IMAGE' in conf.keys() and conf['EVENT_IMAGE'].strip() != '' \
                and not conf['EVENT_IMAGE'].startswith('http'):
            conf['EVENT_IMAGE'] = '/uploads/admin/{}'.format(conf['EVENT_IMAGE'])
        return conf
    except:
        return {}

def get_last_modified_datasets(limit):
    try:
        package = model.Package
        q = model.Session.query(package.name, package.title, package.type, package.metadata_modified.label('date_modified')).filter(package.state == 'active').filter(package.private == False).order_by(package.metadata_modified.desc()).limit(limit)
        packages = q.all()
    except:
        return []
    return packages

def get_popular_datasets(limit):
    package_list = []

    result_pkg_list = toolkit.get_action('package_search')(data_dict={'sort': 'views_total desc','rows':limit})
    for item in result_pkg_list['results']:
        tracking_summary = (model.TrackingSummary.get_for_package(item['id']))
        package_list.append({
            'name': item['name'],
            'title': item['title'],
            'type': item['type'],
            'date_modified' : item['metadata_modified'],
            'total_view': tracking_summary['total']})

    return package_list


def group_tree(organizations=[], type_='organization'):
    full_tree_list = toolkit.get_action('group_tree')({}, {'type': type_})

    if not organizations:
        return full_tree_list
    else:
        filtered_tree_list = group_tree_filter(organizations, full_tree_list)
        return filtered_tree_list


def group_tree_filter(organizations, group_tree_list, highlight=False):
    # this method leaves only the sections of the tree corresponding to the
    # list since it was developed for the users, all children organizations
    # from the organizations in the list are included
    def traverse_select_highlighted(group_tree, selection=[], highlight=False):
        # add highlighted branches to the filtered tree
        if group_tree['highlighted']:
            # add to the selection and remove highlighting if necessary
            if highlight:
                selection += [group_tree]
            else:
                selection += group_tree_highlight([], [group_tree])
        else:
            # check if there is any highlighted child tree
            for child in group_tree.get('children', []):
                traverse_select_highlighted(child, selection)

    filtered_tree = []
    # first highlights all the organizations from the list in the three
    for group in group_tree_highlight(organizations, group_tree_list):
        traverse_select_highlighted(group, filtered_tree, highlight)

    return filtered_tree


def group_tree_section(id_, type_='organization', include_parents=True,
                       include_siblings=True):
    return toolkit.get_action('group_tree_section')(
        {'include_parents': include_parents,
         'include_siblings': include_siblings},
        {'id': id_, 'type': type_, })


def _get_action_name(group_id):
    model_obj = model.Group.get(group_id)
    return "organization_show" if model_obj.is_organization else "group_show"


def group_tree_parents(id_):
    action_name = _get_action_name(id_)
    data_dict = {
        'id': id_,
        'include_dataset_count': False,
        'include_users': False,
        'include_followers': False,
        'include_tags': False
    }
    tree_node = toolkit.get_action(action_name)({}, data_dict)
    if (tree_node['groups']):
        parent_id = tree_node['groups'][0]['name']
        parent_node = \
            toolkit.get_action(action_name)({}, {'id': parent_id})
        return group_tree_parents(parent_id) + [parent_node]
    else:
        return []
    
def group_tree_highlight(organizations, group_tree_list):
    def traverse_highlight(group_tree, name_list):
        if group_tree.get('name', "") in name_list:
            group_tree['highlighted'] = True
        else:
            group_tree['highlighted'] = False
        for child in group_tree.get('children', []):
            traverse_highlight(child, name_list)

    selected_names = [o.get('name', None) for o in organizations]

    for group in group_tree_list:
        traverse_highlight(group, selected_names)
    return group_tree_list