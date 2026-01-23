from rest_framework import serializers
from .models import Category, Product, Order, Review, Brand

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    class Meta:
        model = Product
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    class Meta:
        model = Review
        fields = '__all__'

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    items = serializers.StringRelatedField(many=True)
    class Meta:
        model = Order
        fields = '__all__'
