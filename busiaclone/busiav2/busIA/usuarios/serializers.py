"""
Serializadores para el modelo Usuario.
Maneja la conversión entre objetos Python y JSON para la API.
"""

from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Usuario

class UsuarioSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo Usuario.
    Convierte instancias de Usuario a JSON y viceversa.
    
    Fields:
        id: ID único del usuario
        email: Correo electrónico del usuario
        nombre: Nombre completo del usuario
        fecha_registro: Fecha de creación de la cuenta
    """
    class Meta:
        model = Usuario
        fields = ('id', 'email', 'nombre', 'fecha_registro')
        read_only_fields = ('id', 'fecha_registro')

class RegistroUsuarioSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = Usuario
        fields = ('email', 'nombre', 'password', 'password2')
        extra_kwargs = {
            'password': {'write_only': True, 'required': True},
            'nombre': {'required': True},
            'email': {'required': True}
        }
    
    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e))
        return value
    
    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({
                'password2': 'Las contraseñas no coinciden'
            })
        return data
    
    def create(self, validated_data):
        validated_data.pop('password2')
        usuario = Usuario.objects.create_user(**validated_data)
        return usuario

class ResetPasswordEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

class ResetPasswordConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField()
    new_password2 = serializers.CharField()
    
    def validate(self, data):
        if data['new_password'] != data['new_password2']:
            raise serializers.ValidationError({
                'new_password2': 'Las contraseñas no coinciden'
            })
            
        try:
            validate_password(data['new_password'])
        except ValidationError as e:
            raise serializers.ValidationError({
                'new_password': list(e)
            })
            
        return data

class CambioPasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()
    
    def validate_new_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e))
        return value

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        data['access'] = str(refresh.access_token)
        data['refresh'] = str(refresh)
        data['user'] = UsuarioSerializer(self.user).data
        return data