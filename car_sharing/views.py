from rest_framework.generics import get_object_or_404
from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.http import HttpResponse, JsonResponse
from rest_framework_jwt.settings import api_settings
from websocket import create_connection
import json

from .models import Car, Order
from django.contrib.auth.models import User
from .serializers import CarSerializer, OrderSerializer, UserSerializer, jwt_response_payload_handler


def index(request):
    return HttpResponse('Намана')


class OrderView(APIView):
    def get(self, request):
        orders = Order.objects.all()
        serializer = OrderSerializer(instance=orders, many=True)
        return Response({"orders": serializer.data})

    def post(self, request):
        order = request.data.get('order')
        serializer = OrderSerializer(data=order)
        if serializer.is_valid(raise_exception=True):
            order_save = serializer.save()
        return Response({"success": "Order '{}' create successfully".format(order_save.id)})


class CarView(APIView):
    def get(self, request):
        cars = Car.objects.all()
        serializer = CarSerializer(cars, many=True)
        return Response({"cars": serializer.data})

    def post(self, request):
        car = request.data
        serializer = CarSerializer(data=car)
        if serializer.is_valid(raise_exception=True):
            car_saved = serializer.save()
        return Response({"success": "Car '{}' create successfully".format(car_saved.model)})

    def put(self, request, pk):
        saved_car = get_object_or_404(Car.objects.all(), pk=pk)
        data = request.data
        serializer = CarSerializer(instance=saved_car, data=data, partial=True)

        if serializer.is_valid(raise_exception=True):
            car_saved = serializer.save()

        return Response({"success": "Car '{}' update successfully".format(car_saved.model)})

    def delete(self, request, pk):
        car = get_object_or_404(Car.objects.all(), pk=pk)
        car.delete()
        return Response({"message": "Car with id `{}` has been deleted.".format(pk)}, status=204)


class CarList(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    queryset = Car.objects.all()
    serializer_class = CarSerializer

    def get(self, request, *args, **kwargs):
        web_socket(self)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        web_socket(self)
        return response

    def get_queryset(self):
        querystring = self.request.query_params.get('q')

        if querystring is not None:
            return Car.objects.filter(model__icontains=querystring)

        return Car.objects.all()


class CarDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [AllowAny]
    queryset = Car.objects.all()
    serializer_class = CarSerializer

    def put(self, request, *args, **kwargs):
        response = super().put(request, *args, **kwargs)
        web_socket(self)
        return response

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        web_socket(self)
        return response


class UserList(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class OauthVK(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = User.objects.create_user(email, email, User.objects.make_random_password())

        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        return Response(data=jwt_response_payload_handler(token, user), status=status.HTTP_200_OK, )



class VkHook(APIView):
    queryset = Car.objects.all()
    permission_classes = [AllowAny]

    def post(self, request):
        if request.data.get('type') == "confirmation" and request.data.get("group_id") == 188729360:
            return HttpResponse('df7968cb')

        label = request.data.get('object').get('body').split('\n')
        car = {"model": label[0], "price": label[1]}
        serializer = CarSerializer(data=car)
        if serializer.is_valid(raise_exception=True):
            car_saved = serializer.save()

        ws = create_connection("wss://web-socket-server-lab.herokuapp.com/")
        ws.send(json.dumps({
            "messageType": "vkHook",
            "data": request.data
        }))
        ws.close()

        ws = create_connection("wss://web-socket-server-lab.herokuapp.com/")
        ws.send(json.dumps({
            "messageType": "data",
            "cars": CarSerializer(Car.objects.all(), many=True).data
        }))
        ws.close()

        # serializer = CarSerializer(data=car)
        # if serializer.is_valid(raise_exception=True):
        #     car_saved = serializer.save()

        return HttpResponse('ok', content_type="text/plain", status=200)



def web_socket(self):
    ws = create_connection("wss://web-socket-server-lab.herokuapp.com/")
    ws.send(json.dumps({
        "messageType": "data",
        "cars": CarSerializer(self.get_queryset(), many=True).data
    }))
    ws.close()