from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

user = User.objects.create_user('test')
token = Token.objects.create(user=user)
print(token.key)