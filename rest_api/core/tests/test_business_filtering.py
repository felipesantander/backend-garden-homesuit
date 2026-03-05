import pytest
import uuid
from django.contrib.auth.models import User
from core.models import Business, Garden, Machine, Channel, Role, Permission, UserRole
from rest_framework.test import APIClient

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def setup_data(db):
    # Create Businesses
    b1 = Business.objects.create(name="Business 1")
    b2 = Business.objects.create(name="Business 2")
    
    # Create Gardens
    g1 = Garden.objects.create(name="Garden B1", business=b1)
    g2 = Garden.objects.create(name="Garden B2", business=b2)
    
    # Create Machines
    m1 = Machine.objects.create(Name="Machine B1", garden=g1, serial="SNB1")
    m2 = Machine.objects.create(Name="Machine B2", garden=g2, serial="SNB2")
    
    # Create Channels
    c1 = Channel.objects.create(name="Channel B1", business=b1)
    c2 = Channel.objects.create(name="Channel B2", business=b2)
    
    # Create User
    user = User.objects.create_user(username="testuser", password="password")
    
    # Create Permission for B1 only
    perm = Permission.objects.create(
        name="B1 Access",
        businesses=[str(b1.idBusiness)],
        endpoints=[{"path": "/api/*", "host": "*", "method": "*"}]
    )
    
    # Create Role and assign to User
    role = Role.objects.create(name="B1 Manager")
    role.permissions.add(perm)
    UserRole.objects.create(user=user, role=role)
    
    return {
        "user": user,
        "b1": b1,
        "b2": b2,
        "g1": g1,
        "g2": g2,
        "m1": m1,
        "m2": m2,
        "c1": c1,
        "c2": c2
    }

@pytest.mark.django_db
class TestBusinessFiltering:
    def test_filter_garden(self, api_client, setup_data):
        user = setup_data["user"]
        api_client.force_authenticate(user=user)
        
        url = "/api/gardens/"
        res = api_client.get(url)
        assert res.status_code == 200
        
        # Should only see Garden from B1
        ids = [item["idGarden"] for item in res.data]
        assert str(setup_data["g1"].idGarden) in ids
        assert str(setup_data["g2"].idGarden) not in ids

    def test_filter_machine(self, api_client, setup_data):
        user = setup_data["user"]
        api_client.force_authenticate(user=user)
        
        url = "/api/machines/"
        res = api_client.get(url)
        assert res.status_code == 200
        
        # Should only see Machine from B1
        ids = [item["machineId"] for item in res.data]
        assert str(setup_data["m1"].machineId) in ids
        assert str(setup_data["m2"].machineId) not in ids

    def test_filter_channel(self, api_client, setup_data):
        user = setup_data["user"]
        api_client.force_authenticate(user=user)
        
        url = "/api/channels/"
        res = api_client.get(url)
        assert res.status_code == 200
        
        # Should only see Channel from B1
        ids = [item["idChannel"] for item in res.data]
        assert str(setup_data["c1"].idChannel) in ids
        assert str(setup_data["c2"].idChannel) not in ids
