from django.shortcuts import render
from django.core.files.storage import default_storage
from django.http import JsonResponse
from rest_framework.decorators import api_view
import cv2
from django.views.decorators.csrf import csrf_exempt
import os


def index(request):
    return render(request, 'analyzer/index.html')


#@csrf_exempt
@api_view(['POST'])
def upload_image(request):
    try:
        # Save uploaded image to a temporary location
        uploaded_file = request.FILES['image']
        file_path = default_storage.save(f'tmp/{uploaded_file.name}', uploaded_file)
        image_full_path = os.path.join(default_storage.location, file_path)

        # Extract colors from the image
        colors = extract_strip_colors(image_full_path)

        # Prepare response data
        response_data = {
            'image_url': default_storage.url(file_path),
            'colors': colors
        }

        return JsonResponse(response_data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


import cv2


def extract_strip_colors(image_path):
    # Load the image
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError("Image not found or unable to load.")

    # Resize image to a standard width for better processing
    standard_width = 600
    scale_percent = standard_width / image.shape[1]
    width = int(image.shape[1] * scale_percent)
    height = int(image.shape[0] * scale_percent)
    dim = (width, height)
    image = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)

    # Convert the image to the RGB color space (OpenCV loads images in BGR format)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Assuming the image contains 10 strips, we will divide it into 10 equal parts
    strip_height = image_rgb.shape[0] // 10
    colors = []
    for i in range(10):
        strip = image_rgb[i * strip_height:(i + 1) * strip_height, :, :]
        average_color = cv2.mean(strip)[:3]  # Get the average color of the strip
        colors.append({'color': tuple(map(int, average_color))})  # Convert to int and append

    return colors