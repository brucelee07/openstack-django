import requests

# proxy = {"https": "abc:abc%40123@218.90.141.146:4000"}

# url = "http://10.0.0.12/horizon"
# url = "http://10.0.0.194:5000/v3"
# url = "http://218.90.141.146:8774"
url = "https://36.154.248.198:5000"

# username = "admin"

# password = "admin%40123456"

# response = requests.get(url, auth=(username, password), proxies=proxy)
response = requests.get(url)
# response = requests.get(url, auth=(username, password))

# print(response.content)
print(response.status_code)

# from keystoneauth1.identity import v3
# from keystoneauth1 import session
# from keystoneclient.v3 import client
# from keystoneclient.v3.users import UserManager

# auth = v3.Password(
#     auth_url="http://10.0.0.194:5000/v3",
#     user_id="userid",
#     password="password",
#     project_domain_name="admin_domain",
# )

# sess = session.Session(auth=auth)

# keystone = client.Client(session=sess)

# user_manager = UserManager(keystone)

# users = user_manager.list()
