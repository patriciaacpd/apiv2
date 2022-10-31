import json
from unittest.mock import MagicMock, patch

from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.views import APIView

import breathecode.utils.decorators as decorators
from breathecode.utils.decorators import PermissionContextType

from ..mixins import UtilsTestCase

PERMISSION = 'can_kill_kenny'
GET_RESPONSE = {'a': 1}
GET_ID_RESPONSE = {'a': 2}
POST_RESPONSE = {'a': 3}
PUT_ID_RESPONSE = {'a': 4}
DELETE_ID_RESPONSE = {'a': 5}
UTC_NOW = timezone.now()


def consumer(context: PermissionContextType, args: tuple, kwargs: dict) -> tuple[dict, tuple, dict]:
    return (context, args, kwargs)


CONSUMER_MOCK = MagicMock(wraps=consumer)


def build_view_function(methods, data, decorator, decorator_args=(), decorator_kwargs={}):

    @api_view(methods)
    @permission_classes([AllowAny])
    @decorator(*decorator_args, **decorator_kwargs)
    def view_function(request, id=None):
        return Response(data)

    return view_function


get = build_view_function(['GET'], GET_RESPONSE, decorators.has_permission, decorator_args=(PERMISSION, ))
get_consumer = build_view_function(['GET'],
                                   GET_RESPONSE,
                                   decorators.has_permission,
                                   decorator_args=(PERMISSION, ),
                                   decorator_kwargs={'consumer': True})

get_consumer_callback = build_view_function(['GET'],
                                            GET_RESPONSE,
                                            decorators.has_permission,
                                            decorator_args=(PERMISSION, ),
                                            decorator_kwargs={'consumer': CONSUMER_MOCK})

get_id = build_view_function(['GET'],
                             GET_ID_RESPONSE,
                             decorators.has_permission,
                             decorator_args=(PERMISSION, ))

get_id_consumer = build_view_function(['GET'],
                                      GET_ID_RESPONSE,
                                      decorators.has_permission,
                                      decorator_args=(PERMISSION, ),
                                      decorator_kwargs={'consumer': True})

get_id_consumer_callback = build_view_function(['GET'],
                                               GET_ID_RESPONSE,
                                               decorators.has_permission,
                                               decorator_args=(PERMISSION, ),
                                               decorator_kwargs={'consumer': CONSUMER_MOCK})

post = build_view_function(['POST'], POST_RESPONSE, decorators.has_permission, decorator_args=(PERMISSION, ))
post_consumer = build_view_function(['POST'],
                                    POST_RESPONSE,
                                    decorators.has_permission,
                                    decorator_args=(PERMISSION, ),
                                    decorator_kwargs={'consumer': True})

post_consumer_callback = build_view_function(['POST'],
                                             POST_RESPONSE,
                                             decorators.has_permission,
                                             decorator_args=(PERMISSION, ),
                                             decorator_kwargs={'consumer': CONSUMER_MOCK})

put_id = build_view_function(['PUT'],
                             PUT_ID_RESPONSE,
                             decorators.has_permission,
                             decorator_args=(PERMISSION, ))

put_id_consumer = build_view_function(['PUT'],
                                      PUT_ID_RESPONSE,
                                      decorators.has_permission,
                                      decorator_args=(PERMISSION, ),
                                      decorator_kwargs={'consumer': True})

put_id_consumer_callback = build_view_function(['PUT'],
                                               PUT_ID_RESPONSE,
                                               decorators.has_permission,
                                               decorator_args=(PERMISSION, ),
                                               decorator_kwargs={'consumer': CONSUMER_MOCK})

delete_id = build_view_function(['DELETE'],
                                DELETE_ID_RESPONSE,
                                decorators.has_permission,
                                decorator_args=(PERMISSION, ))

delete_id_consumer = build_view_function(['DELETE'],
                                         DELETE_ID_RESPONSE,
                                         decorators.has_permission,
                                         decorator_args=(PERMISSION, ),
                                         decorator_kwargs={'consumer': True})

delete_id_consumer_callback = build_view_function(['DELETE'],
                                                  DELETE_ID_RESPONSE,
                                                  decorators.has_permission,
                                                  decorator_args=(PERMISSION, ),
                                                  decorator_kwargs={'consumer': CONSUMER_MOCK})


def build_view_class(decorator, decorator_args=(), decorator_kwargs={}):

    class TestView(APIView):
        """
        List all snippets, or create a new snippet.
        """
        permission_classes = [AllowAny]

        @decorator(*decorator_args, **decorator_kwargs)
        def get(self, request, id=None):
            if id:
                return Response(GET_ID_RESPONSE)

            return Response(GET_RESPONSE)

        @decorator(*decorator_args, **decorator_kwargs)
        def post(self, request):
            return Response(POST_RESPONSE)

        @decorator(*decorator_args, **decorator_kwargs)
        def put(self, request, id):
            return Response(PUT_ID_RESPONSE)

        @decorator(*decorator_args, **decorator_kwargs)
        def delete(self, request, id=None):
            return Response(DELETE_ID_RESPONSE)

    return TestView


TestView = build_view_class(decorators.has_permission, decorator_args=(PERMISSION, ))
TestViewConsumer = build_view_class(decorators.has_permission,
                                    decorator_args=(PERMISSION, ),
                                    decorator_kwargs={'consumer': True})

TestViewConsumerCallback = build_view_class(decorators.has_permission,
                                            decorator_args=(PERMISSION, ),
                                            decorator_kwargs={'consumer': CONSUMER_MOCK})


