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
        perm_data = {
            'idPermission': str(uuid.uuid4()),
            'name': 'Full Access',
            'endpoints': [
                {'path': '/api/machines/*', 'host': '*', 'method': 'GET'},
                {'path': '/api/machines/*', 'host': '*', 'method': 'POST'},
                {'path': '/api/machines/*', 'host': '*', 'method': 'DELETE'},
                {'path': '/api/machines/*', 'host': '*', 'method': 'PUT'},
                {'path': '/api/machines/*', 'host': '*', 'method': 'PATCH'},
                {'path': '/api/channels/*', 'host': '*', 'method': 'GET'},
                {'path': '/api/channels/*', 'host': '*', 'method': 'POST'},
                {'path': '/api/channels/*', 'host': '*', 'method': 'DELETE'},
                {'path': '/api/channels/*', 'host': '*', 'method': 'PUT'},
                {'path': '/api/channels/*', 'host': '*', 'method': 'PATCH'},
                {'path': '/api/data/*', 'host': '*', 'method': 'GET'},
                {'path': '/api/data/*', 'host': '*', 'method': 'POST'},
                {'path': '/api/data/*', 'host': '*', 'method': 'DELETE'},
                {'path': '/api/data/*', 'host': '*', 'method': 'PUT'},
                {'path': '/api/data/*', 'host': '*', 'method': 'PATCH'},
                {'path': '/api/token/', 'host': '*', 'method': 'POST'},
                {'path': '/api/data/ingest/', 'host': '*', 'method': 'POST'},
            ],
            'components': ['admin_panel', 'dashboard', 'settings']
        }
        
        db.core_permission.replace_one(
            {'name': perm_data['name']},
            perm_data,
            upsert=True
        )
        perm = db.core_permission.find_one({'name': perm_data['name']})
        self.stdout.write(f'Permission "{perm["name"]}" updated/synchronized.')

        # 3.2 Role
        role_data = {
            'idRole': str(uuid.uuid4()),
            'name': 'SuperAdmin'
        }
        role = db.core_role.find_one({'name': role_data['name']})
        if not role:
            db.core_role.insert_one(role_data)
            role = role_data
            self.stdout.write(f'Role "{role["name"]}" created.')
        else:
            self.stdout.write(f'Role "{role["name"]}" already exists.')

        # 3.3 Role-Permission Relationship (M2M table)
        if not db.core_role_permissions.find_one({'role_id': role['idRole'], 'permission_id': perm['idPermission']}):
            db.core_role_permissions.insert_one({
                'id': int(uuid.uuid4().int >> 96),
                'role_id': role['idRole'],
                'permission_id': perm['idPermission']
            })
            self.stdout.write('Relation Role-Permission linked.')

        # 3.4 UserRole (Mapping User to Role)
        if not db.core_userrole.find_one({'user_id': user.id, 'role_id': role['idRole']}):
            db.core_userrole.insert_one({
                'idUserRole': str(uuid.uuid4()),
                'user_id': user.id,
                'role_id': role['idRole']
            })
            self.stdout.write('User assigned to SuperAdmin role.')

        # 3.5 Machine
        machine_data = {
            'machineId': str(uuid.uuid4()),
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

        # 3.6 Channel
        channel_data = {
            'idChannel': str(uuid.uuid4()),
            'name': 'Hydraulic Pressure'
        }
        channel = db.core_channel.find_one({'name': channel_data['name']})
        if not channel:
            db.core_channel.insert_one(channel_data)
            channel = channel_data
            self.stdout.write(f'Channel "{channel["name"]}" created.')
        else:
            self.stdout.write(f'Channel "{channel["name"]}" already exists.')

        # 3.7 Data
        data_sample = {
            'idData': str(uuid.uuid4()),
            'dataId': 'D_SEED_001',
            'frequency': 2.5,
            'value': 120.0,
            'type': 'float',
            'serial_machine': machine['serial'],
            'machineId_id': machine['machineId'],
            'channelId_id': channel['idChannel']
        }
        if not db.core_data.find_one({'dataId': data_sample['dataId']}):
            db.core_data.insert_one(data_sample)
            self.stdout.write(f'Data sample "{data_sample["dataId"]}" created.')

        # 3.8 Business
        if not db.core_business.find_one({'user_id': user.id, 'machine_id': machine['machineId']}):
            db.core_business.insert_one({
                'idBusiness': str(uuid.uuid4()),
                'user_id': user.id,
                'machine_id': machine['machineId']
            })
            self.stdout.write('Business relation created.')

        client.close()
        self.stdout.write(self.style.SUCCESS('Database seeded successfully via direct PyMongo.'))
