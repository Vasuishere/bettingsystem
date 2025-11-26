# Django Setup Script - Creates test users
# Save this as: setup_django_users.py

from django.contrib.auth import get_user_model
from django.db import connection

User = get_user_model()

def create_test_users():
    print("\n🌱 Creating Django test users...\n")
    
    # Create admin superuser
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@betting.com',
            password='admin123',
            first_name='Admin',
            last_name='User'
        )
        print("✅ Admin user created")
        print("   Username: admin")
        print("   Email: admin@betting.com")
        print("   Password: admin123\n")
    else:
        print("⚠️  Admin user already exists\n")
    
    # Create test user
    if not User.objects.filter(username='testuser').exists():
        testuser = User.objects.create_user(
            username='testuser',
            email='test@betting.com',
            password='test123',
            first_name='Test',
            last_name='User'
        )
        print("✅ Test user created")
        print("   Username: testuser")
        print("   Email: test@betting.com")
        print("   Password: test123\n")
    else:
        print("⚠️  Test user already exists\n")
    
    # Create demo user
    if not User.objects.filter(username='demo').exists():
        demouser = User.objects.create_user(
            username='demo',
            email='demo@betting.com',
            password='demo123',
            first_name='Demo',
            last_name='User'
        )
        print("✅ Demo user created")
        print("   Username: demo")
        print("   Email: demo@betting.com")
        print("   Password: demo123\n")
    else:
        print("⚠️  Demo user already exists\n")
    
    print("🎉 Django users setup completed!\n")
    print("═══════════════════════════════════════════")
    print("LOGIN CREDENTIALS:")
    print("═══════════════════════════════════════════")
    print("\n1️⃣  DJANGO ADMIN (Superuser)")
    print("   URL: http://localhost:8000/admin/")
    print("   Username: admin")
    print("   Password: admin123")
    print("\n2️⃣  TEST USER")
    print("   Username: testuser")
    print("   Password: test123")
    print("\n3️⃣  DEMO USER")
    print("   Username: demo")
    print("   Password: demo123")
    print("═══════════════════════════════════════════\n")

if __name__ == '__main__':
    create_test_users()
