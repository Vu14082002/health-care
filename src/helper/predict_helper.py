import requests
import tensorflow as tf
from tensorflow.keras.models import load_model


class PredictHelper:
    def __init__(self) -> None:
        self.model_vgg16 = load_model("ai/my_model_vgg16_1.h5")
        self.class_names = [
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

    def _load_and_prep_image_from_url(url, img_shape=224):
        """
        Downloads an image from a URL, turns it into a tensor
        and reshapes it to (img_shape, img_shape, colour_channel).
        """
        response = requests.get(url)
        img = tf.image.decode_image(response.content, channels=3)

        # Resize the image (to the same size our model was trained on)
        img = tf.image.resize(img, size=[img_shape, img_shape])

        img = img / 255.0 #type: ignore
        return img

    def pred_and_plot(self, url: str, model: str | None = None):
        """
        Imports an image located at url, makes a prediction on it with
        a trained model and prints the predicted class and probabilities.
        """
        img = self._load_and_prep_image_from_url(url)

        pred = self.model_vgg16.predict(tf.expand_dims(img, axis=0))

        predicted_class = self.class_names[tf.argmax(pred[0]).numpy()]


        print(f"Predicted class: {predicted_class}")

        # Create a list of (class_name, probability) tuples
        probabilities = [
            (class_names[i], pred[0][i] * 100) for i in range(len(class_names))
        ]

        # Sort probabilities from high to low
        sorted_probabilities = sorted(probabilities, key=lambda x: x[1], reverse=True)

        # Print the probabilities for each class in sorted order
        for class_name, probability in sorted_probabilities:
            print(f"{class_name}: {probability:.2f}%")
