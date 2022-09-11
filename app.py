from flask import Flask, request
from flask.json import jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager

from http import HTTPStatus

from config import Config

app = Flask(__name__)

# 환경 변수 세팅
app.config.from_object(Config)

# JWT 토큰 만들기
jwt = JWTManager(app)

# 로그아웃한 유저의 jti를 확인하는 코드 
# todo 로그아웃 관련 리소스 생성 후 주석 해제
# @jwt.token_in_blocklist_loader
# def check_if_token_is_revoked(jwt_header, jwt_payload) :
#     # jti = jwt_payload['jti']
#     # return jti in jwt_blacklist
#     jti = jwt_payload['jti']
#     result = check_blocklist(jti)
    
#     return result


api = Api(app)

# resources 와 연결 
# todo 리소스 생성완료시 하나씩 주석 해재해서 테스트하기

# api.add_resource(UserRegisterResource, '/v1/user/register')
# api.add_resource(UserLoginResource, '/v1/user/login')
# api.add_resource(LogoutResource, '/v1/user/logout')
# api.add_resource(MemoListResource, '/v1/memo')
# api.add_resource(MemoResource, '/v1/memo/<int:memo_id>')



@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


if __name__ == "__main__" :
    app.run()