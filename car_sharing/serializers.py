from rest_framework import serializers

from .models import Car, Order
from django.contrib.auth.models import User

class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = ['id', 'model', 'price', 'status', 'start_use_date', 'end_use_date', 'order']

    def create(self, validated_data):
        return Car.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.model = validated_data.get('model', instance.model)
        instance.price = validated_data.get('price', instance.price)
        instance.status = validated_data.get('status', instance.status)
        instance.start_use_date = validated_data.get('start_use_date', instance.start_use_date)
        instance.end_use_date = validated_data.get('end_use_date', instance.end_use_date)
        instance.order = validated_data.get('order', instance.order)

        instance.save()
        return instance

class OrderSerializer(serializers.ModelSerializer):
    cars = CarSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'comment', 'cars']

    def create(self, validated_data):
        cars_data = validated_data.pop('cars')
        order = Order.objects.create(**validated_data)
        for car_data in cars_data:
            Car.objects.create(order=order, **car_data)
        return order


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'is_staff')

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token': token,
        'is_staff': UserSerializer(user, context={'request': request}).data['is_staff']
    }