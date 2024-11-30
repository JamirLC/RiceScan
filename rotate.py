import cv2
import os

# Define the parent folder containing the original dataset
parent_folder = "D:/VSCODE/RiceScan/augmentation"

# Define the output folder for the rotated images
output_folder = "D:/VSCODE/RiceScan/dataset"
os.makedirs(output_folder, exist_ok=True)

# Loop through each folder in the parent folder
for folder_name in os.listdir(parent_folder):
    folder_path = os.path.join(parent_folder, folder_name)

    # Ensure the folder_path is a directory
    if not os.path.isdir(folder_path):
        continue

    # Create a corresponding subfolder in the output folder
    output_subfolder = os.path.join(output_folder, folder_name)
    os.makedirs(output_subfolder, exist_ok=True)
    print(f"Processing folder: {folder_name}")

    # Process each image in the folder
    for image_name in os.listdir(folder_path):
        image_path = os.path.join(folder_path, image_name)

        # Skip if it's not a valid image file
        if not (image_name.lower().endswith((".jpg", ".jpeg", ".png"))):
            continue

        # Load the image
        original_image = cv2.imread(image_path)
        if original_image is None:
            print(f"Error: Unable to read {image_path}")
            continue

        # Save the original image to the output folder
        original_path = os.path.join(output_subfolder, f"original_{image_name}")
        cv2.imwrite(original_path, original_image)

        # Generate rotated images and save them
        try:
            # Rotate 90 degrees
            rotated_90 = cv2.rotate(original_image, cv2.ROTATE_90_CLOCKWISE)
            rotated_90_path = os.path.join(output_subfolder, f"rotated_90_{image_name}")
            cv2.imwrite(rotated_90_path, rotated_90)

            # Rotate 180 degrees
            rotated_180 = cv2.rotate(original_image, cv2.ROTATE_180)
            rotated_180_path = os.path.join(output_subfolder, f"rotated_180_{image_name}")
            cv2.imwrite(rotated_180_path, rotated_180)

            # Rotate 270 degrees
            rotated_270 = cv2.rotate(original_image, cv2.ROTATE_90_COUNTERCLOCKWISE)
            rotated_270_path = os.path.join(output_subfolder, f"rotated_270_{image_name}")
            cv2.imwrite(rotated_270_path, rotated_270)

            print(f"Processed and saved all rotations for: {image_name}")

        except Exception as e:
            print(f"Error processing {image_name}: {e}")

    print(f"Finished processing folder: {folder_name}")

print("All folders processed successfully.")
