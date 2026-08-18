import os
import numpy as np
import tensorflow as tf

from tensorflow.keras.applications import EfficientNetB0 # type: ignore
from tensorflow.keras.applications.efficientnet import preprocess_input # type: ignore

from tensorflow.keras.layers import ( # pyright: ignore[reportMissingModuleSource]
    Dense,
    Dropout,
    GlobalAveragePooling2D,
    BatchNormalization,
    RandomFlip,
    RandomRotation,
    RandomZoom,
    RandomContrast,
    RandomBrightness
)

from tensorflow.keras.models import Model, Sequential # type: ignore
from tensorflow.keras.utils import image_dataset_from_directory # type: ignore

from tensorflow.keras.callbacks import ( # type: ignore
    ModelCheckpoint,
    EarlyStopping,
    ReduceLROnPlateau
)

from sklearn.utils.class_weight import compute_class_weight


# ============================================================
# SETTINGS
# ============================================================

IMG_SIZE = (224, 224)
BATCH_SIZE = 32

PHASE1_EPOCHS = 25
PHASE2_EPOCHS = 25

DATASET_DIR = "static/Skin Type.v1i.multiclass"

TRAIN_DIR = os.path.join(DATASET_DIR, "train")
VALID_DIR = os.path.join(DATASET_DIR, "valid")
TEST_DIR = os.path.join(DATASET_DIR, "test")

MODEL_PATH = "skin_model_efficientnet.h5"
CLASS_NAMES_PATH = "class_names_efficientnet.txt"


# ============================================================
# CHECK DATASET
# ============================================================

print("\n==============================================")
print("        CHECKING DATASET")
print("==============================================")

print("Dataset :", DATASET_DIR)
print("Train   :", TRAIN_DIR)
print("Valid   :", VALID_DIR)
print("Test    :", TEST_DIR)

for path in [TRAIN_DIR, VALID_DIR, TEST_DIR]:

    if not os.path.exists(path):
        raise FileNotFoundError(
            f"\nDataset folder not found:\n{path}"
        )

print("\nDataset paths found successfully! ✅")


# ============================================================
# LOAD DATASETS
# ============================================================

print("\n==============================================")
print("        LOADING DATASETS")
print("==============================================")

train_data = image_dataset_from_directory(
    TRAIN_DIR,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    label_mode="categorical",
    shuffle=True,
    seed=42
)

valid_data = image_dataset_from_directory(
    VALID_DIR,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    label_mode="categorical",
    shuffle=False
)

test_data = image_dataset_from_directory(
    TEST_DIR,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    label_mode="categorical",
    shuffle=False
)


# ============================================================
# CLASS NAMES
# ============================================================

class_names = train_data.class_names

print("\n==============================================")
print("        CLASSES")
print("==============================================")

for i, name in enumerate(class_names):
    print(f"{i} -> {name}")


if len(class_names) != 4:

    raise ValueError(
        f"Expected 4 classes but found: {class_names}"
    )


# ============================================================
# CHECK CLASS COUNTS
# ============================================================

print("\n==============================================")
print("        TRAINING IMAGE COUNTS")
print("==============================================")

class_counts = {}

for class_name in class_names:

    class_dir = os.path.join(TRAIN_DIR, class_name)

    count = len([
        f for f in os.listdir(class_dir)
        if f.lower().endswith(
            (".jpg", ".jpeg", ".png", ".bmp", ".webp")
        )
    ])

    class_counts[class_name] = count

    print(f"{class_name:<15} : {count}")


# ============================================================
# CALCULATE CLASS WEIGHTS
# ============================================================

print("\n==============================================")
print("        CALCULATING CLASS WEIGHTS")
print("==============================================")

y_train = []

for class_index, class_name in enumerate(class_names):

    count = class_counts[class_name]

    y_train.extend([class_index] * count)

y_train = np.array(y_train)

class_weights_array = compute_class_weight(
    class_weight="balanced",
    classes=np.unique(y_train),
    y=y_train
)

class_weights = {
    int(i): float(weight)
    for i, weight in enumerate(class_weights_array)
}

for i, class_name in enumerate(class_names):

    print(
        f"{class_name:<15} : "
        f"{class_weights[i]:.4f}"
    )


# ============================================================
# DATA AUGMENTATION
# ============================================================

data_augmentation = Sequential([
    RandomFlip("horizontal"),
    RandomRotation(0.08),
    RandomZoom(0.10),
    RandomContrast(0.10),
    RandomBrightness(0.08)
])


# ============================================================
# PREPROCESSING
# ============================================================

print("\n==============================================")
print("        PREPARING DATA")
print("==============================================")


def preprocess_train(image, label):

    image = data_augmentation(
        image,
        training=True
    )

    image = preprocess_input(image)

    return image, label


def preprocess_valid(image, label):

    image = preprocess_input(image)

    return image, label


