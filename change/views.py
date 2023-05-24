from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response

from django.http import FileResponse
from rest_framework import parsers

from django.core.files import File
from .models import ImageTransform

import cv2
import numpy as np
import os

class TransformView(APIView):
    parser_classes = [parsers.MultiPartParser]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, change_id, format=None):
        file_obj = request.FILES['image']
        # change_id = request.POST['change_id']

        # .t7 파일 로드
        model_dict = {
            '1': 'change/models/candy.t7',
            '2': 'change/models/composition_vii.t7',
            '3': 'change/models/feathers.t7',
            '4': 'change/models/la_muse.t7',
            '5': 'change/models/mosaic.t7',
            '6': 'change/models/starry_night.t7',
            '7': 'change/models/the_scream.t7',
            '8': 'change/models/the_wave.t7',
            '9': 'change/models/udnie.t7',
        }
        model_path = model_dict.get(str(change_id))
        if model_path is None:
            return Response({'error': 'Invalid change_id'}, status=400)
        net = cv2.dnn.readNetFromTorch(model_path)

        # 이미지 전처리
        nparr = np.fromstring(file_obj.read(), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        h, w, c = img.shape
        img = cv2.resize(img, dsize=(500, int(h / w * 500)))
        MEAN_VALUE = [103.939, 116.779, 123.680]
        blob = cv2.dnn.blobFromImage(img, mean=MEAN_VALUE)

        # 추론하기
        net.setInput(blob)
        output = net.forward()

        # 후처리
        output = output.squeeze().transpose((1, 2, 0))
        output += MEAN_VALUE
        output = np.clip(output, 0, 255)  # 가끔 255를 초과하는 경우가 있어서 최대 255 제한
        output = output.astype('uint8')

        # 변환된 이미지를 임시 파일에 저장
        cv2.imwrite('temp.png', output)

        # 임시 파일을 Django model에 저장
        with open('temp.png', 'rb') as f:
            img_transformed = ImageTransform(image=File(f))
            img_transformed.save()
        
        # 임시 파일 삭제
        os.remove('temp.png')

        # 변환된 이미지의 URL을 응답으로 보내기
        return Response({'image_url': img_transformed.image.url},status=status.HTTP_200_OK)
