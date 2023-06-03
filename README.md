# MyGallery


🤗 배포
------
> [My Little Gallery](https://mylittlegallery.netlify.app/)

📚 stacks 
------

<img src="https://img.shields.io/badge/python 3.8.6 -3776AB?style=for-the-badge&logo=python&logoColor=white">  <img src="https://img.shields.io/badge/django 4.2.1-092E20?style=for-the-badge&logo=django&logoColor=white">  <img src="https://img.shields.io/badge/djangorestframework 3.14.0-092E20?style=for-the-badge&logo=django&logoColor=white"> <img src="https://img.shields.io/badge/opencv 4.7.0.-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white">
 <br> <img src="https://img.shields.io/badge/html5-E34F26?style=for-the-badge&logo=html5&logoColor=white">  <img src="https://img.shields.io/badge/javascript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black"> <br>  <img src="https://img.shields.io/badge/mysql-4479A1?style=for-the-badge&logo=mysql&logoColor=white">  <img src="https://img.shields.io/badge/amazonec2-FF9900?style=for-the-badge&logo=amazonec2&logoColor=white"> <img src="https://img.shields.io/badge/amazonrds-527FFF?style=for-the-badge&logo=amazonrds&logoColor=white"> <img src="https://img.shields.io/badge/gunicorn-499848?style=for-the-badge&logo=gunicorn&logoColor=white"> <img src="https://img.shields.io/badge/nginx 1.18.0-009639?style=for-the-badge&logo=nginx&logoColor=white">


***

💖 머신러닝 프로젝트 : 나만의 갤러리 SNS 만들기 🖼️
------
> 2023.05.22 ~ 2023.05.29
  
머신러닝 프로젝트 - Django DRF와 머신러닝 라이브러리를 활용하여 프론트엔드와 백엔드가 분리된 프로젝트를 구성해보기

🖼️ Front-End 
------
[Front-End Link](https://github.com/ChaeYami/MyGallery_front)


🤔 기능
------
### 회원기능 : jwt token 사용

1. 회원가입 `POST`
    - id : 데이터 고유 id(PK)
    - account : 아이디, `UNIQUE`
    - email : 이메일, 회원가입/비밀번호 찾기 시에 인증 정보로 사용, `UNIQUE`
    - password : 비밀번호, 회원 가입이나 회원 수정 시에 해시
    - nickname : 닉네임
    - introduce : 소개, `default=None`, 프로필 편집 시에 수정 가능
    - point : 포인트, `default=500`, 글 작성(이미지 변환)시 사용, 댓글작성/출석 시 획득

2. 로그인  

3. 회원 정보 수정 `PATCH`
    - 프로필 사진, 닉네임, 자기소개 수정 가능

5. 회원 탈퇴 `DELETE`
    - 비밀번호를 입력받고 비활성화(`is_active = False`)

6. 계정 재활성화 `POST`
    - 이메일 인증 받고 다시 계정을 활성화 (`is_active = True`)

7. 팔로우 ,팔로워 `POST`
    - 팔로우 여부에 따라 팔로우/언팔로우 버튼
    - 자기 자신 팔로우 불가

8. 프로필 페이지 `GET`
    - 프로필사진, 닉네임, 아이디
    - 게시글 갯수
    - 팔로우 수 -> 목록, 팔로잉 수 -> 목록
    - 프로필 수정 `PUT`
    - 해당 사용자가 쓴 게시글 모아보기
    - 좋아요 누른 게시글 모아보기

9. 포인트
    - 회원가입시 500p 지급
    - 댓글 작성시에 50p 지급 
    - 출석보상으로 50p 지급 
    - 글 쓸 때 100p 차감
    - 글 작성 시 잔여 포인트로 포인트 부족 처리

### Article

1. 게시글 CREATE `POST`
    - **머신러닝** : 사용자가 이미지를 업로드하고 모델을 선택 -> 해당 모델에 맞는 그림으로 사진 변환 

2. 게시글 READ `GET`
    - 목록
        - 홈, 게시글 목록
        - 사진으로 목록화, 누르면 해당 게시글 상세페이지
        - 작성자 닉네임 클릭시 해당 유저 프로필로 이동
        - 홈 목록에서 좋아요 누르기 가능
    - 상세페이지
        - 해당 게시글의 상세 페이지
        - 댓글
        
4. 게시글 UPDATE `PUT`
    - 글 작성자만 가능 

5. 게시글 DELETE `DELETE`
    - 글 작성자만 가능 

6. 댓글 작성 `POST`
    - 로그인한 사용자만 가능 (access token)
    
7. 댓글 목록 `GET`
    
8. 댓글 삭제 `DELETE`
    - 댓글 작성자만 가능 

9. 좋아요 `POST`
    - 로그인한 사용자만 가능 (access token)
    
10. 좋아요 순위 보기 `GET`

***
💜 ERD
------
![image](https://github.com/ChaeYami/MyGallery/assets/120750451/51b45c4d-4503-4f00-a407-a1bb394f799d)

💚 API 명세
------
[API 명세](https://www.notion.so/S-A-dd7cf4020b524e6f878f25b994c9de2a?pvs=4#98e29231ef8a463aa4a489e504fc2687)

🧡 역할분담
------
[역할분담](https://www.notion.so/1f3d9558f6214ac39cc43cad4064763b?v=cf34176ae70c43318fb22f9d572da1c9&pvs=4)

💛 회의록
------
[회의록]([https://www.notion.so/b0a1e10efe444ceba18f2a632b4ac328?pvs=4](https://secretive-enthusiasm-4ee.notion.site/b0a1e10efe444ceba18f2a632b4ac328))
