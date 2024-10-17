import requests
import tensorflow as tf
from starlette.datastructures import FormData, UploadFile
from starlette.requests import Request

from src.core.endpoint import HTTPEndpoint
from src.core.exception import BaseException, Forbidden, InternalServer
from src.core.security.authentication import JsonWebToken
from src.enum import ErrorCode, Role
from src.helper.s3_helper import S3Service
from src.schema.predict_schema import PredictSchema

new_model2_load = tf.keras.models.load_model(
    "src/ai/my_model_vgg16_1.h5", custom_objects=None, compile=True, safe_mode=True
)
# Class names
class_names = [
    "Acne and Rosacea Photos",
    "Actinic Keratosis Basal Cell Carcinoma and other Malignant Lesions",
    "Atopic Dermatitis Photos",
    "Bullous Disease Photos",
    "Cellulitis Impetigo and other Bacterial Infections",
    "Eczema Photos",
    "Exanthems and Drug Eruptions",
    "Hair Loss Photos Alopecia and other Hair Diseases",
    "Herpes HPV and other STDs Photos",
    "Light Diseases and Disorders of Pigmentation",
    "Lupus and other Connective Tissue diseases",
    "Melanoma Skin Cancer Nevi and Moles",
    "Nail Fungus and other Nail Disease",
    "Poison Ivy Photos and other Contact Dermatitis",
    "Psoriasis pictures Lichen Planus and related diseases",
    "Scabies Lyme Disease and other Infestations and Bites",
    "Seborrheic Keratoses and other Benign Tumors",
    "Systemic Disease",
    "Tinea Ringworm Candidiasis and other Fungal Infections",
    "Urticaria Hives",
    "Vascular Tumors",
    "Vasculitis Photos",
    "Warts Molluscum and other Viral Infections",
]


# Create a function to download an image and resize it for the model
def load_and_prep_image_from_url(url, img_shape=224):
    """
    Downloads an image from a URL, turns it into a tensor
    and reshapes it to (img_shape, img_shape, colour_channel).
    """
    # Download the image from the URL
    response = requests.get(url)
    img = tf.image.decode_image(response.content, channels=3)

    # Resize the image (to the same size our model was trained on)
    img = tf.image.resize(img, size=[img_shape, img_shape])

    # Rescale the image (get all values between 0 and 1)
    img = img / 255.0
    return img


def pred_and_plot(url):
    img = load_and_prep_image_from_url(url)
    model = new_model2_load
    pred = model.predict(tf.expand_dims(img, axis=0))
    predicted_class = class_names[tf.argmax(pred[0]).numpy()]
    print(f"Predicted class: {predicted_class}")
    probabilities = [
        (class_names[i], pred[0][i] * 100) for i in range(len(class_names))
    ]
    sorted_probabilities = sorted(probabilities, key=lambda x: x[1], reverse=True)
    return {
        "predict_final": predicted_class,
        "sorted_probabilities": sorted_probabilities,
    }


class ApiPredictData(HTTPEndpoint):
    async def post(self, form_data: PredictSchema, request: Request, auth: JsonWebToken):
        '''
        this api will predict...
        '''
        try:
            if auth.get("role") not in [Role.ADMIN.value,Role.DOCTOR.value]:
                raise Forbidden(
                    error_code=ErrorCode.FORBIDDEN.name,
                    errors={
                        "message":ErrorCode.msg_permission_denied.value
                    }
                )
            image_url = form_data.image if isinstance(form_data.image, str) else None
            if not image_url:
                form_request: FormData = await request.form()
                image_file = form_request.get("image")
                if isinstance(image_file,UploadFile):
                    if image_file.content_type not in ["image/jpeg", "image/png","image/jpg","image/JPG","image/PNG"]:
                        raise InternalServer(
                            error_code=ErrorCode.SERVER_ERROR.name,
                            errors={
                                "message": "chỉ chấp nhận file ảnh định dạng jpg, jpeg hoặc png"
                            },
                        )
                    s3_service =S3Service()
                    image_url = await s3_service.upload_file_from_form(image_file)
                    if image_url is None:
                        raise InternalServer(
                            error_code=ErrorCode.SERVER_ERROR.name,
                            errors={
                                "message": ErrorCode.msg_server_error.value
                            }
                        )
                    if not image_url.startswith("http"):
                        raise InternalServer(
                            error_code=ErrorCode.SERVER_ERROR.name,
                            errors={"message": "chỉ chấp nhân link ảnh hoặc file ảnh"},
                        )
            data = pred_and_plot(image_url)
            return data

        except Exception as e:
            if isinstance(e,BaseException):
                raise e
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={
                    "message": ErrorCode.msg_server_error.value
                }
            )
