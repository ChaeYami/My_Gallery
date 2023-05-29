from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from django.test import TestCase
from rest_framework import status
from .models import Article,Comment
from user.models import User
from django.test.client import MULTIPART_CONTENT, encode_multipart, BOUNDARY
from PIL import Image
import tempfile
from django.core.files.uploadedfile import SimpleUploadedFile
from faker import Faker
from .serializers import ArticleSerializer


# ----------------------------- 임시 이미지 파일 -----------------------------


def get_temporary_image(temp_file):
    size = (200, 200)
    color = (255, 0, 0, 0)
    image = Image.new("RGBA", size, color)
    image.save(temp_file, "png")
    return temp_file


#--------------------------- 유저 생성 -------------------------------------


class CustomTokenObtainPairViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        cls.email = 'dsadasd123@naver.com'
        cls.account = 'admin'
        cls.nickname = 'admin'
        cls.password = 'G1843514dadg23!4'
        cls.user_data = {'account':'admin','email':'ark375@naver.com','password':'G1843514dadg23!4'}
        cls.user = User.objects.create_user(account=cls.account, email=cls.email, nickname=cls.nickname, password=cls.password)
        cls.article_data = {"title": "test title", "content": "test content"}
        cls.article = Article.objects.create(**cls.article_data, user=cls.user)
        cls.user.is_active = True  # 인증 상태를 True로 설정
        cls.user.save()
    
    def setUp(self):
        self.access_token = self.client.post(reverse('user:login_view'), self.user_data).data['access']


    #---------------------- 로그인 테스트 코드 ----------------------
    
    
    def test_login(self):
        url = reverse("user:login_view")
        data = {
            'account': self.account,
            'password': self.password
        }
        
        response = self.client.post(url, data)
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # 로그인 요청이 성공적으로 처리되었는지 확인




    # ------------------- 로그인 안 되어 있을 때 -------------------
    
    
    def test_fail_if_not_logged_in(self):
        url = reverse("articles:article_view")
        response = self.client.post(url, self.article_data)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
   

    #-------------------- 게시글 생성  ---------------------------
    
    
    def test_create_article_image(self):
        temp_file = tempfile.NamedTemporaryFile()
        temp_file.name = "image.png"
        image_file = get_temporary_image(temp_file)
        image_file.seek(0)

        temp_file2 = tempfile.NamedTemporaryFile()
        temp_file2.name = "image2.png"
        image_file2 = get_temporary_image(temp_file2)
        image_file2.seek(0)

        self.article_data["uploaded_image"] = image_file
        self.article_data["changed_image"] = image_file2

        response = self.client.post(
            path=reverse("articles:article_view"),
            data=encode_multipart(data=self.article_data, boundary=BOUNDARY),
            content_type=MULTIPART_CONTENT,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Article.objects.count(), 2)
        self.assertEqual(Article.objects.last().title, "test title")

    




    #-------------- 게시글 보기(아무것도 없을 경우) ------------------
    
    
    def test_get_article_list_empty(self):
        response = self.client.get(path=reverse("articles:article_list", kwargs={"user_id": self.user.id}))
        print(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)





    #-------------- 게시글 보기(모두 보기 게시글) ------------------
    
    
    def test_article_list(self):
        self.article = []
        for _ in range(3):
            self.article.append(
                Article.objects.create(**self.article_data, user=self.user)
            )
        response = self.client.get(
            path=reverse("articles:article_list", kwargs={"user_id": self.user.id}),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)



#------------------------------ ArticleDetail ---------------------------------



class ArticleDetailViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_data = {'account':'admin','email':'dsadasd123@naver.com','password':'G1843514dadg23!4'}
        cls.article_data = [
            {"title": "test Title1", "content": "test content1"},
            {"title": "test Title2", "content": "test content2"},
            {"title": "test Title3", "content": "test content3"},
            {"title": "test Title4", "content": "test content4"},
            {"title": "test Title5", "content": "test content5"},
        ]
        cls.user = User.objects.create_user(
            'admin','dsadasd123@naver.com','G1843514dadg23!4')
        cls.user_data = {'account':'admin','email':'dsadasd123@naver.com','password':'G1843514dadg23!4'}
        cls.article = []
        for i in range(5):
            cls.article.append(
                Article.objects.create(**cls.article_data[i], user=cls.user)
            )

    def setUp(self):
        self.client.force_authenticate(user=self.user) # 토큰없이 로그인
    #     self.access_token = self.client.post(reverse('user:login_view'), self.user_data).data['access']

    
        

    
    
    #--------------------------- 게시글 상세보기 ---------------------------
    
    
    def test_article_detail(self):
        response = self.client.get(
            path=reverse("articles:article_detail_view", kwargs={"article_id": 5}),
            # HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["content"], "test content5")

    
    
    #-------------------------- 게시글 수정하기 --------------------------
   
   
   
    def test_article_detail_update(self):
        temp_file = tempfile.NamedTemporaryFile()
        temp_file.name = "image.png"
        image_file = get_temporary_image(temp_file)
        image_file.seek(0)

        self.article_data = {
            "title": "updated test Title",
            "content": "updated test content",
        }
        # 이미지 파일 추가
        image_data = image_file.read()
        uploaded_image = SimpleUploadedFile("image.png", image_data, content_type="image/png")
        changed_image = SimpleUploadedFile("image.png", image_data, content_type="image/png")
        self.article_data["uploaded_image"] = uploaded_image
        self.article_data["changed_image"] = changed_image
       
        response = self.client.patch(
            path=reverse("articles:article_detail_view", kwargs={"article_id": 5}),
            data=self.article_data,
            # HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )

        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Article.objects.count(), 5)
        self.assertEqual(response.data["content"], "updated test content")


    #------------------ 게시글 삭제하기 ------------------
    
    
    def test_article_detail_delete(self):
        response = self.client.delete(
            path=reverse("articles:article_detail_view", kwargs={"article_id": 5}),
            # HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Article.objects.count(), 4)
        self.assertEqual(response.data,{'message': '삭제완료!'})



# -------------------------  Comment 생성 조회 -------------------------

class CommentViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.email = 'dsadasd123@naver.com'
        cls.nickname = 'admin'
        cls.account = 'admin'
        cls.password = 'G1843514dadg23!4'
        cls.user_data = {'account':'admin','email':'dsadasd123@naver.com','password':'G1843514dadg23!4'}
        cls.article_data = {"title": "test Title", "content": "test content"}
        cls.comment_data = {"comment": "test comment"}
        cls.user = User.objects.create_user(account=cls.account, email=cls.email, nickname=cls.nickname, password=cls.password)
        cls.article = Article.objects.create(**cls.article_data, user=cls.user)

    def setUp(self):
        # self.access_token = self.client.post(reverse("user:login_view"), self.user_data).data["access"]
        self.client.force_authenticate(user=self.user)




    #------------------------ Comment 작성 ------------------------
    
    
    def test_create_article_success(self):
        response = self.client.post(
            path=reverse("articles:comment_view", kwargs={"article_id": self.article.id}),
            data=self.comment_data,
            # HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        print(response)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(Comment.objects.get().comment, self.comment_data["comment"])


    
    #------------------------- Comment리스트 -----------------------
    
    def test_comment_list(self):
        self.comments = []
        for _ in range(5):
            self.comments.append(
                Comment.objects.create(
                    comment="comment", article=self.article, user=self.user
                )
            )
        response = self.client.get(
            path=reverse("articles:comment_view", kwargs={"article_id": self.article.id}),
            # HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Comment.objects.count(), 5)
        self.assertEqual(len(response.data), 5)
        self.assertEqual(response.data[0]["comment"], "comment")




#--------------------- Comment, 삭제 ---------------------


class CommentDetailViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.email = 'dsadasd123@naver.com'
        cls.nickname = 'admin'
        cls.account = 'admin'
        cls.password = 'G1843514dadg23!4'
        cls.user_data = {'account':'admin','email':'dsadasd123@naver.com','password':'G1843514dadg23!4'}
        cls.article_data = {"title": "test Title", "content": "test content"}
        cls.comment_data = {"comment": "test comment"}
        cls.user = User.objects.create_user(account=cls.account, email=cls.email, nickname=cls.nickname, password=cls.password)
        cls.article = Article.objects.create(**cls.article_data, user=cls.user)
        cls.comment_data = [
            {"content": "test 1"},
            {"content": "test 2"},
            {"content": "test 3"},
            {"content": "test 4"},
            {"content": "test 5"},
        ]
       
        cls.comment = []
        for _ in range(5):
            cls.comment.append(
                Comment.objects.create(
                    comment="comment", article=cls.article, user=cls.user
                )
            )

    def setUp(self):
        # self.access_token = self.client.post(reverse("token_obtain_pair"), self.user_data).data["access"]
        self.client.force_authenticate(user=self.user)

    
   
    #------------------------- 코멘트 삭제 -------------------------
    
    
    def test_comment_delete(self):
        comment_id = self.comment[0].id  # 삭제할 댓글의 ID
        response = self.client.delete(
            path=reverse("articles:comment_delete", kwargs={"comment_id": comment_id}),
            # HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comment.objects.count(), 4)
        self.assertEqual(response.data, {'message': '삭제완료!'})



# -------------------------------- 좋아요 test --------------------------------

class HerartViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.email = 'dsadasd123@naver.com'
        cls.nickname = 'admin'
        cls.account = 'admin'
        cls.password = 'G1843514dadg23!4'
        cls.user_data = {'account':'admin','email':'dsadasd123@naver.com','password':'G1843514dadg23!4'}
        cls.article_data = {"title": "test Title", "content": "test content"}
        cls.user = User.objects.create_user(account=cls.account, email=cls.email, nickname=cls.nickname, password=cls.password)
        cls.article = Article.objects.create(**cls.article_data, user=cls.user)
        cls.article_2 = Article.objects.create(**cls.article_data, user=cls.user)
        cls.user.hearts.add(cls.article_2)
        

    def setUp(self):
        # self.access_token = self.client.post(reverse("user:login_view"), self.user_data).data["access"]
        self.client.force_authenticate(user=self.user)
    
    
    
    # ----------------------------- 좋아요 누르기 -----------------------------
    def test_hearts_article(self):
        url = reverse("articles:Hearts_view", kwargs={"article_id": self.article.id})

        response = self.client.post(url)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'message': '좋아요를 눌렀습니다.'})

    
    
    #----------------------------- 좋아요 취소하기 -----------------------------
    def test_hearts_article_cancle(self):
        url = reverse("articles:Hearts_view", kwargs={"article_id": self.article_2.id})

        response = self.client.post(url)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'message': '좋아요를 취소했습니다.'})

    
    
    #------------------------------ 좋아요 count ------------------------------

    def test_get_hearts_count(self):
        url = reverse("articles:Hearts_view", kwargs={"article_id": self.article_2.id})

        response = self.client.get(url)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    
    
    #------------------------------ 게시글 좋아요 보기, 순위 ------------------------------

    def test_get_hearts_article(self):
        user_id = self.user.id
        url = reverse("articles:User_Hearts_View", kwargs={"user_id": self.user.id})

        # 좋아요한 게시글 조회 테스트
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        articles = response.data
        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0]['id'], self.article_2.id)
        self.assertEqual(articles[0]['title'], self.article_2.title)
        self.assertEqual(articles[0]['content'], self.article_2.content)



 # ======================================= 테스트 코드 끝 =======================================