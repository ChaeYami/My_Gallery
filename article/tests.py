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



class CustomTokenObtainPairViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        cls.email = 'ark375@naver.com'
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
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
   


    
    #-------------------- 게시글 생성 --------------------
    # def test_create_article(self):
    #     response = self.client.post(
    #         path=reverse("articles:article_view"),
    #         data=self.article_data,
    #         HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
    #     )
    #     print(response.data)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(Article.objects.count(), 1)
    #     self.assertEqual(Article.objects.get().title,"test title")




    #-------------------- 임시 이미지 파일 게시글 생성  ---------------------------
    def test_create_article_image(self):
        temp_file = tempfile.NamedTemporaryFile()
        temp_file.name = "image.png"
        image_file = get_temporary_image(temp_file)
        image_file.seek(0)

        temp_file2 = tempfile.NamedTemporaryFile()
        temp_file2.name = "image2.png"
        image_file2 = get_temporary_image(temp_file2)
        image_file.seek(0)

        self.article_data["uploaded_image"]= image_file
        print(self.article_data)
        response = self.client.post(
            path=reverse("articles:article_view"),
            data=encode_multipart(data=self.article_data, boundary=BOUNDARY),
            content_type=MULTIPART_CONTENT,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)  
        self.assertEqual(Article.objects.count(), 2)  # 게시글이 추가되었는지 확인
        self.assertEqual(Article.objects.last().title, "test title")
        self.assertEqual(response.status_code,status.HTTP_200_OK)
    
    


    #-------------- 게시글 보기(아무것도 없을 경우) ------------------
    def test_get_article_list_empty(self):
        response = self.client.get(path=reverse("articles:article_view"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    


    
    #-------------- 게시글 보기(모두 보기 게시글 ) ------------------
    def test_article_list(self):
        self.article = []
        for _ in range(3):
            self.article.append(
                Article.objects.create(**self.article_data, user=self.user)
            )
        response = self.client.get(
            path=reverse("articles:article_view"),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)






#------------------------- 가짜 데이터 -------------------------
# class ArticleReadAPIViewTestCase(APITestCase):
#     @classmethod
#     def setUpTestData(cls):
#         cls.faker = Faker()
#         cls.articles = []
#         for i in range(10):
#             cls.user = User.objects.create_user(cls.faker.name(), cls.faker.word())
#             cls.articles.append(Article.objects.create(title=cls.faker.text(max_nb_chars=20), content=cls.faker.text(), user=cls.user))
#             # faker를 이용해서 랜덤으로 생성

#     def test_get_article(self):
#         for article in self.articles:
#             url = article.get_absolute_url()
#             response = self.client.get(url)
#             serializer = ArticleSerializer(article).data 
#             for key, value in serializer.items():
#                 self.assertEqual(response.data[key], value)




#------------------------------ ArticleDetail ---------------------------------



class ArticleDetailViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_data = {'account':'admin','email':'ark375@naver.com','password':'G1843514dadg23!4'}
        cls.article_data = [
            {"title": "test Title1", "content": "test content1"},
            {"title": "test Title2", "content": "test content2"},
            {"title": "test Title3", "content": "test content3"},
            {"title": "test Title4", "content": "test content4"},
            {"title": "test Title5", "content": "test content5"},
        ]
        cls.user = User.objects.create_user(
            'admin','ark375@naver.com','G1843514dadg23!4')
        cls.user_data = {'account':'admin','email':'ark375@naver.com','password':'G1843514dadg23!4'}
        cls.article = []
        for i in range(5):
            cls.article.append(
                Article.objects.create(**cls.article_data[i], user=cls.user)
            )

    def setUp(self):
        self.client.force_authenticate(user=self.user)
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
            "uploaded_image": SimpleUploadedFile('image.png', image_file.read(), content_type='image/png')
        }

        response = self.client.put(
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





