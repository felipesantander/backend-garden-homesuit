import os
import uuid
import logging
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from pymongo import MongoClient

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Seed the database with initial test data using PyMongo for stability'

    def handle(self, *_args, **_kwargs):
        self.stdout.write('Seeding database using direct PyMongo access...')

        # 1. MongoDB Connection Setup
        db_url = os.environ.get('DATABASE_URL', 'mongodb://root:example@192.168.1.134:27017/')
        
        # Ensure authSource=admin is present if we have credentials
        if 'root' in db_url and 'authSource' not in db_url:
            if '?' in db_url:
                db_url += '&authSource=admin'
            else:
                db_url += '?authSource=admin'

        db_name = 'garden_db'
        client = MongoClient(db_url)
        db = client[db_name]

        # 2. Create SuperUser (Using Django Auth for password hashing)
        try:
            user = User.objects.get(username='admin')
            self.stdout.write(f'User "admin" already exists (ID: {user.id}).')
        except User.DoesNotExist:
            user = User.objects.create(
                username='admin',
                email='admin@example.com',
                is_staff=True,
                is_superuser=True
            )
            user.set_password('admin123')
            user.save()
            self.stdout.write(self.style.SUCCESS(f'User "admin" created (ID: {user.id}).'))

        # 3.1 Permission
        perm_uuid = uuid.uuid4()
        perm_data = {
            'idPermission': perm_uuid,
            'name': 'Full Access',
            'endpoints': [
                {'path': '/api/*', 'host': '*', 'method': '*'},
            ],
            'machines': ["9405bfd9-75e0-4688-8cc3-353450a32944"],
            'components': [
                'dashboard',
                'dashboard_filter_by_business',
                'dashboard_filter_by_garden',
                'dashboard_add_machine',
                'dashboard_see_machine',
                'dashboard_config_machine',
                'dashboard_delete_machine',
                'machine_candidates',
                'channels',
                'channels_add',
                'channels_see',
                'channels_config',
                'channels_delete',
                'gardens',
                'gardens_add',
                'gardens_see',
                'gardens_config',
                'gardens_delete',
                'users',
                'users_add',
                'users_see',
                'users_config',
                'users_delete',
                'businesses',
                'businesses_add',
                'businesses_see',
                'businesses_config',
                'businesses_delete',
                'alerts',
                'alerts_add',
                'alerts_see',
                'alerts_config',
                'alerts_delete',
                'roles_permissions',
                'roles_permissions_add',
                'roles_permissions_see',
                'roles_permissions_config',
                'roles_permissions_delete',
            ]
        }
        
        db.core_permission.replace_one(
            {'name': perm_data['name']},
            perm_data,
            upsert=True
        )
        perm = db.core_permission.find_one({'name': perm_data['name']})
        perm_id = perm['idPermission']
        self.stdout.write(f'Permission "{perm["name"]}" updated/synchronized.')

        # 3.1.b View Machine Permission
        view_machine_data = {
            'idPermission': uuid.uuid4(),
            'name': 'View Machine',
            'endpoints': [{'path': '/api/machines/*', 'host': '*', 'method': 'GET'}],
            'components': ['dashboard_see_machine', 'machine_candidates']
        }
        db.core_permission.replace_one({'name': view_machine_data['name']}, view_machine_data, upsert=True)
        self.stdout.write('Permission "View Machine" updated/synchronized.')

        # 3.1.c Edit Machine Permission
        edit_machine_data = {
            'idPermission': uuid.uuid4(),
            'name': 'Edit Machine',
            'endpoints': [
                {'path': '/api/machines/*', 'host': '*', 'method': 'PUT'},
                {'path': '/api/machines/*', 'host': '*', 'method': 'PATCH'}
            ],
            'components': ['dashboard_config_machine']
        }
        db.core_permission.replace_one({'name': edit_machine_data['name']}, edit_machine_data, upsert=True)
        self.stdout.write('Permission "Edit Machine" updated/synchronized.')

        # 3.1.d Create and Delete Machine Permission
        create_delete_machine_data = {
            'idPermission': uuid.uuid4(),
            'name': 'Create and Delete Machine',
            'endpoints': [
                {'path': '/api/machines/*', 'host': '*', 'method': 'POST'},
                {'path': '/api/machines/*', 'host': '*', 'method': 'DELETE'}
            ],
            'components': ['dashboard_add_machine', 'dashboard_delete_machine']
        }
        db.core_permission.replace_one({'name': create_delete_machine_data['name']}, create_delete_machine_data, upsert=True)
        self.stdout.write('Permission "Create and Delete Machine" updated/synchronized.')

        # 3.1.e Channels Permissions
        db.core_permission.replace_one({'name': 'View Channel'}, {
            'idPermission': uuid.uuid4(),
            'name': 'View Channel',
            'endpoints': [{'path': '/api/channels/*', 'host': '*', 'method': 'GET'}],
            'components': ['channels', 'channels_see']
        }, upsert=True)
        db.core_permission.replace_one({'name': 'Edit Channel'}, {
            'idPermission': uuid.uuid4(),
            'name': 'Edit Channel',
            'endpoints': [
                {'path': '/api/channels/*', 'host': '*', 'method': 'PUT'},
                {'path': '/api/channels/*', 'host': '*', 'method': 'PATCH'}
            ],
            'components': ['channels_config']
        }, upsert=True)
        db.core_permission.replace_one({'name': 'Create and Delete Channel'}, {
            'idPermission': uuid.uuid4(),
            'name': 'Create and Delete Channel',
            'endpoints': [
                {'path': '/api/channels/*', 'host': '*', 'method': 'POST'},
                {'path': '/api/channels/*', 'host': '*', 'method': 'DELETE'}
            ],
            'components': ['channels_add', 'channels_delete']
        }, upsert=True)
        self.stdout.write('Permissions for Channels updated/synchronized.')

        # 3.1.f Data Permissions
        db.core_permission.replace_one({'name': 'View Data'}, {
            'idPermission': uuid.uuid4(),
            'name': 'View Data',
            'endpoints': [
                {'path': '/api/data/*', 'host': '*', 'method': 'GET'},
                {'path': '/api/data/latest/*', 'host': '*', 'method': 'GET'},
                {'path': '/api/data/query/*', 'host': '*', 'method': 'GET'}
            ],
            'components': ['dashboard']
        }, upsert=True)
        db.core_permission.replace_one({'name': 'Edit Data'}, {
            'idPermission': uuid.uuid4(),
            'name': 'Edit Data',
            'endpoints': [
                {'path': '/api/data/*', 'host': '*', 'method': 'PUT'},
                {'path': '/api/data/*', 'host': '*', 'method': 'PATCH'}
            ],
            'components': []
        }, upsert=True)
        db.core_permission.replace_one({'name': 'Create and Delete Data'}, {
            'idPermission': uuid.uuid4(),
            'name': 'Create and Delete Data',
            'endpoints': [
                {'path': '/api/data/*', 'host': '*', 'method': 'POST'},
                {'path': '/api/data/*', 'host': '*', 'method': 'DELETE'}
            ],
            'components': []
        }, upsert=True)
        self.stdout.write('Permissions for Data updated/synchronized.')

        # 3.1.g Gardens Permissions
        db.core_permission.replace_one({'name': 'View Garden'}, {
            'idPermission': uuid.uuid4(),
            'name': 'View Garden',
            'endpoints': [{'path': '/api/gardens/*', 'host': '*', 'method': 'GET'}],
            'components': ['gardens', 'gardens_see']
        }, upsert=True)
        db.core_permission.replace_one({'name': 'Edit Garden'}, {
            'idPermission': uuid.uuid4(),
            'name': 'Edit Garden',
            'endpoints': [
                {'path': '/api/gardens/*', 'host': '*', 'method': 'PUT'},
                {'path': '/api/gardens/*', 'host': '*', 'method': 'PATCH'}
            ],
            'components': ['gardens_config']
        }, upsert=True)
        db.core_permission.replace_one({'name': 'Create and Delete Garden'}, {
            'idPermission': uuid.uuid4(),
            'name': 'Create and Delete Garden',
            'endpoints': [
                {'path': '/api/gardens/*', 'host': '*', 'method': 'POST'},
                {'path': '/api/gardens/*', 'host': '*', 'method': 'DELETE'}
            ],
            'components': ['gardens_add', 'gardens_delete']
        }, upsert=True)
        self.stdout.write('Permissions for Gardens updated/synchronized.')

        # 3.1.h Alerts Permissions
        alert_endpoints = ['/api/alerts/*', '/api/alert-states/*', '/api/alert-histories/*']
        db.core_permission.replace_one({'name': 'View Alert'}, {
            'idPermission': uuid.uuid4(),
            'name': 'View Alert',
            'endpoints': [{'path': ep, 'host': '*', 'method': 'GET'} for ep in alert_endpoints],
            'components': ['alerts', 'alerts_see']
        }, upsert=True)
        db.core_permission.replace_one({'name': 'Edit Alert'}, {
            'idPermission': uuid.uuid4(),
            'name': 'Edit Alert',
            'endpoints': [
                {'path': ep, 'host': '*', 'method': 'PUT'} for ep in alert_endpoints
            ] + [
                {'path': ep, 'host': '*', 'method': 'PATCH'} for ep in alert_endpoints
            ],
            'components': ['alerts_config']
        }, upsert=True)
        db.core_permission.replace_one({'name': 'Create and Delete Alert'}, {
            'idPermission': uuid.uuid4(),
            'name': 'Create and Delete Alert',
            'endpoints': [
                {'path': ep, 'host': '*', 'method': 'POST'} for ep in alert_endpoints
            ] + [
                {'path': ep, 'host': '*', 'method': 'DELETE'} for ep in alert_endpoints
            ],
            'components': ['alerts_add', 'alerts_delete']
        }, upsert=True)
        self.stdout.write('Permissions for Alerts (Alert, State, History) updated/synchronized.')

        # 3.2 Role
        role_data = {
            'idRole': uuid.uuid4(),
            'name': 'SuperAdmin'
        }
        role = db.core_role.find_one({'name': role_data['name']})
        if not role:
            db.core_role.insert_one(role_data)
            role = role_data
            self.stdout.write(f'Role "{role["name"]}" created.')
        else:
            self.stdout.write(f'Role "{role["name"]}" already exists.')
        
        role_id = role['idRole']

        # 3.3 Role-Permission Relationship (M2M table)
        if not db.core_role_permissions.find_one({'role_id': role_id, 'permission_id': perm_id}):
            db.core_role_permissions.insert_one({
                'id': int(uuid.uuid4().int >> 96),
                'role_id': role_id,
                'permission_id': perm_id
            })
            self.stdout.write('Relation Role-Permission linked.')

        # 3.4 UserRole (Mapping User to Role)
        if not db.core_userrole.find_one({'user_id': user.id, 'role_id': role_id}):
            db.core_userrole.insert_one({
                'idUserRole': uuid.uuid4(),
                'user_id': user.id,
                'role_id': role_id
            })
            self.stdout.write('User assigned to SuperAdmin role.')

        # 3.5 Machine
        machine_uuid = uuid.uuid4()
        machine_data = {
            'machineId': machine_uuid,
            'serial': 'SN010',
            'Name': 'Engine Monitor 10'
        }
        machine = db.core_machine.find_one({'serial': machine_data['serial']})
        if not machine:
            db.core_machine.insert_one(machine_data)
            machine = machine_data
            self.stdout.write(f'Machine "{machine["serial"]}" created.')
        else:
            self.stdout.write(f'Machine "{machine["serial"]}" already exists.')
        
        machine_id = machine['machineId']

        channel_uuid = uuid.uuid4()
        channel_data = {
            'idChannel': channel_uuid,
            'name': 'Hydraulic Pressure',
            'unit': 'V',
            'color': '#3498db',
            'icon': 'water-outline',
        }
        db.core_channel.replace_one(
            {'name': channel_data['name']},
            channel_data,
            upsert=True
        )
        channel = db.core_channel.find_one({'name': channel_data['name']})
        channel_id = channel['idChannel']
        self.stdout.write(f'Channel "{channel["name"]}" updated/synchronized.')

        # 3.7 Data
        data_sample = {
            'idData': uuid.uuid4(),
            'dataId': 'D_SEED_001',
            'frequency': 2.5,
            'value': 120.0,
            'type': 'float',
            'serial_machine': machine['serial'],
            'machineId_id': machine_id,
            'channelId_id': channel_id
        }
        if not db.core_data.find_one({'dataId': data_sample['dataId']}):
            db.core_data.insert_one(data_sample)
            self.stdout.write(f'Data sample "{data_sample["dataId"]}" created.')

        # 3.8 Business
        if not db.core_business.find_one({'user_id': user.id, 'machine_id': machine_id}):
            db.core_business.insert_one({
                'idBusiness': uuid.uuid4(),
                'user_id': user.id,
                'machine_id': machine_id
            })
            self.stdout.write('Business relation created.')

        client.close()
        self.stdout.write(self.style.SUCCESS('Database seeded successfully via direct PyMongo.'))
