from keystoneclient.v3 import client

from novaclient import client as noclient

# from keystoneauth1.identity import v3
# from keystoneauth1 import session

auth_url = "http://10.0.0.194:5000/v3"
username = "admin"
password = "abc@123456"
user_domain_name = "admin_domain"

keystone = client.Client(
    auth_url=auth_url,
    username=username,
    password=password,
    user_domain_name=user_domain_name,
)

auth_token = keystone.auth_ref["auth_token"]
print(auth_token)
nova_url = "http://10.0.0.6:8774/v2.1"
nova_c = noclient.Client(auth_url=nova_url, version="2.1", auth_token=auth_token)
print(nova_c.servers.list())
# instances = nova_c.servers.list()
# for instance in instances:
#     print(instance)


# auth = v3.Password(
#     auth_url=auth_url,
#     username=username,
#     password=password,
#     user_domain_name=user_domain_name,
# )

# sess = session.Session(auth=auth)
# keystone = client.Client(session=sess)
# print(keystone.auth_ref)