class FunctionBasedViewTestSuite(UtilsTestCase):

    def setUp(self):
        super().setUp()
        CONSUMER_MOCK.call_args_list = []

    """
    🔽🔽🔽 Function get
    """

    def test__function__get__anonymous_user(self):
        factory = APIRequestFactory()
        request = factory.get('/they-killed-kenny')

        view = get

        response = view(request).render()
        expected = {'detail': 'anonymous-user-without-permission', 'status_code': 403}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__get__with_user(self):
        model = self.bc.database.create(user=1)

        factory = APIRequestFactory()
        request = factory.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = get

        response = view(request).render()
        expected = {'detail': 'without-permission', 'status_code': 403}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__get__with_user__with_permission__dont_match(self):
        model = self.bc.database.create(user=1, permission=1)

        factory = APIRequestFactory()
        request = factory.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = get

        response = view(request).render()
        expected = {'detail': 'without-permission', 'status_code': 403}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__get__with_user__with_permission(self):
        permission = {'codename': PERMISSION}
        model = self.bc.database.create(user=1, permission=permission)

        factory = APIRequestFactory()
        request = factory.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = get

        response = view(request).render()
        expected = GET_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__get__with_user__with_group_related_to_permission(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        model = self.bc.database.create(user=user, permission=permissions, group=group)

        factory = APIRequestFactory()
        request = factory.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = get

        response = view(request).render()
        expected = GET_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    """
    🔽🔽🔽 Function get id
    """

    def test__function__get_id__anonymous_user(self):
        factory = APIRequestFactory()
        request = factory.get('/they-killed-kenny')

        view = get_id

        response = view(request, id=1).render()
        expected = {'detail': 'anonymous-user-without-permission', 'status_code': 403}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__get_id__with_user(self):
        model = self.bc.database.create(user=1)

        factory = APIRequestFactory()
        request = factory.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = get_id

        response = view(request, id=1).render()
        expected = {'detail': 'without-permission', 'status_code': 403}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__get_id__with_user__with_permission__dont_match(self):
        model = self.bc.database.create(user=1, permission=1)

        factory = APIRequestFactory()
        request = factory.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = get_id

        response = view(request, id=1).render()
        expected = {'detail': 'without-permission', 'status_code': 403}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__get_id__with_user__with_permission(self):
        permission = {'codename': PERMISSION}
        model = self.bc.database.create(user=1, permission=permission)

        factory = APIRequestFactory()
        request = factory.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = get_id

        response = view(request, id=1).render()
        expected = GET_ID_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__get_id__with_user__with_group_related_to_permission(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        model = self.bc.database.create(user=user, permission=permissions, group=group)

        factory = APIRequestFactory()
        request = factory.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = get_id

        response = view(request, id=1).render()
        expected = GET_ID_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    """
    🔽🔽🔽 Function post
    """

    def test__function__post__anonymous_user(self):
        factory = APIRequestFactory()
        request = factory.post('/they-killed-kenny')

        view = post

        response = view(request).render()
        expected = {'detail': 'anonymous-user-without-permission', 'status_code': 403}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__post__with_user(self):
        model = self.bc.database.create(user=1)

        factory = APIRequestFactory()
        request = factory.post('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = post

        response = view(request).render()
        expected = {'detail': 'without-permission', 'status_code': 403}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__post__with_user__with_permission__dont_match(self):
        model = self.bc.database.create(user=1, permission=1)

        factory = APIRequestFactory()
        request = factory.post('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = post

        response = view(request).render()
        expected = {'detail': 'without-permission', 'status_code': 403}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__post__with_user__with_permission(self):
        permission = {'codename': PERMISSION}
        model = self.bc.database.create(user=1, permission=permission)

        factory = APIRequestFactory()
        request = factory.post('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = post

        response = view(request).render()
        expected = POST_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__post__with_user__with_group_related_to_permission(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        model = self.bc.database.create(user=user, permission=permissions, group=group)

        factory = APIRequestFactory()
        request = factory.post('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = post

        response = view(request).render()
        expected = POST_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    """
    🔽🔽🔽 Function put id
    """

    def test__function__put_id__anonymous_user(self):
        factory = APIRequestFactory()
        request = factory.put('/they-killed-kenny')

        view = put_id

        response = view(request, id=1).render()
        expected = {'detail': 'anonymous-user-without-permission', 'status_code': 403}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__put_id__with_user(self):
        model = self.bc.database.create(user=1)

        factory = APIRequestFactory()
        request = factory.put('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = put_id

        response = view(request, id=1).render()
        expected = {'detail': 'without-permission', 'status_code': 403}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__put_id__with_user__with_permission__dont_match(self):
        model = self.bc.database.create(user=1, permission=1)

        factory = APIRequestFactory()
        request = factory.put('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = put_id

        response = view(request, id=1).render()
        expected = {'detail': 'without-permission', 'status_code': 403}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__put_id__with_user__with_permission(self):
        permission = {'codename': PERMISSION}
        model = self.bc.database.create(user=1, permission=permission)

        factory = APIRequestFactory()
        request = factory.put('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = put_id

        response = view(request, id=1).render()
        expected = PUT_ID_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__put_id__with_user__with_group_related_to_permission(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        model = self.bc.database.create(user=user, permission=permissions, group=group)

        factory = APIRequestFactory()
        request = factory.put('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = put_id

        response = view(request, id=1).render()
        expected = PUT_ID_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    """
    🔽🔽🔽 Function delete id
    """

    def test__function__delete_id__anonymous_user(self):
        factory = APIRequestFactory()
        request = factory.delete('/they-killed-kenny')

        view = delete_id

        response = view(request, id=1).render()
        expected = {'detail': 'anonymous-user-without-permission', 'status_code': 403}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__delete_id__with_user(self):
        model = self.bc.database.create(user=1)

        factory = APIRequestFactory()
        request = factory.delete('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = delete_id

        response = view(request, id=1).render()
        expected = {'detail': 'without-permission', 'status_code': 403}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__delete_id__with_user__with_permission__dont_match(self):
        model = self.bc.database.create(user=1, permission=1)

        factory = APIRequestFactory()
        request = factory.delete('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = delete_id

        response = view(request, id=1).render()
        expected = {'detail': 'without-permission', 'status_code': 403}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__delete_id__with_user__with_permission(self):
        permission = {'codename': PERMISSION}
        model = self.bc.database.create(user=1, permission=permission)

        factory = APIRequestFactory()
        request = factory.delete('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = delete_id

        response = view(request, id=1).render()
        expected = DELETE_ID_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__delete_id__with_user__with_group_related_to_permission(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        model = self.bc.database.create(user=user, permission=permissions, group=group)

        factory = APIRequestFactory()
        request = factory.delete('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = delete_id

        response = view(request, id=1).render()
        expected = DELETE_ID_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])


class ConsumerFunctionBasedViewTestSuite(UtilsTestCase):

    def setUp(self):
        super().setUp()
        CONSUMER_MOCK.call_args_list = []

    """
    🔽🔽🔽 Function get
    """

    def test__function__get__anonymous_user(self):
        factory = APIRequestFactory()
        request = factory.get('/they-killed-kenny')

        view = get_consumer

        response = view(request).render()
        expected = {'detail': 'anonymous-user-not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__get__with_user(self):
        model = self.bc.database.create(user=1)

        factory = APIRequestFactory()
        request = factory.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = get_consumer

        response = view(request).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__get__with_user__with_permission__dont_match(self):
        model = self.bc.database.create(user=1, permission=1)

        factory = APIRequestFactory()
        request = factory.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = get_consumer

        response = view(request).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__get__with_user__with_group_related_to_permission__without_consumable(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        model = self.bc.database.create(user=user, permission=permissions, group=group)

        factory = APIRequestFactory()
        request = factory.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = get_consumer

        response = view(request).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__get__with_user__with_group_related_to_permission__consumable__how_many_minus_1(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': -1}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        factory = APIRequestFactory()
        request = factory.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = get_consumer

        response = view(request).render()
        expected = GET_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__get__with_user__with_group_related_to_permission__consumable__how_many_0(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': 0}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        factory = APIRequestFactory()
        request = factory.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = get_consumer

        response = view(request).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__get__with_user__with_group_related_to_permission__consumable__how_many_1(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': 1}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        factory = APIRequestFactory()
        request = factory.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = get_consumer

        response = view(request).render()
        expected = GET_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    """
    🔽🔽🔽 Function get id
    """

    def test__function__get_id__anonymous_user(self):
        factory = APIRequestFactory()
        request = factory.get('/they-killed-kenny')

        view = get_id_consumer

        response = view(request, id=1).render()
        expected = {'detail': 'anonymous-user-not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__get_id__with_user(self):
        model = self.bc.database.create(user=1)

        factory = APIRequestFactory()
        request = factory.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = get_id_consumer

        response = view(request, id=1).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__get_id__with_user__with_permission__dont_match(self):
        model = self.bc.database.create(user=1, permission=1)

        factory = APIRequestFactory()
        request = factory.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = get_id_consumer

        response = view(request, id=1).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__get_id__with_user__with_group_related_to_permission__without_consumable(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        model = self.bc.database.create(user=user, permission=permissions, group=group)

        factory = APIRequestFactory()
        request = factory.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = get_id_consumer

        response = view(request, id=1).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__get_id__with_user__with_group_related_to_permission__consumable__how_many_minus_1(
            self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': -1}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        factory = APIRequestFactory()
        request = factory.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = get_id_consumer

        response = view(request, id=1).render()
        expected = GET_ID_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__get_id__with_user__with_group_related_to_permission__consumable__how_many_0(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': 0}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        factory = APIRequestFactory()
        request = factory.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = get_id_consumer

        response = view(request, id=1).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__get_id__with_user__with_group_related_to_permission__consumable__how_many_1(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': 1}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        factory = APIRequestFactory()
        request = factory.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = get_id_consumer

        response = view(request, id=1).render()
        expected = GET_ID_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    """
    🔽🔽🔽 Function post
    """

    def test__function__post__anonymous_user(self):
        factory = APIRequestFactory()
        request = factory.post('/they-killed-kenny')

        view = post_consumer

        response = view(request).render()
        expected = {'detail': 'anonymous-user-not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__post__with_user(self):
        model = self.bc.database.create(user=1)

        factory = APIRequestFactory()
        request = factory.post('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = post_consumer

        response = view(request).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__post__with_user__with_permission__dont_match(self):
        model = self.bc.database.create(user=1, permission=1)

        factory = APIRequestFactory()
        request = factory.post('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = post_consumer

        response = view(request).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__post__with_user__with_group_related_to_permission__without_consumable(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        model = self.bc.database.create(user=user, permission=permissions, group=group)

        factory = APIRequestFactory()
        request = factory.post('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = post_consumer

        response = view(request).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__post__with_user__with_group_related_to_permission__consumable__how_many_minus_1(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': -1}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        factory = APIRequestFactory()
        request = factory.post('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = post_consumer

        response = view(request).render()
        expected = POST_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__post__with_user__with_group_related_to_permission__consumable__how_many_0(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': 0}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        factory = APIRequestFactory()
        request = factory.post('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = post_consumer

        response = view(request).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__post__with_user__with_group_related_to_permission__consumable__how_many_1(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': 1}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        factory = APIRequestFactory()
        request = factory.post('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = post_consumer

        response = view(request).render()
        expected = POST_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    """
    🔽🔽🔽 Function put id
    """

    def test__function__put_id__anonymous_user(self):
        factory = APIRequestFactory()
        request = factory.put('/they-killed-kenny')

        view = put_id_consumer

        response = view(request, id=1).render()
        expected = {'detail': 'anonymous-user-not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__put_id__with_user(self):
        model = self.bc.database.create(user=1)

        factory = APIRequestFactory()
        request = factory.put('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = put_id_consumer

        response = view(request, id=1).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__put_id__with_user__with_permission__dont_match(self):
        model = self.bc.database.create(user=1, permission=1)

        factory = APIRequestFactory()
        request = factory.put('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = put_id_consumer

        response = view(request, id=1).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__put_id__with_user__with_group_related_to_permission__without_consumable(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        model = self.bc.database.create(user=user, permission=permissions, group=group)

        factory = APIRequestFactory()
        request = factory.put('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = put_id_consumer

        response = view(request, id=1).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__put_id__with_user__with_group_related_to_permission__consumable__how_many_minus_1(
            self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': -1}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        factory = APIRequestFactory()
        request = factory.put('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = put_id_consumer

        response = view(request, id=1).render()
        expected = PUT_ID_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__put_id__with_user__with_group_related_to_permission__consumable__how_many_0(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': 0}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        factory = APIRequestFactory()
        request = factory.put('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = put_id_consumer

        response = view(request, id=1).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__put_id__with_user__with_group_related_to_permission__consumable__how_many_1(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': 1}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        factory = APIRequestFactory()
        request = factory.put('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = put_id_consumer

        response = view(request, id=1).render()
        expected = PUT_ID_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    """
    🔽🔽🔽 Function delete id
    """

    def test__function__delete_id__anonymous_user(self):
        factory = APIRequestFactory()
        request = factory.delete('/they-killed-kenny')

        view = delete_id_consumer

        response = view(request, id=1).render()
        expected = {'detail': 'anonymous-user-not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__delete_id__with_user(self):
        model = self.bc.database.create(user=1)

        factory = APIRequestFactory()
        request = factory.delete('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = delete_id_consumer

        response = view(request, id=1).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__delete_id__with_user__with_permission__dont_match(self):
        model = self.bc.database.create(user=1, permission=1)

        factory = APIRequestFactory()
        request = factory.delete('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = delete_id_consumer

        response = view(request, id=1).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__delete_id__with_user__with_group_related_to_permission__without_consumable(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        model = self.bc.database.create(user=user, permission=permissions, group=group)

        factory = APIRequestFactory()
        request = factory.delete('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = delete_id_consumer

        response = view(request, id=1).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__delete_id__with_user__with_group_related_to_permission__consumable__how_many_minus_1(
            self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': -1}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        factory = APIRequestFactory()
        request = factory.delete('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = delete_id_consumer

        response = view(request, id=1).render()
        expected = DELETE_ID_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__delete_id__with_user__with_group_related_to_permission__consumable__how_many_0(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': 0}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        factory = APIRequestFactory()
        request = factory.delete('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = delete_id_consumer

        response = view(request, id=1).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__delete_id__with_user__with_group_related_to_permission__consumable__how_many_1(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': 1}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        factory = APIRequestFactory()
        request = factory.delete('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = delete_id_consumer

        response = view(request, id=1).render()
        expected = DELETE_ID_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])


class ConsumerFunctionCallbackBasedViewTestSuite(UtilsTestCase):

    def setUp(self):
        super().setUp()
        CONSUMER_MOCK.call_args_list = []

    """
    🔽🔽🔽 Function get
    """

    def test__function__get__anonymous_user(self):
        factory = APIRequestFactory()
        request = factory.get('/they-killed-kenny')

        view = get_consumer_callback

        response = view(request).render()
        expected = {'detail': 'anonymous-user-not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__get__with_user(self):
        model = self.bc.database.create(user=1)

        factory = APIRequestFactory()
        request = factory.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = get_consumer_callback

        response = view(request).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__get__with_user__with_permission__dont_match(self):
        model = self.bc.database.create(user=1, permission=1)

        factory = APIRequestFactory()
        request = factory.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = get_consumer_callback

        response = view(request).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__get__with_user__with_group_related_to_permission__without_consumable(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        model = self.bc.database.create(user=user, permission=permissions, group=group)

        factory = APIRequestFactory()
        request = factory.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = get_consumer_callback

        response = view(request).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)

        Consumable = self.bc.database.get_model('payments.Consumable')
        consumables = Consumable.objects.filter()
        self.assertEqual(len(CONSUMER_MOCK.call_args_list), 1)

        args, kwargs = CONSUMER_MOCK.call_args_list[0]
        context, args, kwargs = args

        self.assertTrue(isinstance(context['request'], Request))
        self.bc.check.partial_equality(context, {
            'utc_now': UTC_NOW,
            'consumer': CONSUMER_MOCK,
            'permission': PERMISSION,
            'consumables': consumables,
        })

        self.assertEqual(len(args), 1)
        self.assertTrue(isinstance(args[0], Request))

        self.assertEqual(kwargs, {})

    def test__function__get__with_user__with_group_related_to_permission__consumable__how_many_minus_1(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': -1}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        factory = APIRequestFactory()
        request = factory.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = get_consumer_callback

        response = view(request).render()
        expected = GET_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        Consumable = self.bc.database.get_model('payments.Consumable')
        consumables = Consumable.objects.filter()
        self.assertEqual(len(CONSUMER_MOCK.call_args_list), 1)

        args, kwargs = CONSUMER_MOCK.call_args_list[0]
        context, args, kwargs = args

        self.assertTrue(isinstance(context['request'], Request))
        self.bc.check.partial_equality(context, {
            'utc_now': UTC_NOW,
            'consumer': CONSUMER_MOCK,
            'permission': PERMISSION,
            'consumables': consumables,
        })

        self.assertEqual(len(args), 1)
        self.assertTrue(isinstance(args[0], Request))

        self.assertEqual(kwargs, {})

    def test__function__get__with_user__with_group_related_to_permission__consumable__how_many_0(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': 0}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        factory = APIRequestFactory()
        request = factory.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = get_consumer_callback

        response = view(request).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)

        Consumable = self.bc.database.get_model('payments.Consumable')
        consumables = Consumable.objects.filter()
        self.assertEqual(len(CONSUMER_MOCK.call_args_list), 1)

        args, kwargs = CONSUMER_MOCK.call_args_list[0]
        context, args, kwargs = args

        self.assertTrue(isinstance(context['request'], Request))
        self.bc.check.partial_equality(context, {
            'utc_now': UTC_NOW,
            'consumer': CONSUMER_MOCK,
            'permission': PERMISSION,
            'consumables': consumables,
        })

        self.assertEqual(len(args), 1)
        self.assertTrue(isinstance(args[0], Request))

        self.assertEqual(kwargs, {})

    def test__function__get__with_user__with_group_related_to_permission__consumable__how_many_1(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': 1}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        factory = APIRequestFactory()
        request = factory.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = get_consumer_callback

        response = view(request).render()
        expected = GET_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        Consumable = self.bc.database.get_model('payments.Consumable')
        consumables = Consumable.objects.filter()
        self.assertEqual(len(CONSUMER_MOCK.call_args_list), 1)

        args, kwargs = CONSUMER_MOCK.call_args_list[0]
        context, args, kwargs = args

        self.assertTrue(isinstance(context['request'], Request))
        self.bc.check.partial_equality(context, {
            'utc_now': UTC_NOW,
            'consumer': CONSUMER_MOCK,
            'permission': PERMISSION,
            'consumables': consumables,
        })

        self.assertEqual(len(args), 1)
        self.assertTrue(isinstance(args[0], Request))

        self.assertEqual(kwargs, {})

    """
    🔽🔽🔽 Function get id
    """

    def test__function__get_id__anonymous_user(self):
        factory = APIRequestFactory()
        request = factory.get('/they-killed-kenny')

        view = get_id_consumer_callback

        response = view(request, id=1).render()
        expected = {'detail': 'anonymous-user-not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__get_id__with_user(self):
        model = self.bc.database.create(user=1)

        factory = APIRequestFactory()
        request = factory.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = get_id_consumer_callback

        response = view(request, id=1).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__get_id__with_user__with_permission__dont_match(self):
        model = self.bc.database.create(user=1, permission=1)

        factory = APIRequestFactory()
        request = factory.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = get_id_consumer_callback

        response = view(request, id=1).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__get_id__with_user__with_group_related_to_permission__without_consumable(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        model = self.bc.database.create(user=user, permission=permissions, group=group)

        factory = APIRequestFactory()
        request = factory.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = get_id_consumer_callback

        response = view(request, id=1).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)

        Consumable = self.bc.database.get_model('payments.Consumable')
        consumables = Consumable.objects.filter()
        self.assertEqual(len(CONSUMER_MOCK.call_args_list), 1)

        args, kwargs = CONSUMER_MOCK.call_args_list[0]
        context, args, kwargs = args

        self.assertTrue(isinstance(context['request'], Request))
        self.bc.check.partial_equality(context, {
            'utc_now': UTC_NOW,
            'consumer': CONSUMER_MOCK,
            'permission': PERMISSION,
            'consumables': consumables,
        })

        self.assertEqual(len(args), 1)
        self.assertTrue(isinstance(args[0], Request))

        self.assertEqual(kwargs, {'id': 1})

    def test__function__get_id__with_user__with_group_related_to_permission__consumable__how_many_minus_1(
            self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': -1}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        factory = APIRequestFactory()
        request = factory.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = get_id_consumer_callback

        response = view(request, id=1).render()
        expected = GET_ID_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        Consumable = self.bc.database.get_model('payments.Consumable')
        consumables = Consumable.objects.filter()
        self.assertEqual(len(CONSUMER_MOCK.call_args_list), 1)

        args, kwargs = CONSUMER_MOCK.call_args_list[0]
        context, args, kwargs = args

        self.assertTrue(isinstance(context['request'], Request))
        self.bc.check.partial_equality(context, {
            'utc_now': UTC_NOW,
            'consumer': CONSUMER_MOCK,
            'permission': PERMISSION,
            'consumables': consumables,
        })

        self.assertEqual(len(args), 1)
        self.assertTrue(isinstance(args[0], Request))

        self.assertEqual(kwargs, {'id': 1})

    def test__function__get_id__with_user__with_group_related_to_permission__consumable__how_many_0(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': 0}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        factory = APIRequestFactory()
        request = factory.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = get_id_consumer_callback

        response = view(request, id=1).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)

        Consumable = self.bc.database.get_model('payments.Consumable')
        consumables = Consumable.objects.filter()
        self.assertEqual(len(CONSUMER_MOCK.call_args_list), 1)

        args, kwargs = CONSUMER_MOCK.call_args_list[0]
        context, args, kwargs = args

        self.assertTrue(isinstance(context['request'], Request))
        self.bc.check.partial_equality(context, {
            'utc_now': UTC_NOW,
            'consumer': CONSUMER_MOCK,
            'permission': PERMISSION,
            'consumables': consumables,
        })

        self.assertEqual(len(args), 1)
        self.assertTrue(isinstance(args[0], Request))

        self.assertEqual(kwargs, {'id': 1})

    def test__function__get_id__with_user__with_group_related_to_permission__consumable__how_many_1(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': 1}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        factory = APIRequestFactory()
        request = factory.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = get_id_consumer_callback

        response = view(request, id=1).render()
        expected = GET_ID_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        Consumable = self.bc.database.get_model('payments.Consumable')
        consumables = Consumable.objects.filter()
        self.assertEqual(len(CONSUMER_MOCK.call_args_list), 1)

        args, kwargs = CONSUMER_MOCK.call_args_list[0]
        context, args, kwargs = args

        self.assertTrue(isinstance(context['request'], Request))
        self.bc.check.partial_equality(context, {
            'utc_now': UTC_NOW,
            'consumer': CONSUMER_MOCK,
            'permission': PERMISSION,
            'consumables': consumables,
        })

        self.assertEqual(len(args), 1)
        self.assertTrue(isinstance(args[0], Request))

        self.assertEqual(kwargs, {'id': 1})

    """
    🔽🔽🔽 Function post
    """

    def test__function__post__anonymous_user(self):
        factory = APIRequestFactory()
        request = factory.post('/they-killed-kenny')

        view = post_consumer_callback

        response = view(request).render()
        expected = {'detail': 'anonymous-user-not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__post__with_user(self):
        model = self.bc.database.create(user=1)

        factory = APIRequestFactory()
        request = factory.post('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = post_consumer_callback

        response = view(request).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__post__with_user__with_permission__dont_match(self):
        model = self.bc.database.create(user=1, permission=1)

        factory = APIRequestFactory()
        request = factory.post('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = post_consumer_callback

        response = view(request).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__post__with_user__with_group_related_to_permission__without_consumable(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        model = self.bc.database.create(user=user, permission=permissions, group=group)

        factory = APIRequestFactory()
        request = factory.post('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = post_consumer_callback

        response = view(request).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)

        Consumable = self.bc.database.get_model('payments.Consumable')
        consumables = Consumable.objects.filter()
        self.assertEqual(len(CONSUMER_MOCK.call_args_list), 1)

        args, kwargs = CONSUMER_MOCK.call_args_list[0]
        context, args, kwargs = args

        self.assertTrue(isinstance(context['request'], Request))
        self.bc.check.partial_equality(context, {
            'utc_now': UTC_NOW,
            'consumer': CONSUMER_MOCK,
            'permission': PERMISSION,
            'consumables': consumables,
        })

        self.assertEqual(len(args), 1)
        self.assertTrue(isinstance(args[0], Request))

        self.assertEqual(kwargs, {})

    def test__function__post__with_user__with_group_related_to_permission__consumable__how_many_minus_1(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': -1}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        factory = APIRequestFactory()
        request = factory.post('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = post_consumer_callback

        response = view(request).render()
        expected = POST_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        Consumable = self.bc.database.get_model('payments.Consumable')
        consumables = Consumable.objects.filter()
        self.assertEqual(len(CONSUMER_MOCK.call_args_list), 1)

        args, kwargs = CONSUMER_MOCK.call_args_list[0]
        context, args, kwargs = args

        self.assertTrue(isinstance(context['request'], Request))
        self.bc.check.partial_equality(context, {
            'utc_now': UTC_NOW,
            'consumer': CONSUMER_MOCK,
            'permission': PERMISSION,
            'consumables': consumables,
        })

        self.assertEqual(len(args), 1)
        self.assertTrue(isinstance(args[0], Request))

        self.assertEqual(kwargs, {})

    def test__function__post__with_user__with_group_related_to_permission__consumable__how_many_0(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': 0}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        factory = APIRequestFactory()
        request = factory.post('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = post_consumer_callback

        response = view(request).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)

        Consumable = self.bc.database.get_model('payments.Consumable')
        consumables = Consumable.objects.filter()
        self.assertEqual(len(CONSUMER_MOCK.call_args_list), 1)

        args, kwargs = CONSUMER_MOCK.call_args_list[0]
        context, args, kwargs = args

        self.assertTrue(isinstance(context['request'], Request))
        self.bc.check.partial_equality(context, {
            'utc_now': UTC_NOW,
            'consumer': CONSUMER_MOCK,
            'permission': PERMISSION,
            'consumables': consumables,
        })

        self.assertEqual(len(args), 1)
        self.assertTrue(isinstance(args[0], Request))

        self.assertEqual(kwargs, {})

    def test__function__post__with_user__with_group_related_to_permission__consumable__how_many_1(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': 1}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        factory = APIRequestFactory()
        request = factory.post('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = post_consumer_callback

        response = view(request).render()
        expected = POST_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        Consumable = self.bc.database.get_model('payments.Consumable')
        consumables = Consumable.objects.filter()
        self.assertEqual(len(CONSUMER_MOCK.call_args_list), 1)

        args, kwargs = CONSUMER_MOCK.call_args_list[0]
        context, args, kwargs = args

        self.assertTrue(isinstance(context['request'], Request))
        self.bc.check.partial_equality(context, {
            'utc_now': UTC_NOW,
            'consumer': CONSUMER_MOCK,
            'permission': PERMISSION,
            'consumables': consumables,
        })

        self.assertEqual(len(args), 1)
        self.assertTrue(isinstance(args[0], Request))

        self.assertEqual(kwargs, {})

    """
    🔽🔽🔽 Function put id
    """

    def test__function__put_id__anonymous_user(self):
        factory = APIRequestFactory()
        request = factory.put('/they-killed-kenny')

        view = put_id_consumer_callback

        response = view(request, id=1).render()
        expected = {'detail': 'anonymous-user-not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__put_id__with_user(self):
        model = self.bc.database.create(user=1)

        factory = APIRequestFactory()
        request = factory.put('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = put_id_consumer_callback

        response = view(request, id=1).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__put_id__with_user__with_permission__dont_match(self):
        model = self.bc.database.create(user=1, permission=1)

        factory = APIRequestFactory()
        request = factory.put('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = put_id_consumer_callback

        response = view(request, id=1).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__put_id__with_user__with_group_related_to_permission__without_consumable(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        model = self.bc.database.create(user=user, permission=permissions, group=group)

        factory = APIRequestFactory()
        request = factory.put('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = put_id_consumer_callback

        response = view(request, id=1).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)

        Consumable = self.bc.database.get_model('payments.Consumable')
        consumables = Consumable.objects.filter()
        self.assertEqual(len(CONSUMER_MOCK.call_args_list), 1)

        args, kwargs = CONSUMER_MOCK.call_args_list[0]
        context, args, kwargs = args

        self.assertTrue(isinstance(context['request'], Request))
        self.bc.check.partial_equality(context, {
            'utc_now': UTC_NOW,
            'consumer': CONSUMER_MOCK,
            'permission': PERMISSION,
            'consumables': consumables,
        })

        self.assertEqual(len(args), 1)
        self.assertTrue(isinstance(args[0], Request))

        self.assertEqual(kwargs, {'id': 1})

    def test__function__put_id__with_user__with_group_related_to_permission__consumable__how_many_minus_1(
            self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': -1}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        factory = APIRequestFactory()
        request = factory.put('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = put_id_consumer_callback

        response = view(request, id=1).render()
        expected = PUT_ID_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        Consumable = self.bc.database.get_model('payments.Consumable')
        consumables = Consumable.objects.filter()
        self.assertEqual(len(CONSUMER_MOCK.call_args_list), 1)

        args, kwargs = CONSUMER_MOCK.call_args_list[0]
        context, args, kwargs = args

        self.assertTrue(isinstance(context['request'], Request))
        self.bc.check.partial_equality(context, {
            'utc_now': UTC_NOW,
            'consumer': CONSUMER_MOCK,
            'permission': PERMISSION,
            'consumables': consumables,
        })

        self.assertEqual(len(args), 1)
        self.assertTrue(isinstance(args[0], Request))

        self.assertEqual(kwargs, {'id': 1})

    def test__function__put_id__with_user__with_group_related_to_permission__consumable__how_many_0(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': 0}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        factory = APIRequestFactory()
        request = factory.put('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = put_id_consumer_callback

        response = view(request, id=1).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)

        Consumable = self.bc.database.get_model('payments.Consumable')
        consumables = Consumable.objects.filter()
        self.assertEqual(len(CONSUMER_MOCK.call_args_list), 1)

        args, kwargs = CONSUMER_MOCK.call_args_list[0]
        context, args, kwargs = args

        self.assertTrue(isinstance(context['request'], Request))
        self.bc.check.partial_equality(context, {
            'utc_now': UTC_NOW,
            'consumer': CONSUMER_MOCK,
            'permission': PERMISSION,
            'consumables': consumables,
        })

        self.assertEqual(len(args), 1)
        self.assertTrue(isinstance(args[0], Request))

        self.assertEqual(kwargs, {'id': 1})

    def test__function__put_id__with_user__with_group_related_to_permission__consumable__how_many_1(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': 1}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        factory = APIRequestFactory()
        request = factory.put('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = put_id_consumer_callback

        response = view(request, id=1).render()
        expected = PUT_ID_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        Consumable = self.bc.database.get_model('payments.Consumable')
        consumables = Consumable.objects.filter()
        self.assertEqual(len(CONSUMER_MOCK.call_args_list), 1)

        args, kwargs = CONSUMER_MOCK.call_args_list[0]
        context, args, kwargs = args

        self.assertTrue(isinstance(context['request'], Request))
        self.bc.check.partial_equality(context, {
            'utc_now': UTC_NOW,
            'consumer': CONSUMER_MOCK,
            'permission': PERMISSION,
            'consumables': consumables,
        })

        self.assertEqual(len(args), 1)
        self.assertTrue(isinstance(args[0], Request))

        self.assertEqual(kwargs, {'id': 1})

    """
    🔽🔽🔽 Function delete id
    """

    def test__function__delete_id__anonymous_user(self):
        factory = APIRequestFactory()
        request = factory.delete('/they-killed-kenny')

        view = delete_id_consumer_callback

        response = view(request, id=1).render()
        expected = {'detail': 'anonymous-user-not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__delete_id__with_user(self):
        model = self.bc.database.create(user=1)

        factory = APIRequestFactory()
        request = factory.delete('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = delete_id_consumer_callback

        response = view(request, id=1).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__delete_id__with_user__with_permission__dont_match(self):
        model = self.bc.database.create(user=1, permission=1)

        factory = APIRequestFactory()
        request = factory.delete('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = delete_id_consumer_callback

        response = view(request, id=1).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__function__delete_id__with_user__with_group_related_to_permission__without_consumable(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        model = self.bc.database.create(user=user, permission=permissions, group=group)

        factory = APIRequestFactory()
        request = factory.delete('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = delete_id_consumer_callback

        response = view(request, id=1).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)

        Consumable = self.bc.database.get_model('payments.Consumable')
        consumables = Consumable.objects.filter()
        self.assertEqual(len(CONSUMER_MOCK.call_args_list), 1)

        args, kwargs = CONSUMER_MOCK.call_args_list[0]
        context, args, kwargs = args

        self.assertTrue(isinstance(context['request'], Request))
        self.bc.check.partial_equality(context, {
            'utc_now': UTC_NOW,
            'consumer': CONSUMER_MOCK,
            'permission': PERMISSION,
            'consumables': consumables,
        })

        self.assertEqual(len(args), 1)
        self.assertTrue(isinstance(args[0], Request))

        self.assertEqual(kwargs, {'id': 1})

    def test__function__delete_id__with_user__with_group_related_to_permission__consumable__how_many_minus_1(
            self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': -1}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        factory = APIRequestFactory()
        request = factory.delete('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = delete_id_consumer_callback

        response = view(request, id=1).render()
        expected = DELETE_ID_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        Consumable = self.bc.database.get_model('payments.Consumable')
        consumables = Consumable.objects.filter()
        self.assertEqual(len(CONSUMER_MOCK.call_args_list), 1)

        args, kwargs = CONSUMER_MOCK.call_args_list[0]
        context, args, kwargs = args

        self.assertTrue(isinstance(context['request'], Request))
        self.bc.check.partial_equality(context, {
            'utc_now': UTC_NOW,
            'consumer': CONSUMER_MOCK,
            'permission': PERMISSION,
            'consumables': consumables,
        })

        self.assertEqual(len(args), 1)
        self.assertTrue(isinstance(args[0], Request))

        self.assertEqual(kwargs, {'id': 1})

    def test__function__delete_id__with_user__with_group_related_to_permission__consumable__how_many_0(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': 0}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        factory = APIRequestFactory()
        request = factory.delete('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = delete_id_consumer_callback

        response = view(request, id=1).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)

        Consumable = self.bc.database.get_model('payments.Consumable')
        consumables = Consumable.objects.filter()
        self.assertEqual(len(CONSUMER_MOCK.call_args_list), 1)

        args, kwargs = CONSUMER_MOCK.call_args_list[0]
        context, args, kwargs = args

        self.assertTrue(isinstance(context['request'], Request))
        self.bc.check.partial_equality(context, {
            'utc_now': UTC_NOW,
            'consumer': CONSUMER_MOCK,
            'permission': PERMISSION,
            'consumables': consumables,
        })

        self.assertEqual(len(args), 1)
        self.assertTrue(isinstance(args[0], Request))

        self.assertEqual(kwargs, {'id': 1})

    def test__function__delete_id__with_user__with_group_related_to_permission__consumable__how_many_1(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': 1}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        factory = APIRequestFactory()
        request = factory.delete('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = delete_id_consumer_callback

        response = view(request, id=1).render()
        expected = DELETE_ID_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        Consumable = self.bc.database.get_model('payments.Consumable')
        consumables = Consumable.objects.filter()
        self.assertEqual(len(CONSUMER_MOCK.call_args_list), 1)

        args, kwargs = CONSUMER_MOCK.call_args_list[0]
        context, args, kwargs = args

        self.assertTrue(isinstance(context['request'], Request))
        self.bc.check.partial_equality(context, {
            'utc_now': UTC_NOW,
            'consumer': CONSUMER_MOCK,
            'permission': PERMISSION,
            'consumables': consumables,
        })

        self.assertEqual(len(args), 1)
        self.assertTrue(isinstance(args[0], Request))

        self.assertEqual(kwargs, {'id': 1})


class ViewTestSuite(UtilsTestCase):

    def setUp(self):
        super().setUp()
        CONSUMER_MOCK.call_args_list = []

    """
    🔽🔽🔽 View get
    """

    def test__view__get__anonymous_user(self):
        request = APIRequestFactory()
        request = request.get('/they-killed-kenny')

        view = TestView.as_view()

        response = view(request).render()
        expected = {'detail': 'anonymous-user-without-permission', 'status_code': 403}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__view__get__with_user(self):
        model = self.bc.database.create(user=1)

        request = APIRequestFactory()
        request = request.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestView.as_view()

        response = view(request).render()
        expected = {'detail': 'without-permission', 'status_code': 403}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__view__get__with_user__with_permission__dont_match(self):
        model = self.bc.database.create(user=1, permission=1)

        request = APIRequestFactory()
        request = request.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestView.as_view()

        response = view(request).render()
        expected = {'detail': 'without-permission', 'status_code': 403}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__view__get__with_user__with_permission(self):
        permission = {'codename': PERMISSION}
        model = self.bc.database.create(user=1, permission=permission)

        request = APIRequestFactory()
        request = request.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestView.as_view()

        response = view(request).render()
        expected = GET_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__view__get__with_user__with_group_related_to_permission(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        model = self.bc.database.create(user=user, permission=permissions, group=group)

        request = APIRequestFactory()
        request = request.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestView.as_view()

        response = view(request).render()
        expected = GET_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    """
    🔽🔽🔽 View get id
    """

    def test__view__get_id__anonymous_user(self):
        request = APIRequestFactory()
        request = request.get('/they-killed-kenny')

        view = TestView.as_view()

        response = view(request, id=1).render()
        expected = {'detail': 'anonymous-user-without-permission', 'status_code': 403}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__view__get_id__with_user(self):
        model = self.bc.database.create(user=1)

        request = APIRequestFactory()
        request = request.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestView.as_view()

        response = view(request, id=1).render()
        expected = {'detail': 'without-permission', 'status_code': 403}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__view__get_id__with_user__with_permission__dont_match(self):
        model = self.bc.database.create(user=1, permission=1)

        request = APIRequestFactory()
        request = request.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestView.as_view()

        response = view(request, id=1).render()
        expected = {'detail': 'without-permission', 'status_code': 403}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__view__get_id__with_user__with_permission(self):
        permission = {'codename': PERMISSION}
        model = self.bc.database.create(user=1, permission=permission)

        request = APIRequestFactory()
        request = request.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestView.as_view()

        response = view(request, id=1).render()
        expected = GET_ID_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__view__get_id__with_user__with_group_related_to_permission(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        model = self.bc.database.create(user=user, permission=permissions, group=group)

        request = APIRequestFactory()
        request = request.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestView.as_view()

        response = view(request, id=1).render()
        expected = GET_ID_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    """
    🔽🔽🔽 View post
    """

    def test__view__post__anonymous_user(self):
        request = APIRequestFactory()
        request = request.post('/they-killed-kenny')

        view = TestView.as_view()

        response = view(request).render()
        expected = {'detail': 'anonymous-user-without-permission', 'status_code': 403}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__view__post__with_user(self):
        model = self.bc.database.create(user=1)

        request = APIRequestFactory()
        request = request.post('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestView.as_view()

        response = view(request).render()
        expected = {'detail': 'without-permission', 'status_code': 403}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__view__post__with_user__with_permission__dont_match(self):
        model = self.bc.database.create(user=1, permission=1)

        request = APIRequestFactory()
        request = request.post('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestView.as_view()

        response = view(request).render()
        expected = {'detail': 'without-permission', 'status_code': 403}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__view__post__with_user__with_permission(self):
        permission = {'codename': PERMISSION}
        model = self.bc.database.create(user=1, permission=permission)

        request = APIRequestFactory()
        request = request.post('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestView.as_view()

        response = view(request).render()
        expected = POST_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__view__post__with_user__with_group_related_to_permission(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        model = self.bc.database.create(user=user, permission=permissions, group=group)

        request = APIRequestFactory()
        request = request.post('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestView.as_view()

        response = view(request).render()
        expected = POST_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    """
    🔽🔽🔽 View put id
    """

    def test__view__put_id__anonymous_user(self):
        request = APIRequestFactory()
        request = request.put('/they-killed-kenny')

        view = TestView.as_view()

        response = view(request, id=1).render()
        expected = {'detail': 'anonymous-user-without-permission', 'status_code': 403}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__view__put_id__with_user(self):
        model = self.bc.database.create(user=1)

        request = APIRequestFactory()
        request = request.put('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestView.as_view()

        response = view(request, id=1).render()
        expected = {'detail': 'without-permission', 'status_code': 403}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__view__put_id__with_user__with_permission__dont_match(self):
        model = self.bc.database.create(user=1, permission=1)

        request = APIRequestFactory()
        request = request.put('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestView.as_view()

        response = view(request, id=1).render()
        expected = {'detail': 'without-permission', 'status_code': 403}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__view__put_id__with_user__with_permission(self):
        permission = {'codename': PERMISSION}
        model = self.bc.database.create(user=1, permission=permission)

        request = APIRequestFactory()
        request = request.put('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestView.as_view()

        response = view(request, id=1).render()
        expected = PUT_ID_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__view__put_id__with_user__with_group_related_to_permission(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        model = self.bc.database.create(user=user, permission=permissions, group=group)

        request = APIRequestFactory()
        request = request.put('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestView.as_view()

        response = view(request, id=1).render()
        expected = PUT_ID_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    """
    🔽🔽🔽 View delete id
    """

    def test__view__delete_id__anonymous_user(self):
        request = APIRequestFactory()
        request = request.delete('/they-killed-kenny')

        view = TestView.as_view()

        response = view(request, id=1).render()
        expected = {'detail': 'anonymous-user-without-permission', 'status_code': 403}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__view__delete_id__with_user(self):
        model = self.bc.database.create(user=1)

        request = APIRequestFactory()
        request = request.delete('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestView.as_view()

        response = view(request, id=1).render()
        expected = {'detail': 'without-permission', 'status_code': 403}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__view__delete_id__with_user__with_permission__dont_match(self):
        model = self.bc.database.create(user=1, permission=1)

        request = APIRequestFactory()
        request = request.delete('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestView.as_view()

        response = view(request, id=1).render()
        expected = {'detail': 'without-permission', 'status_code': 403}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__view__delete_id__with_user__with_permission(self):
        permission = {'codename': PERMISSION}
        model = self.bc.database.create(user=1, permission=permission)

        request = APIRequestFactory()
        request = request.delete('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestView.as_view()

        response = view(request, id=1).render()
        expected = DELETE_ID_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__view__delete_id__with_user__with_group_related_to_permission(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        model = self.bc.database.create(user=user, permission=permissions, group=group)

        request = APIRequestFactory()
        request = request.delete('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestView.as_view()

        response = view(request, id=1).render()
        expected = DELETE_ID_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])


class ConsumerViewTestSuite(UtilsTestCase):

    def setUp(self):
        super().setUp()
        CONSUMER_MOCK.call_args_list = []

    """
    🔽🔽🔽 View get
    """

    def test__view__get__anonymous_user(self):
        request = APIRequestFactory()
        request = request.get('/they-killed-kenny')

        view = TestViewConsumer.as_view()

        response = view(request).render()
        expected = {'detail': 'anonymous-user-not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__view__get__with_user(self):
        model = self.bc.database.create(user=1)

        request = APIRequestFactory()
        request = request.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumer.as_view()

        response = view(request).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__view__get__with_user__with_permission__dont_match(self):
        model = self.bc.database.create(user=1, permission=1)

        request = APIRequestFactory()
        request = request.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumer.as_view()

        response = view(request).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__view__get__with_user__with_group_related_to_permission__without_consumer(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        model = self.bc.database.create(user=user, permission=permissions, group=group)

        request = APIRequestFactory()
        request = request.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumer.as_view()

        response = view(request).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__view__get__with_user__with_group_related_to_permission__consumer__how_many_minus_1(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': -1}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        request = APIRequestFactory()
        request = request.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumer.as_view()

        response = view(request).render()
        expected = GET_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__view__get__with_user__with_group_related_to_permission__consumer__how_many_0(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': 0}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        request = APIRequestFactory()
        request = request.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumer.as_view()

        response = view(request).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__view__get__with_user__with_group_related_to_permission__consumer__how_many_1(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': 1}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        request = APIRequestFactory()
        request = request.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumer.as_view()

        response = view(request).render()
        expected = GET_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    """
    🔽🔽🔽 View get id
    """

    def test__view__get_id__anonymous_user(self):
        request = APIRequestFactory()
        request = request.get('/they-killed-kenny')

        view = TestViewConsumer.as_view()

        response = view(request, id=1).render()
        expected = {'detail': 'anonymous-user-not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__view__get_id__with_user(self):
        model = self.bc.database.create(user=1)

        request = APIRequestFactory()
        request = request.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumer.as_view()

        response = view(request, id=1).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__view__get_id__with_user__with_permission__dont_match(self):
        model = self.bc.database.create(user=1, permission=1)

        request = APIRequestFactory()
        request = request.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumer.as_view()

        response = view(request, id=1).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__view__get_id__with_user__with_group_related_to_permission__without_consumer(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        model = self.bc.database.create(user=user, permission=permissions, group=group)

        request = APIRequestFactory()
        request = request.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumer.as_view()

        response = view(request, id=1).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__view__get_id__with_user__with_group_related_to_permission__consumer__how_many_minus_1(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': -1}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        request = APIRequestFactory()
        request = request.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumer.as_view()

        response = view(request, id=1).render()
        expected = GET_ID_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__view__get_id__with_user__with_group_related_to_permission__consumer__how_many_0(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': 0}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        request = APIRequestFactory()
        request = request.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumer.as_view()

        response = view(request, id=1).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__view__get_id__with_user__with_group_related_to_permission__consumer__how_many_1(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': 1}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        request = APIRequestFactory()
        request = request.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumer.as_view()

        response = view(request, id=1).render()
        expected = GET_ID_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    """
    🔽🔽🔽 View post
    """

    def test__view__post__anonymous_user(self):
        request = APIRequestFactory()
        request = request.post('/they-killed-kenny')

        view = TestViewConsumer.as_view()

        response = view(request).render()
        expected = {'detail': 'anonymous-user-not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__view__post__with_user(self):
        model = self.bc.database.create(user=1)

        request = APIRequestFactory()
        request = request.post('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumer.as_view()

        response = view(request).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__view__post__with_user__with_permission__dont_match(self):
        model = self.bc.database.create(user=1, permission=1)

        request = APIRequestFactory()
        request = request.post('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumer.as_view()

        response = view(request).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__view__post__with_user__with_group_related_to_permission__without_consumer(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        model = self.bc.database.create(user=user, permission=permissions, group=group)

        request = APIRequestFactory()
        request = request.post('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumer.as_view()

        response = view(request).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__view__post__with_user__with_group_related_to_permission__consumer__how_many_minus_1(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': -1}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        request = APIRequestFactory()
        request = request.post('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumer.as_view()

        response = view(request).render()
        expected = POST_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__view__post__with_user__with_group_related_to_permission__consumer__how_many_0(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': 0}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        request = APIRequestFactory()
        request = request.post('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumer.as_view()

        response = view(request).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__view__post__with_user__with_group_related_to_permission__consumer__how_many_1(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': 1}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        request = APIRequestFactory()
        request = request.post('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumer.as_view()

        response = view(request).render()
        expected = POST_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    """
    🔽🔽🔽 View put id
    """

    def test__view__put_id__anonymous_user(self):
        request = APIRequestFactory()
        request = request.put('/they-killed-kenny')

        view = TestViewConsumer.as_view()

        response = view(request, id=1).render()
        expected = {'detail': 'anonymous-user-not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__view__put_id__with_user(self):
        model = self.bc.database.create(user=1)

        request = APIRequestFactory()
        request = request.put('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumer.as_view()

        response = view(request, id=1).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__view__put_id__with_user__with_permission__dont_match(self):
        model = self.bc.database.create(user=1, permission=1)

        request = APIRequestFactory()
        request = request.put('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumer.as_view()

        response = view(request, id=1).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__view__put_id__with_user__with_group_related_to_permission__without_consumer(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        model = self.bc.database.create(user=user, permission=permissions, group=group)

        request = APIRequestFactory()
        request = request.put('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumer.as_view()

        response = view(request, id=1).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__view__put_id__with_user__with_group_related_to_permission__consumer__how_many_minus_1(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': -1}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        request = APIRequestFactory()
        request = request.put('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumer.as_view()

        response = view(request, id=1).render()
        expected = PUT_ID_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__view__put_id__with_user__with_group_related_to_permission__consumer__how_many_0(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': 0}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        request = APIRequestFactory()
        request = request.put('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumer.as_view()

        response = view(request, id=1).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__view__put_id__with_user__with_group_related_to_permission__consumer__how_many_1(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': 1}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        request = APIRequestFactory()
        request = request.put('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumer.as_view()

        response = view(request, id=1).render()
        expected = PUT_ID_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    """
    🔽🔽🔽 View delete id
    """

    def test__view__delete_id__anonymous_user(self):
        request = APIRequestFactory()
        request = request.delete('/they-killed-kenny')

        view = TestViewConsumer.as_view()

        response = view(request, id=1).render()
        expected = {'detail': 'anonymous-user-not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__view__delete_id__with_user(self):
        model = self.bc.database.create(user=1)

        request = APIRequestFactory()
        request = request.delete('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumer.as_view()

        response = view(request, id=1).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__view__delete_id__with_user__with_permission__dont_match(self):
        model = self.bc.database.create(user=1, permission=1)

        request = APIRequestFactory()
        request = request.delete('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumer.as_view()

        response = view(request, id=1).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__view__delete_id__with_user__with_group_related_to_permission__without_consumer(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        model = self.bc.database.create(user=user, permission=permissions, group=group)

        request = APIRequestFactory()
        request = request.delete('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumer.as_view()

        response = view(request, id=1).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__view__delete_id__with_user__with_group_related_to_permission__consumer__how_many_minus_1(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': -1}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        request = APIRequestFactory()
        request = request.delete('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumer.as_view()

        response = view(request, id=1).render()
        expected = DELETE_ID_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__view__delete_id__with_user__with_group_related_to_permission__consumer__how_many_0(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': 0}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        request = APIRequestFactory()
        request = request.delete('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumer.as_view()

        response = view(request, id=1).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    def test__view__delete_id__with_user__with_group_related_to_permission__consumer__how_many_1(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': 1}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        request = APIRequestFactory()
        request = request.delete('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumer.as_view()

        response = view(request, id=1).render()
        expected = DELETE_ID_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CONSUMER_MOCK.call_args_list, [])


class ConsumerCallbackViewTestSuite(UtilsTestCase):

    def setUp(self):
        super().setUp()
        CONSUMER_MOCK.call_args_list = []

    """
    🔽🔽🔽 View get
    """

    @patch('django.utils.timezone.now', MagicMock(return_value=UTC_NOW))
    def test__view__get__anonymous_user(self):
        request = APIRequestFactory()
        request = request.get('/they-killed-kenny')

        view = TestViewConsumerCallback.as_view()

        response = view(request).render()
        expected = {'detail': 'anonymous-user-not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)

        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    @patch('django.utils.timezone.now', MagicMock(return_value=UTC_NOW))
    def test__view__get__with_user(self):
        model = self.bc.database.create(user=1)

        request = APIRequestFactory()
        request = request.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumerCallback.as_view()

        response = view(request).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)

        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    @patch('django.utils.timezone.now', MagicMock(return_value=UTC_NOW))
    def test__view__get__with_user__with_permission__dont_match(self):
        model = self.bc.database.create(user=1, permission=1)

        request = APIRequestFactory()
        request = request.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumerCallback.as_view()

        response = view(request).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)

        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    @patch('django.utils.timezone.now', MagicMock(return_value=UTC_NOW))
    def test__view__get__with_user__with_group_related_to_permission__without_consumer(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        model = self.bc.database.create(user=user, permission=permissions, group=group)

        request = APIRequestFactory()
        request = request.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumerCallback.as_view()

        response = view(request).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)

        Consumable = self.bc.database.get_model('payments.Consumable')
        consumables = Consumable.objects.filter()
        self.assertEqual(len(CONSUMER_MOCK.call_args_list), 1)

        args, kwargs = CONSUMER_MOCK.call_args_list[0]
        context, args, kwargs = args

        self.assertTrue(isinstance(context['request'], Request))
        self.bc.check.partial_equality(context, {
            'utc_now': UTC_NOW,
            'consumer': CONSUMER_MOCK,
            'permission': PERMISSION,
            'consumables': consumables,
        })

        self.assertEqual(len(args), 2)
        self.assertTrue(isinstance(args[0], TestViewConsumerCallback))
        self.assertTrue(isinstance(args[1], Request))

        self.assertEqual(kwargs, {})

    @patch('django.utils.timezone.now', MagicMock(return_value=UTC_NOW))
    def test__view__get__with_user__with_group_related_to_permission__consumer__how_many_minus_1(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': -1}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        request = APIRequestFactory()
        request = request.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumerCallback.as_view()

        response = view(request).render()
        expected = GET_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        Consumable = self.bc.database.get_model('payments.Consumable')
        consumables = Consumable.objects.filter()
        self.assertEqual(len(CONSUMER_MOCK.call_args_list), 1)

        args, kwargs = CONSUMER_MOCK.call_args_list[0]
        context, args, kwargs = args

        self.assertTrue(isinstance(context['request'], Request))
        self.bc.check.partial_equality(context, {
            'utc_now': UTC_NOW,
            'consumer': CONSUMER_MOCK,
            'permission': PERMISSION,
            'consumables': consumables,
        })

        self.assertEqual(len(args), 2)
        self.assertTrue(isinstance(args[0], TestViewConsumerCallback))
        self.assertTrue(isinstance(args[1], Request))

        self.assertEqual(kwargs, {})

    @patch('django.utils.timezone.now', MagicMock(return_value=UTC_NOW))
    def test__view__get__with_user__with_group_related_to_permission__consumer__how_many_0(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': 0}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        request = APIRequestFactory()
        request = request.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumerCallback.as_view()

        response = view(request).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)

        Consumable = self.bc.database.get_model('payments.Consumable')
        consumables = Consumable.objects.filter()
        self.assertEqual(len(CONSUMER_MOCK.call_args_list), 1)

        args, kwargs = CONSUMER_MOCK.call_args_list[0]
        context, args, kwargs = args

        self.assertTrue(isinstance(context['request'], Request))
        self.bc.check.partial_equality(context, {
            'utc_now': UTC_NOW,
            'consumer': CONSUMER_MOCK,
            'permission': PERMISSION,
            'consumables': consumables,
        })

        self.assertEqual(len(args), 2)
        self.assertTrue(isinstance(args[0], TestViewConsumerCallback))
        self.assertTrue(isinstance(args[1], Request))

        self.assertEqual(kwargs, {})

    @patch('django.utils.timezone.now', MagicMock(return_value=UTC_NOW))
    def test__view__get__with_user__with_group_related_to_permission__consumer__how_many_1(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': 1}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        request = APIRequestFactory()
        request = request.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumerCallback.as_view()

        response = view(request).render()
        expected = GET_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        Consumable = self.bc.database.get_model('payments.Consumable')
        consumables = Consumable.objects.filter()
        self.assertEqual(len(CONSUMER_MOCK.call_args_list), 1)

        args, kwargs = CONSUMER_MOCK.call_args_list[0]
        context, args, kwargs = args

        self.assertTrue(isinstance(context['request'], Request))
        self.bc.check.partial_equality(context, {
            'utc_now': UTC_NOW,
            'consumer': CONSUMER_MOCK,
            'permission': PERMISSION,
            'consumables': consumables,
        })

        self.assertEqual(len(args), 2)
        self.assertTrue(isinstance(args[0], TestViewConsumerCallback))
        self.assertTrue(isinstance(args[1], Request))

        self.assertEqual(kwargs, {})

    """
    🔽🔽🔽 View get id
    """

    @patch('django.utils.timezone.now', MagicMock(return_value=UTC_NOW))
    def test__view__get_id__anonymous_user(self):
        request = APIRequestFactory()
        request = request.get('/they-killed-kenny')

        view = TestViewConsumerCallback.as_view()

        response = view(request, id=1).render()
        expected = {'detail': 'anonymous-user-not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)

        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    @patch('django.utils.timezone.now', MagicMock(return_value=UTC_NOW))
    def test__view__get_id__with_user(self):
        model = self.bc.database.create(user=1)

        request = APIRequestFactory()
        request = request.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumerCallback.as_view()

        response = view(request, id=1).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)

        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    @patch('django.utils.timezone.now', MagicMock(return_value=UTC_NOW))
    def test__view__get_id__with_user__with_permission__dont_match(self):
        model = self.bc.database.create(user=1, permission=1)

        request = APIRequestFactory()
        request = request.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumerCallback.as_view()

        response = view(request, id=1).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)

        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    @patch('django.utils.timezone.now', MagicMock(return_value=UTC_NOW))
    def test__view__get_id__with_user__with_group_related_to_permission__without_consumer(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        model = self.bc.database.create(user=user, permission=permissions, group=group)

        request = APIRequestFactory()
        request = request.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumerCallback.as_view()

        response = view(request, id=1).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)

        Consumable = self.bc.database.get_model('payments.Consumable')
        consumables = Consumable.objects.filter()
        self.assertEqual(len(CONSUMER_MOCK.call_args_list), 1)

        args, kwargs = CONSUMER_MOCK.call_args_list[0]
        context, args, kwargs = args

        self.assertTrue(isinstance(context['request'], Request))
        self.bc.check.partial_equality(context, {
            'utc_now': UTC_NOW,
            'consumer': CONSUMER_MOCK,
            'permission': PERMISSION,
            'consumables': consumables,
        })

        self.assertEqual(len(args), 2)
        self.assertTrue(isinstance(args[0], TestViewConsumerCallback))
        self.assertTrue(isinstance(args[1], Request))

        self.assertEqual(kwargs, {'id': 1})

    @patch('django.utils.timezone.now', MagicMock(return_value=UTC_NOW))
    def test__view__get_id__with_user__with_group_related_to_permission__consumer__how_many_minus_1(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': -1}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        request = APIRequestFactory()
        request = request.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumerCallback.as_view()

        response = view(request, id=1).render()
        expected = GET_ID_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        Consumable = self.bc.database.get_model('payments.Consumable')
        consumables = Consumable.objects.filter()
        self.assertEqual(len(CONSUMER_MOCK.call_args_list), 1)

        args, kwargs = CONSUMER_MOCK.call_args_list[0]
        context, args, kwargs = args

        self.assertTrue(isinstance(context['request'], Request))
        self.bc.check.partial_equality(context, {
            'utc_now': UTC_NOW,
            'consumer': CONSUMER_MOCK,
            'permission': PERMISSION,
            'consumables': consumables,
        })

        self.assertEqual(len(args), 2)
        self.assertTrue(isinstance(args[0], TestViewConsumerCallback))
        self.assertTrue(isinstance(args[1], Request))

        self.assertEqual(kwargs, {'id': 1})

    @patch('django.utils.timezone.now', MagicMock(return_value=UTC_NOW))
    def test__view__get_id__with_user__with_group_related_to_permission__consumer__how_many_0(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': 0}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        request = APIRequestFactory()
        request = request.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumerCallback.as_view()

        response = view(request, id=1).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)

        Consumable = self.bc.database.get_model('payments.Consumable')
        consumables = Consumable.objects.filter()
        self.assertEqual(len(CONSUMER_MOCK.call_args_list), 1)

        args, kwargs = CONSUMER_MOCK.call_args_list[0]
        context, args, kwargs = args

        self.assertTrue(isinstance(context['request'], Request))
        self.bc.check.partial_equality(context, {
            'utc_now': UTC_NOW,
            'consumer': CONSUMER_MOCK,
            'permission': PERMISSION,
            'consumables': consumables,
        })

        self.assertEqual(len(args), 2)
        self.assertTrue(isinstance(args[0], TestViewConsumerCallback))
        self.assertTrue(isinstance(args[1], Request))

        self.assertEqual(kwargs, {'id': 1})

    @patch('django.utils.timezone.now', MagicMock(return_value=UTC_NOW))
    def test__view__get_id__with_user__with_group_related_to_permission__consumer__how_many_1(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': 1}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        request = APIRequestFactory()
        request = request.get('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumerCallback.as_view()

        response = view(request, id=1).render()
        expected = GET_ID_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        Consumable = self.bc.database.get_model('payments.Consumable')
        consumables = Consumable.objects.filter()
        self.assertEqual(len(CONSUMER_MOCK.call_args_list), 1)

        args, kwargs = CONSUMER_MOCK.call_args_list[0]
        context, args, kwargs = args

        self.assertTrue(isinstance(context['request'], Request))
        self.bc.check.partial_equality(context, {
            'utc_now': UTC_NOW,
            'consumer': CONSUMER_MOCK,
            'permission': PERMISSION,
            'consumables': consumables,
        })

        self.assertEqual(len(args), 2)
        self.assertTrue(isinstance(args[0], TestViewConsumerCallback))
        self.assertTrue(isinstance(args[1], Request))

        self.assertEqual(kwargs, {'id': 1})

    """
    🔽🔽🔽 View post
    """

    @patch('django.utils.timezone.now', MagicMock(return_value=UTC_NOW))
    def test__view__post__anonymous_user(self):
        request = APIRequestFactory()
        request = request.post('/they-killed-kenny')

        view = TestViewConsumerCallback.as_view()

        response = view(request).render()
        expected = {'detail': 'anonymous-user-not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)

        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    @patch('django.utils.timezone.now', MagicMock(return_value=UTC_NOW))
    def test__view__post__with_user(self):
        model = self.bc.database.create(user=1)

        request = APIRequestFactory()
        request = request.post('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumerCallback.as_view()

        response = view(request).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)

        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    @patch('django.utils.timezone.now', MagicMock(return_value=UTC_NOW))
    def test__view__post__with_user__with_permission__dont_match(self):
        model = self.bc.database.create(user=1, permission=1)

        request = APIRequestFactory()
        request = request.post('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumerCallback.as_view()

        response = view(request).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)

        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    @patch('django.utils.timezone.now', MagicMock(return_value=UTC_NOW))
    def test__view__post__with_user__with_group_related_to_permission__without_consumer(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        model = self.bc.database.create(user=user, permission=permissions, group=group)

        request = APIRequestFactory()
        request = request.post('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumerCallback.as_view()

        response = view(request).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)

        Consumable = self.bc.database.get_model('payments.Consumable')
        consumables = Consumable.objects.filter()
        self.assertEqual(len(CONSUMER_MOCK.call_args_list), 1)

        args, kwargs = CONSUMER_MOCK.call_args_list[0]
        context, args, kwargs = args

        self.assertTrue(isinstance(context['request'], Request))
        self.bc.check.partial_equality(context, {
            'utc_now': UTC_NOW,
            'consumer': CONSUMER_MOCK,
            'permission': PERMISSION,
            'consumables': consumables,
        })

        self.assertEqual(len(args), 2)
        self.assertTrue(isinstance(args[0], TestViewConsumerCallback))
        self.assertTrue(isinstance(args[1], Request))

        self.assertEqual(kwargs, {})

    @patch('django.utils.timezone.now', MagicMock(return_value=UTC_NOW))
    def test__view__post__with_user__with_group_related_to_permission__consumer__how_many_minus_1(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': -1}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        request = APIRequestFactory()
        request = request.post('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumerCallback.as_view()

        response = view(request).render()
        expected = POST_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        Consumable = self.bc.database.get_model('payments.Consumable')
        consumables = Consumable.objects.filter()
        self.assertEqual(len(CONSUMER_MOCK.call_args_list), 1)

        args, kwargs = CONSUMER_MOCK.call_args_list[0]
        context, args, kwargs = args

        self.assertTrue(isinstance(context['request'], Request))
        self.bc.check.partial_equality(context, {
            'utc_now': UTC_NOW,
            'consumer': CONSUMER_MOCK,
            'permission': PERMISSION,
            'consumables': consumables,
        })

        self.assertEqual(len(args), 2)
        self.assertTrue(isinstance(args[0], TestViewConsumerCallback))
        self.assertTrue(isinstance(args[1], Request))

        self.assertEqual(kwargs, {})

    @patch('django.utils.timezone.now', MagicMock(return_value=UTC_NOW))
    def test__view__post__with_user__with_group_related_to_permission__consumer__how_many_0(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': 0}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        request = APIRequestFactory()
        request = request.post('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumerCallback.as_view()

        response = view(request).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)

        Consumable = self.bc.database.get_model('payments.Consumable')
        consumables = Consumable.objects.filter()
        self.assertEqual(len(CONSUMER_MOCK.call_args_list), 1)

        args, kwargs = CONSUMER_MOCK.call_args_list[0]
        context, args, kwargs = args

        self.assertTrue(isinstance(context['request'], Request))
        self.bc.check.partial_equality(context, {
            'utc_now': UTC_NOW,
            'consumer': CONSUMER_MOCK,
            'permission': PERMISSION,
            'consumables': consumables,
        })

        self.assertEqual(len(args), 2)
        self.assertTrue(isinstance(args[0], TestViewConsumerCallback))
        self.assertTrue(isinstance(args[1], Request))

        self.assertEqual(kwargs, {})

    @patch('django.utils.timezone.now', MagicMock(return_value=UTC_NOW))
    def test__view__post__with_user__with_group_related_to_permission__consumer__how_many_1(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': 1}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        request = APIRequestFactory()
        request = request.post('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumerCallback.as_view()

        response = view(request).render()
        expected = POST_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        Consumable = self.bc.database.get_model('payments.Consumable')
        consumables = Consumable.objects.filter()
        self.assertEqual(len(CONSUMER_MOCK.call_args_list), 1)

        args, kwargs = CONSUMER_MOCK.call_args_list[0]
        context, args, kwargs = args

        self.assertTrue(isinstance(context['request'], Request))
        self.bc.check.partial_equality(context, {
            'utc_now': UTC_NOW,
            'consumer': CONSUMER_MOCK,
            'permission': PERMISSION,
            'consumables': consumables,
        })

        self.assertEqual(len(args), 2)
        self.assertTrue(isinstance(args[0], TestViewConsumerCallback))
        self.assertTrue(isinstance(args[1], Request))

        self.assertEqual(kwargs, {})

    """
    🔽🔽🔽 View put id
    """

    @patch('django.utils.timezone.now', MagicMock(return_value=UTC_NOW))
    def test__view__put_id__anonymous_user(self):
        request = APIRequestFactory()
        request = request.put('/they-killed-kenny')

        view = TestViewConsumerCallback.as_view()

        response = view(request, id=1).render()
        expected = {'detail': 'anonymous-user-not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)

        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    @patch('django.utils.timezone.now', MagicMock(return_value=UTC_NOW))
    def test__view__put_id__with_user(self):
        model = self.bc.database.create(user=1)

        request = APIRequestFactory()
        request = request.put('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumerCallback.as_view()

        response = view(request, id=1).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)

        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    @patch('django.utils.timezone.now', MagicMock(return_value=UTC_NOW))
    def test__view__put_id__with_user__with_permission__dont_match(self):
        model = self.bc.database.create(user=1, permission=1)

        request = APIRequestFactory()
        request = request.put('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumerCallback.as_view()

        response = view(request, id=1).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)

        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    @patch('django.utils.timezone.now', MagicMock(return_value=UTC_NOW))
    def test__view__put_id__with_user__with_group_related_to_permission__without_consumer(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        model = self.bc.database.create(user=user, permission=permissions, group=group)

        request = APIRequestFactory()
        request = request.put('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumerCallback.as_view()

        response = view(request, id=1).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)

        Consumable = self.bc.database.get_model('payments.Consumable')
        consumables = Consumable.objects.filter()
        self.assertEqual(len(CONSUMER_MOCK.call_args_list), 1)

        args, kwargs = CONSUMER_MOCK.call_args_list[0]
        context, args, kwargs = args

        self.assertTrue(isinstance(context['request'], Request))
        self.bc.check.partial_equality(context, {
            'utc_now': UTC_NOW,
            'consumer': CONSUMER_MOCK,
            'permission': PERMISSION,
            'consumables': consumables,
        })

        self.assertEqual(len(args), 2)
        self.assertTrue(isinstance(args[0], TestViewConsumerCallback))
        self.assertTrue(isinstance(args[1], Request))

        self.assertEqual(kwargs, {'id': 1})

    @patch('django.utils.timezone.now', MagicMock(return_value=UTC_NOW))
    def test__view__put_id__with_user__with_group_related_to_permission__consumer__how_many_minus_1(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': -1}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        request = APIRequestFactory()
        request = request.put('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumerCallback.as_view()

        response = view(request, id=1).render()
        expected = PUT_ID_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        Consumable = self.bc.database.get_model('payments.Consumable')
        consumables = Consumable.objects.filter()
        self.assertEqual(len(CONSUMER_MOCK.call_args_list), 1)

        args, kwargs = CONSUMER_MOCK.call_args_list[0]
        context, args, kwargs = args

        self.assertTrue(isinstance(context['request'], Request))
        self.bc.check.partial_equality(context, {
            'utc_now': UTC_NOW,
            'consumer': CONSUMER_MOCK,
            'permission': PERMISSION,
            'consumables': consumables,
        })

        self.assertEqual(len(args), 2)
        self.assertTrue(isinstance(args[0], TestViewConsumerCallback))
        self.assertTrue(isinstance(args[1], Request))

        self.assertEqual(kwargs, {'id': 1})

    @patch('django.utils.timezone.now', MagicMock(return_value=UTC_NOW))
    def test__view__put_id__with_user__with_group_related_to_permission__consumer__how_many_0(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': 0}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        request = APIRequestFactory()
        request = request.put('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumerCallback.as_view()

        response = view(request, id=1).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)

        Consumable = self.bc.database.get_model('payments.Consumable')
        consumables = Consumable.objects.filter()
        self.assertEqual(len(CONSUMER_MOCK.call_args_list), 1)

        args, kwargs = CONSUMER_MOCK.call_args_list[0]
        context, args, kwargs = args

        self.assertTrue(isinstance(context['request'], Request))
        self.bc.check.partial_equality(context, {
            'utc_now': UTC_NOW,
            'consumer': CONSUMER_MOCK,
            'permission': PERMISSION,
            'consumables': consumables,
        })

        self.assertEqual(len(args), 2)
        self.assertTrue(isinstance(args[0], TestViewConsumerCallback))
        self.assertTrue(isinstance(args[1], Request))

        self.assertEqual(kwargs, {'id': 1})

    @patch('django.utils.timezone.now', MagicMock(return_value=UTC_NOW))
    def test__view__put_id__with_user__with_group_related_to_permission__consumer__how_many_1(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': 1}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        request = APIRequestFactory()
        request = request.put('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumerCallback.as_view()

        response = view(request, id=1).render()
        expected = PUT_ID_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        Consumable = self.bc.database.get_model('payments.Consumable')
        consumables = Consumable.objects.filter()
        self.assertEqual(len(CONSUMER_MOCK.call_args_list), 1)

        args, kwargs = CONSUMER_MOCK.call_args_list[0]
        context, args, kwargs = args

        self.assertTrue(isinstance(context['request'], Request))
        self.bc.check.partial_equality(context, {
            'utc_now': UTC_NOW,
            'consumer': CONSUMER_MOCK,
            'permission': PERMISSION,
            'consumables': consumables,
        })

        self.assertEqual(len(args), 2)
        self.assertTrue(isinstance(args[0], TestViewConsumerCallback))
        self.assertTrue(isinstance(args[1], Request))

        self.assertEqual(kwargs, {'id': 1})

    """
    🔽🔽🔽 View delete id
    """

    @patch('django.utils.timezone.now', MagicMock(return_value=UTC_NOW))
    def test__view__delete_id__anonymous_user(self):
        request = APIRequestFactory()
        request = request.delete('/they-killed-kenny')

        view = TestViewConsumerCallback.as_view()

        response = view(request, id=1).render()
        expected = {'detail': 'anonymous-user-not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)

        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    @patch('django.utils.timezone.now', MagicMock(return_value=UTC_NOW))
    def test__view__delete_id__with_user(self):
        model = self.bc.database.create(user=1)

        request = APIRequestFactory()
        request = request.delete('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumerCallback.as_view()

        response = view(request, id=1).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)

        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    @patch('django.utils.timezone.now', MagicMock(return_value=UTC_NOW))
    def test__view__delete_id__with_user__with_permission__dont_match(self):
        model = self.bc.database.create(user=1, permission=1)

        request = APIRequestFactory()
        request = request.delete('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumerCallback.as_view()

        response = view(request, id=1).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)

        self.assertEqual(CONSUMER_MOCK.call_args_list, [])

    @patch('django.utils.timezone.now', MagicMock(return_value=UTC_NOW))
    def test__view__delete_id__with_user__with_group_related_to_permission__without_consumer(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        model = self.bc.database.create(user=user, permission=permissions, group=group)

        request = APIRequestFactory()
        request = request.delete('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumerCallback.as_view()

        response = view(request, id=1).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)

        Consumable = self.bc.database.get_model('payments.Consumable')
        consumables = Consumable.objects.filter()
        self.assertEqual(len(CONSUMER_MOCK.call_args_list), 1)

        args, kwargs = CONSUMER_MOCK.call_args_list[0]
        context, args, kwargs = args

        self.assertTrue(isinstance(context['request'], Request))
        self.bc.check.partial_equality(context, {
            'utc_now': UTC_NOW,
            'consumer': CONSUMER_MOCK,
            'permission': PERMISSION,
            'consumables': consumables,
        })

        self.assertEqual(len(args), 2)
        self.assertTrue(isinstance(args[0], TestViewConsumerCallback))
        self.assertTrue(isinstance(args[1], Request))

        self.assertEqual(kwargs, {'id': 1})

    @patch('django.utils.timezone.now', MagicMock(return_value=UTC_NOW))
    def test__view__delete_id__with_user__with_group_related_to_permission__consumer__how_many_minus_1(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': -1}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        request = APIRequestFactory()
        request = request.delete('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumerCallback.as_view()

        response = view(request, id=1).render()
        expected = DELETE_ID_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        Consumable = self.bc.database.get_model('payments.Consumable')
        consumables = Consumable.objects.filter()
        self.assertEqual(len(CONSUMER_MOCK.call_args_list), 1)

        args, kwargs = CONSUMER_MOCK.call_args_list[0]
        context, args, kwargs = args

        self.assertTrue(isinstance(context['request'], Request))
        self.bc.check.partial_equality(context, {
            'utc_now': UTC_NOW,
            'consumer': CONSUMER_MOCK,
            'permission': PERMISSION,
            'consumables': consumables,
        })

        self.assertEqual(len(args), 2)
        self.assertTrue(isinstance(args[0], TestViewConsumerCallback))
        self.assertTrue(isinstance(args[1], Request))

        self.assertEqual(kwargs, {'id': 1})

    @patch('django.utils.timezone.now', MagicMock(return_value=UTC_NOW))
    def test__view__delete_id__with_user__with_group_related_to_permission__consumer__how_many_0(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': 0}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        request = APIRequestFactory()
        request = request.delete('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumerCallback.as_view()

        response = view(request, id=1).render()
        expected = {'detail': 'not-enough-consumables', 'status_code': 402}

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)

        Consumable = self.bc.database.get_model('payments.Consumable')
        consumables = Consumable.objects.filter()
        self.assertEqual(len(CONSUMER_MOCK.call_args_list), 1)

        args, kwargs = CONSUMER_MOCK.call_args_list[0]
        context, args, kwargs = args

        self.assertTrue(isinstance(context['request'], Request))
        self.bc.check.partial_equality(context, {
            'utc_now': UTC_NOW,
            'consumer': CONSUMER_MOCK,
            'permission': PERMISSION,
            'consumables': consumables,
        })

        self.assertEqual(len(args), 2)
        self.assertTrue(isinstance(args[0], TestViewConsumerCallback))
        self.assertTrue(isinstance(args[1], Request))

        self.assertEqual(kwargs, {'id': 1})

    @patch('django.utils.timezone.now', MagicMock(return_value=UTC_NOW))
    def test__view__delete_id__with_user__with_group_related_to_permission__consumer__how_many_1(self):
        user = {'user_permissions': []}
        permissions = [{}, {'codename': PERMISSION}]
        group = {'permission_id': 2}
        consumable = {'how_many': 1}
        model = self.bc.database.create(user=user, permission=permissions, group=group, consumable=consumable)

        request = APIRequestFactory()
        request = request.delete('/they-killed-kenny')
        force_authenticate(request, user=model.user)

        view = TestViewConsumerCallback.as_view()

        response = view(request, id=1).render()
        expected = DELETE_ID_RESPONSE

        self.assertEqual(json.loads(response.content.decode('utf-8')), expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        Consumable = self.bc.database.get_model('payments.Consumable')
        consumables = Consumable.objects.filter()
        self.assertEqual(len(CONSUMER_MOCK.call_args_list), 1)

        args, kwargs = CONSUMER_MOCK.call_args_list[0]
        context, args, kwargs = args

        self.assertTrue(isinstance(context['request'], Request))
        self.bc.check.partial_equality(context, {
            'utc_now': UTC_NOW,
            'consumer': CONSUMER_MOCK,
            'permission': PERMISSION,
            'consumables': consumables,
        })

        self.assertEqual(len(args), 2)
        self.assertTrue(isinstance(args[0], TestViewConsumerCallback))
        self.assertTrue(isinstance(args[1], Request))

        self.assertEqual(kwargs, {'id': 1})
