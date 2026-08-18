import os
import numpy as np
import tensorflow as tf

from tensorflow.keras.utils import image_dataset_from_directory # type: ignore
from tensorflow.keras.applications.efficientnet import preprocess_input # type: ignore

from sklearn.metrics import confusion_matrix, classification_report


# ============================================================
# SETTINGS
# ============================================================

IMG_SIZE = (224, 224)
BATCH_SIZE = 32

MODEL_PATH = "skin_model_efficientnet.h5"

DATASET_DIR = "static/Skin Type.v1i.multiclass"
TEST_DIR = os.path.join(DATASET_DIR, "test")


# ============================================================
# CHECK PATHS
# ============================================================

print("\n========================================")
print("CHECKING MODEL AND DATASET")
print("========================================")

print("Model :", MODEL_PATH)
print("Test  :", TEST_DIR)

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(
        f"Model not found: {MODEL_PATH}"
    )

if not os.path.exists(TEST_DIR):
    raise FileNotFoundError(
        f"Test folder not found: {TEST_DIR}"
    )

print("\nPaths found successfully!")


# ============================================================
# LOAD TEST DATA
# ============================================================

print("\n========================================")
print("LOADING TEST DATA")
print("========================================")

test_data = image_dataset_from_directory(
    TEST_DIR,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    label_mode="categorical",
    shuffle=False
)

class_names = test_data.class_names

print("\nClasses found:")

for i, name in enumerate(class_names):
    print(f"{i} -> {name}")

if len(class_names) != 4:
    raise ValueError(
        f"Expected 4 classes, found: {class_names}"
    )


# ============================================================
# PREPROCESS TEST DATA
# ============================================================

test_data = test_data.map(
    lambda x, y: (preprocess_input(x), y),
    num_parallel_calls=tf.data.AUTOTUNE
)

test_data = test_data.prefetch(tf.data.AUTOTUNE)


# ============================================================
# LOAD MODEL
# ============================================================

print("\n========================================")
print("LOADING TRAINED MODEL")
print("========================================")

model = tf.keras.models.load_model(MODEL_PATH)

print("Model loaded successfully!")


# ============================================================
# TEST ACCURACY
# ============================================================

print("\n========================================")
print("TESTING MODEL")
print("========================================")

test_loss, test_accuracy = model.evaluate(
    test_data,
    verbose=1
)

print("\n========================================")
print(f"Test Loss     : {test_loss:.4f}")
print(f"Test Accuracy : {test_accuracy * 100:.2f}%")
print("========================================")


# ============================================================
# PREDICTIONS
# ============================================================

print("\n========================================")
print("GENERATING PREDICTIONS")
print("========================================")

y_true = []
y_pred = []

for images, labels in test_data:

    predictions = model.predict(
        images,
        verbose=0
    )

    predicted_classes = np.argmax(
        predictions,
        axis=1
    )

    true_classes = np.argmax(
        labels.numpy(),
        axis=1
    )

    y_true.extend(true_classes)
    y_pred.extend(predicted_classes)


y_true = np.array(y_true)
y_pred = np.array(y_pred)


# ============================================================
# CONFUSION MATRIX
# ============================================================

print("\n========================================")
print("CONFUSION MATRIX")
print("========================================")

cm = confusion_matrix(
    y_true,
    y_pred
)

print("\nRows = Actual")
print("Columns = Predicted\n")

print("              ", end="")

for name in class_names:
    print(f"{name:>13}", end="")

print()

for i, name in enumerate(class_names):

    print(f"{name:<13}", end="")

    for j in range(len(class_names)):
        print(f"{cm[i][j]:>13}", end="")

    print()


# ============================================================
# CLASSIFICATION REPORT
# ============================================================

print("\n========================================")
print("CLASSIFICATION REPORT")
print("========================================")

report = classification_report(
    y_true,
    y_pred,
    target_names=class_names,
    digits=2
)

print(report)


# ============================================================
# PER-CLASS ACCURACY
# ============================================================

print("\n========================================")
print("PER-CLASS ACCURACY")
print("========================================")

for i, name in enumerate(class_names):

    total = np.sum(y_true == i)
    correct = np.sum(
        (y_true == i) & (y_pred == i)
    )

    if total > 0:
        accuracy = correct / total * 100
    else:
        accuracy = 0

    print(
        f"{name:<15}: "
        f"{accuracy:.2f}% "
        f"({correct}/{total})"
    )


# ============================================================
# COMPLETE
# ============================================================

print("\n========================================")
print("EVALUATION COMPLETE")
print("========================================")

print(f"Overall Accuracy : {test_accuracy * 100:.2f}%")
print(f"Model            : {MODEL_PATH}")

print("========================================")