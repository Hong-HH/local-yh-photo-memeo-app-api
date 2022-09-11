from flask import request
from flask_restful import Resource
from http import HTTPStatus
from mysql.connector.errors import Error
# 내가만든 커넥션 함수 임포트
from mysql_connection import get_connection
from email_validator import validate_email, EmailNotValidError

from flask_jwt_extended import create_access_token

from utils import hash_password

class UserRegisterResource(Resource) :
    def post(self) :
        # 1. 클라이언트가 보내준, 회원정보 받아온다.
        data = request.get_json()
        # {
        #     "email": "abc@naver.com",
        #     "password" : "123456",
        #     "nick_name" : "춘식"
        # }
        # 2. 이메일 주소가 제대로 된 주소인지 확인하는 코드
        #    잘못된 이메일 주소면, 잘못되었다고 응답한다.
        try:
            # Validate.
            validate_email(data['email'])

        except EmailNotValidError as e:
            # email is not valid, exception message is human-readable
            print(str(e))
            return {'status' : 400 , 'message' : '이메일 주소가 잘못되었습니다.'} 


        # 3. 비밀번호 길이 같은 조건이 있는지 확인하는 코드
        #    잘못되었으면, 클라이언트에 응답한다.
        if len(data['password']) < 4 or  len(data['password']) > 10 :
            return {'status' : 400, 'message' : '비밀번호의 길이를 확인하세요'}


        # 4. 비밀번호를 암호화한다.
        hashed_password = hash_password(data['password'])
        
        print('암호화된 비번길이 : ', str(len(data['password'])) )
        
        
        try : 
            # 1. DB에 연결
            connection = get_connection()

        except Error as e:
            print('Error', e)

            return {'status' : 500 , 'message' : 'db연결에 실패했습니다.'} 
        
        # 이메일이 중복인지 확인하기
        try :
            print("connection is connected and check email is unique")
            query = '''select * 
                        from user
                        where email = %s; '''
            
            param = (data["email"], )
            
            cursor = connection.cursor(dictionary = True)

            cursor.execute(query, param)

            # select 문은 아래 내용이 필요하다.
            record_list = cursor.fetchall()
            print(record_list)

            if len( record_list ) == 1 :
                return {'status' : 400 , 'message' : '이미 계정이 있습니다.'}
    
            
        # 위의 코드를 실행하다가, 문제가 생기면, except를 실행하라는 뜻.
        except Error as e :
            print('Error while connecting to MySQL', e)
            return {'status' : 500, 'message' : str(e)} 
        
        # 닉네임이 중복인지 확인하기
        try :
            print("connection is connected and check nick_name is unique")
            query = '''select * 
                        from user
                        where nick_name = %s; '''
            
            param = (data["nick_name"], )
            
            cursor = connection.cursor(dictionary = True)

            cursor.execute(query, param)

            # select 문은 아래 내용이 필요하다.
            record_list = cursor.fetchall()
            print(record_list)

            if len( record_list ) == 1 :
                return {'status' : 400 , 'message' : '해당 닉네임은 이미 존재합니다.'}
    
            
        # 위의 코드를 실행하다가, 문제가 생기면, except를 실행하라는 뜻.
        except Error as e :
            print('Error while connecting to MySQL', e)
            return {'status' : 500, 'message' : str(e)} 


        # 5. 데이터를 db에 저장한다.
        try :
            query = '''insert into user
                (nick_name, email, password)
                values
                (%s,%s,%s);'''
            # 파이썬에서, 튜플만들때, 데이터가 1개인 경우에는 콤마를 꼭 써주자.
            record = [data['nick_name'], data['email'], hashed_password]
            # 3. 커넥션으로부터 커서를 가져온다.
            cursor = connection.cursor()

            # 4. 쿼리문을 커서에 넣어서 실행한다. // 실제로 실행하는 것은 커서가 해준다.
            # 레코드는 직접입력말고 변수로 넣었을때 실행
            cursor.execute(query, record)

            # 5. 커넥션을 커밋한다. => 디비에 영구적으로 반영하라는 뜻.
            connection.commit()
            # 디비에 저장된 유저의 아이디를 가져온다.
            user_id = cursor.lastrowid

            print("유저아이디 {} 회원가입 완료".format(str(user_id)))
            
        except Error as e:
            print('Error', e)
            return {'status' : 500, 'message' : str(e)} 
        # finally는 필수는 아니다.
        finally :
            if connection.is_connected():
                cursor.close()
                connection.close()
                print('MySQL connection is closed')
            else :
                print('MySQL connection failed connect')

        # 7. JWT 토큰을 발행한다.
        ### DB에 저장된 유저 아이디 값으로 토큰을 발행한다!
        # flask_jwt_extended의 api 문서를 기반으로 access_token이 만료되지 않게 설정하였다.
        access_token = create_access_token(user_id, expires_delta=False)

        # 8. 모든것이 정상이면, 회원가입 잘 되었다고 응답한다. 
        return {'status' : 200 , 'message' : access_token}