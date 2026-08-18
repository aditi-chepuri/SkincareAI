import os
import shutil

# ============================================================
# SETTINGS
# ============================================================

DATASET_DIR = "static/Skin Type.v1i.multiclass"

SPLITS = ["train", "valid", "test"]

CLASSES = ["combination", "dry", "normal", "oily"]


# ============================================================
# ORGANIZE DATASET
# ============================================================

print("\n========================================")
print("ORGANIZING SKIN TYPE DATASET")
print("========================================")

print("Dataset:", DATASET_DIR)


if not os.path.exists(DATASET_DIR):
    raise FileNotFoundError(
        f"Dataset folder not found: {DATASET_DIR}"
    )


for split in SPLITS:

    split_dir = os.path.join(DATASET_DIR, split)

    if not os.path.exists(split_dir):
        print(f"\nSkipping {split} - folder not found")
        continue

    print(f"\n========================================")
    print(f"PROCESSING: {split.upper()}")
    print("========================================")

    # Create class folders
    for class_name in CLASSES:

        class_dir = os.path.join(split_dir, class_name)

        os.makedirs(class_dir, exist_ok=True)

    # Read files
    files = os.listdir(split_dir)

    moved = {
        "combination": 0,
        "dry": 0,
        "normal": 0,
        "oily": 0
    }

    for file_name in files:

        # Ignore CSV and other files
        if not file_name.lower().endswith(
            (".jpg", ".jpeg", ".png")
        ):
            continue

        lower_name = file_name.lower()

        # Determine class from filename
        if lower_name.startswith("combination"):
            class_name = "combination"

        elif lower_name.startswith("dry"):
            class_name = "dry"

        elif lower_name.startswith("normal"):
            class_name = "normal"

        elif lower_name.startswith("oily"):
            class_name = "oily"

        else:
            print("UNKNOWN FILE:", file_name)
            continue

        source = os.path.join(split_dir, file_name)

        destination = os.path.join(
            split_dir,
            class_name,
            file_name
        )

        # Move image
        shutil.move(source, destination)

        moved[class_name] += 1

    # Print counts
    print("\nImages organized:")

    for class_name in CLASSES:
        print(
            f"{class_name:<15}: "
            f"{moved[class_name]}"
        )


print("\n========================================")
print("DATASET ORGANIZATION COMPLETE")
print("========================================")