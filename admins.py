import json
import os
import errno

path = 'cogs/data/'
admins_config_file = 'admins.json'


class MaxTasksReachedException(Exception):
    pass


class DeltaSmallerThanOne(Exception):
    pass


# Read admins.json file and return admins IDs
def read_admins_ids(guild_id):
    admins_id_json = []
    admins_id = []
    file_path = path + str(guild_id) + '/' + admins_config_file
    try:
        with open(file_path, 'r') as admins_roles:
            admins_id_json = json.load(admins_roles)
            print(admins_id_json)
            admins_roles.close()
        admins_id = [admin_id['admin_role_id'] for admin_id in admins_id_json]
    except FileNotFoundError:
        print('File does not exist or was not found, creating it.')
        if not os.path.exists(os.path.dirname(file_path)):
            try:
                os.makedirs(os.path.dirname(file_path))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        with open(file_path, 'w') as admins_roles:
            json.dump(admins_id, admins_roles, indent=4)
            admins_roles.close()
    return admins_id


# Read the tasks.json file for the specified guild
def read_admins(guild_id):
    admins = []
    file_path = path + str(guild_id) + '/' + admins_config_file
    try:
        with open(file_path, 'r') as admin_file:
            admins = json.load(admin_file)
            admin_file.close()
    except FileNotFoundError:
        print('File does not exist or was not found, creating it.')
        if not os.path.exists(os.path.dirname(file_path)):
            try:
                os.makedirs(os.path.dirname(file_path))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        with open(file_path, 'w') as admin_file:
            json.dump(admins, admin_file, indent=4)
            admin_file.close()
    return admins


# Write task in tasks.json
def write_admins(guild_id, admins_data):
    file_path = path + str(guild_id) + '/' + admins_config_file
    if not os.path.exists(os.path.dirname(file_path)):
        try:
            os.makedirs(os.path.dirname(file_path))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    with open(file_path, 'w') as admin_file:
        json.dump(admins_data, admin_file, indent=4)
        admin_file.close()


def read_guilds_ids():
    directories = [dir_name for dir_name in os.listdir('./cogs/data/') if os.path.isdir(os.path.join('./cogs/data/',
                                                                                                     dir_name))]
    return directories
