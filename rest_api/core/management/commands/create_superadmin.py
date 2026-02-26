import os
import uuid
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from pymongo import MongoClient

class Command(BaseCommand):
    help = 'Create a user with the SuperAdmin role'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username for the new user')
        parser.add_argument('email', type=str, help='Email for the new user')
        parser.add_argument('password', type=str, help='Password for the new user')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

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

        # 2. Create/Get User
        try:
            user = User.objects.get(username=username)
            self.stdout.write(f'User "{username}" already exists (ID: {user.id}). Updating password...')
            user.set_password(password)
            user.save()
        except User.DoesNotExist:
            user = User.objects.create(
                username=username,
                email=email,
                is_staff=True,
                is_superuser=True
            )
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'User "{username}" created (ID: {user.id}).'))

        # 3. Ensure SuperAdmin Role exists
        role_name = 'SuperAdmin'
        role = db.core_role.find_one({'name': role_name})
        
        if not role:
            role_id = uuid.uuid4()
            role_data = {
                'idRole': role_id,
                'name': role_name
            }
            db.core_role.insert_one(role_data)
            role = role_data
            self.stdout.write(f'Role "{role_name}" created.')
        else:
            role_id = role['idRole']
            self.stdout.write(f'Role "{role_name}" found.')

        # 4. Ensure Full Access Permission exists
        perm_name = 'Full Access'
        perm = db.core_permission.find_one({'name': perm_name})
        if not perm:
            perm_id = uuid.uuid4()
            perm_data = {
                'idPermission': perm_id,
                'name': perm_name,
                'endpoints': [{'path': '/api/*', 'host': '*', 'method': '*'}],
                'gardens': [],
                'businesses': [],
                'machines': [],
                'channels': [],
                'components': ['admin_panel', 'dashboard', 'settings']
            }
            db.core_permission.insert_one(perm_data)
            perm = perm_data
            self.stdout.write(f'Permission "{perm_name}" created.')
        else:
            perm_id = perm['idPermission']
            self.stdout.write(f'Permission "{perm_name}" found.')

        # 5. Link Role and Permission
        if not db.core_role_permissions.find_one({'role_id': role_id, 'permission_id': perm_id}):
            db.core_role_permissions.insert_one({
                'id': int(uuid.uuid4().int >> 96),
                'role_id': role_id,
                'permission_id': perm_id
            })
            self.stdout.write('Relation Role-Permission linked.')

        # 6. Assign Role to User (UserRole mapping)
        user_role_exists = db.core_userrole.find_one({'user_id': user.id, 'role_id': role_id})
        
        if not user_role_exists:
            db.core_userrole.insert_one({
                'idUserRole': uuid.uuid4(),
                'user_id': user.id,
                'role_id': role_id
            })
            self.stdout.write(self.style.SUCCESS(f'User "{username}" assigned to "{role_name}" role.'))
        else:
            self.stdout.write(f'User "{username}" already has the "{role_name}" role.')

        client.close()
        self.stdout.write(self.style.SUCCESS(f'Successfully ensured user "{username}" is a SuperAdmin.'))
