# MyGallery

📚 stacks 
------
<img src="https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=python&logoColor=white">  <img src="https://img.shields.io/badge/django-092E20?style=for-the-badge&logo=django&logoColor=white"> <img src="https://img.shields.io/badge/html5-E34F26?style=for-the-badge&logo=html5&logoColor=white">  <img src="https://img.shields.io/badge/javascript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black"> 

***

💖 머신러닝 프로젝트 : 나만의 갤러리 SNS 만들기 🖼️
------
> 2023.05.22 ~ 
  
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
2. 로그인
3. 회원 정보 수정 `PATCH`
4. 회원 탈퇴 `DELETE`
5. 팔로우 ,팔로워
    - 팔로우 여부에 따라 팔로우/언팔로우 버튼
    - 자기 자신 팔로우 불가
6. 프로필 페이지
    - 팔로우 목록, 팔로잉 목록

### Article

1. 게시글 CREATE - 

2. 게시글 READ `GET`
    - 목록
        - 홈, 게시글 목록
    - 상세페이지
        - 해당 게시글의 상세 페이지
        
4. 게시글 UPDATE `PUT`
   

5. 게시글 DELETE `DELETE`

6. 댓글 작성
7. 댓글 목록
8. 댓글 삭제 

8. 좋아요
