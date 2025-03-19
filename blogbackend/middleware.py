import jwt
from django.http import JsonResponse
from django.conf import settings
from datetime import datetime, timedelta
from django.contrib.auth.models import User 
from rest_framework_simplejwt.tokens import RefreshToken 

class CheckAccessTokenMiddleware:
    """
    Middleware to check if access_token and refresh_token are available in the request headers,
    but skip checks for signup and signin URLs.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path in ['/signup/', '/signin/']: 
            return self.get_response(request)

        access_token = request.headers.get('Authorization')
        refresh_token = request.headers.get('Refresh-Token')  
        
        print(f"Access Token: {access_token}")
        print(f"Refresh Token: {refresh_token}")

        if not access_token or not access_token.startswith('Bearer '):
            return JsonResponse(
                {'error': 'Access token missing or invalid'},
                status=401
            )

        try:
            print("Token format correct. Extracting the token...")
            token = access_token.split(' ')[1]  
            print(f"Extracted Token: {token}")

            decoded_token = self.decode_access_token(token)
            print(f"Decoded Token: {decoded_token}")
            
            user_id = decoded_token.get('id') 
            print(f"User ID from token: {user_id}")

            if not user_id:
                return JsonResponse(
                    {'error': 'User ID not found in access token'},
                    status=401
                )

         
            request.user_id = user_id

        except jwt.ExpiredSignatureError:
            print("Access token expired, attempting to refresh...")
            if not refresh_token:
                return JsonResponse({'error': 'Refresh token missing, cannot refresh access token'}, status=401)
            
            try:
                decoded_refresh_token = self.decode_refresh_token(refresh_token)
                print(decoded_refresh_token)
                new_access_token = self.generate_new_access_token(refresh_token)
                return JsonResponse({'access_token': new_access_token}, status=200)

            except Exception as e:
                return JsonResponse({'error': f'Failed to refresh access token: {str(e)}'}, status=401)
        
        except Exception as e:
            print(f"Error: {str(e)}")
            return JsonResponse({'error': f'Invalid access token: {str(e)}'}, status=401)

      
        if refresh_token:
            try:
                self.validate_refresh_token(refresh_token)  
            except Exception as e:
                return JsonResponse({'error': f'Invalid refresh token: {str(e)}'}, status=401)

       
        response = self.get_response(request)
        return response

    def decode_access_token(self, token):
        """
        Decode the access token (JWT) and return the decoded information.
        Assumes the token is a JWT and includes a 'secret' for verification.
        """
        try:
            print("Attempting to decode the token...")

            SECRET_KEY = 'secret' 
            decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"], options={"verify_exp": True})  

            print(f"Decoded Token: {decoded}")

            return decoded
        except jwt.ExpiredSignatureError:
            raise jwt.ExpiredSignatureError("Access token has expired")
        except jwt.InvalidTokenError as e:
            raise jwt.InvalidTokenError(f"Invalid access token: {str(e)}")

    def decode_refresh_token(self, refresh_token):
        """
        Decode the refresh token (JWT) and return the decoded information.
        Assumes the token is a JWT and includes a 'secret' for verification.
        """
        try:
            print("Attempting to decode the refresh token...")
            print(refresh_token)
            refreshtoken = refresh_token.split(' ')[1]  
            print(f"Extracted Token: {refreshtoken}")

            SECRET_KEY = 'secret' 
            decoded = jwt.decode(refreshtoken, SECRET_KEY, algorithms=["HS256"], options={"verify_exp": True})

            print(f"Decoded Refresh Token: {decoded}")

            return decoded
        except jwt.ExpiredSignatureError:
            raise jwt.ExpiredSignatureError("Refresh token has expired")
        except jwt.InvalidTokenError as e:
            raise jwt.InvalidTokenError(f"Invalid refresh token: {str(e)}")

    def generate_new_access_token(self, refresh_token):
        """
        Generate a new access token from the refresh token.
        Extract user information (like user_id) from the refresh token and generate a new access token.
        """
        try:
            refreshtoken = refresh_token.split(' ')[1] 
            print(f"Extracted Token: {refreshtoken}")
            
            
            SECRET_KEY = 'secret'
            decoded_refresh_token = jwt.decode(refreshtoken,SECRET_KEY, algorithms=["HS256"])

            user_id = decoded_refresh_token.get('id')
            if not user_id:
                raise Exception("Invalid refresh token: User ID missing")

            user_role = decoded_refresh_token.get('role', None) 
            SECRET_KEY = 'secret'

            new_access_token = jwt.encode(
                {
                    'id': user_id, 
                    'role': user_role, 
                    'exp': datetime.utcnow() + timedelta(minutes=1), 
                    'iat': datetime.utcnow()
                },
                SECRET_KEY, 
                algorithm="HS256"
            )
            print(f"new_access_token: {new_access_token}")
            return new_access_token

        except jwt.ExpiredSignatureError:
            raise Exception("The refresh token has expired.")
        except jwt.InvalidTokenError:
            raise Exception("Invalid refresh token.")

    def validate_refresh_token(self, refresh_token):
        """
        Validates the refresh token.
        """
        try:
            decoded_refresh_token = self.decode_refresh_token(refresh_token)
        except Exception as e:
            raise Exception(f"Invalid refresh token: {str(e)}")