train_data = train_data.map(
    preprocess_train,
    num_parallel_calls=tf.data.AUTOTUNE
)

valid_data = valid_data.map(
    preprocess_valid,
    num_parallel_calls=tf.data.AUTOTUNE
)

test_data = test_data.map(
    preprocess_valid,
    num_parallel_calls=tf.data.AUTOTUNE
)


train_data = train_data.prefetch(
    tf.data.AUTOTUNE
)

valid_data = valid_data.prefetch(
    tf.data.AUTOTUNE
)

test_data = test_data.prefetch(
    tf.data.AUTOTUNE
)


# ============================================================
# BUILD EFFICIENTNETB0
# ============================================================

print("\n==============================================")
print("        BUILDING EFFICIENTNETB0")
print("==============================================")


base_model = EfficientNetB0(
    weights="imagenet",
    include_top=False,
    input_shape=(224, 224, 3)
)


# Freeze pretrained layers initially

base_model.trainable = False


x = base_model.output

x = GlobalAveragePooling2D()(x)

x = Dense(
    256,
    activation="relu"
)(x)

x = BatchNormalization()(x)

x = Dropout(0.4)(x)

output = Dense(
    len(class_names),
    activation="softmax"
)(x)


model = Model(
    inputs=base_model.input,
    outputs=output
)


# ============================================================
# COMPILE - PHASE 1
# ============================================================

print("\n==============================================")
print("        PHASE 1 COMPILATION")
print("==============================================")


model.compile(
    optimizer=tf.keras.optimizers.Adam(
        learning_rate=1e-4
    ),

    loss="categorical_crossentropy",

    metrics=["accuracy"]
)


# ============================================================
# CALLBACKS
# ============================================================

checkpoint = ModelCheckpoint(
    MODEL_PATH,

    monitor="val_accuracy",

    save_best_only=True,

    mode="max",

    verbose=1
)


early_stop = EarlyStopping(
    monitor="val_accuracy",

    patience=7,

    restore_best_weights=True,

    mode="max",

    verbose=1
)


reduce_lr = ReduceLROnPlateau(
    monitor="val_loss",

    factor=0.3,

    patience=3,

    min_lr=1e-7,

    verbose=1
)


# ============================================================
# PHASE 1
# ============================================================

print("\n==============================================")
print("        PHASE 1 - TRANSFER LEARNING")
print("==============================================")


history1 = model.fit(

    train_data,

    validation_data=valid_data,

    epochs=PHASE1_EPOCHS,

    class_weight=class_weights,

    callbacks=[
        checkpoint,
        early_stop,
        reduce_lr
    ]
)


# ============================================================
# PHASE 2 - FINE TUNING
# ============================================================

print("\n==============================================")
print("        PHASE 2 - FINE TUNING")
print("==============================================")


base_model.trainable = True


# Freeze most layers.
# Only the final 40 layers will be fine-tuned.

for layer in base_model.layers[:-40]:

    layer.trainable = False


# Keep BatchNormalization layers frozen.
# This is important for stable transfer learning.

for layer in base_model.layers:

    if isinstance(layer, BatchNormalization):

        layer.trainable = False


model.compile(

    optimizer=tf.keras.optimizers.Adam(
        learning_rate=1e-5
    ),

    loss="categorical_crossentropy",

    metrics=["accuracy"]
)


history2 = model.fit(

    train_data,

    validation_data=valid_data,

    epochs=PHASE2_EPOCHS,

    class_weight=class_weights,

    callbacks=[
        checkpoint,
        early_stop,
        reduce_lr
    ]
)


# ============================================================
# LOAD BEST MODEL
# ============================================================

print("\n==============================================")
print("        LOADING BEST MODEL")
print("==============================================")


model = tf.keras.models.load_model(
    MODEL_PATH
)


# ============================================================
# FINAL TEST
# ============================================================

print("\n==============================================")
print("        FINAL TEST")
print("==============================================")


test_loss, test_accuracy = model.evaluate(
    test_data,
    verbose=1
)


print("\n==============================================")
print("        FINAL RESULT")
print("==============================================")

print(
    f"Test Loss     : {test_loss:.4f}"
)

print(
    f"Test Accuracy : {test_accuracy * 100:.2f}%"
)


# ============================================================
# SAVE CLASS NAMES
# ============================================================

with open(
    CLASS_NAMES_PATH,
    "w"
) as f:

    for name in class_names:

        f.write(name + "\n")


# ============================================================
# COMPLETE
# ============================================================

print("\n==============================================")
print("        TRAINING COMPLETE ✅")
print("==============================================")

print(
    f"Model saved    : {MODEL_PATH}"
)

print(
    f"Classes saved  : {CLASS_NAMES_PATH}"
)

print(
    f"Classes        : {class_names}"
)

print(
    f"Final Accuracy : {test_accuracy * 100:.2f}%"
)

print("==============================================")