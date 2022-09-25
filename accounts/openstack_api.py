from keystoneauth1.identity import v3
from keystoneauth1 import session
from keystoneclient.v3 import client
from keystoneclient.v3.users import UserManager

auth = v3.Password(
    auth_url="http://36.154.248.198:5000/v3",
    user_id="admin",
    password="admin@123456",
    project_domain_name="admin_domain",
)

sess = session.Session(auth=auth)

keystone = client.Client(session=sess)

# token_key = keystone.auth_token
# print(token_key)
user_manager = UserManager(keystone)

users = user_manager.list()
print(users)
