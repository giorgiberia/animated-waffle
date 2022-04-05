import datetime

import requests
from django.http import JsonResponse
from rest_framework import viewsets, permissions

from api.models import GithubUser
from api.serializers import GithubUserSerializer


def get_gihtub_user_details(username):
    url = f"https://api.github.com/users/{username}"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None


class GithubUserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = GithubUser.objects.all()
    serializer_class = GithubUserSerializer
    permission_classes = [permissions.AllowAny]

    def list(self, request, *args, **kwargs):
        users = self.get_queryset()
        serializer = self.get_serializer(users, many=True)
        return JsonResponse({"error": False, "msg": "Users", "result": serializer.data}, status=200)

    def retrieve(self, request, pk=None, **kwargs):
        username = str(pk).lower()

        if GithubUser.objects.filter(username=username).exists():
            user = GithubUser.objects.get(username=username)
            serializer = GithubUserSerializer(user)
        else:
            user_details = get_gihtub_user_details(username)

            if not user_details:
                return JsonResponse({"error": True, "msg": "User not found", "result": {}}, status=404)

            new_user = GithubUser(
                username=user_details["login"].lower(),
                name=user_details["name"],
                avatar_url=user_details["avatar_url"],
                html_url=user_details["html_url"],
                followers=user_details["followers"],
                following=user_details["following"],
                public_repos=user_details["public_repos"],
                retrieved_at=datetime.datetime.now(),
            )
            new_user.save()
            serializer = GithubUserSerializer(new_user)

        return JsonResponse({"error": False, "msg": "User", "result": serializer.data}, status=200)

