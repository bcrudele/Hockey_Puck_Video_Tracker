from transformers import DetrImageProcessor, DetrForObjectDetection
import torch
from PIL import Image, ImageDraw

# def draw_boxes_on_image(boxes, image, output_path="output_image_with_boxes.jpg"):

#     draw = ImageDraw.Draw(image)

# 	# for each box, draw a rect:
#     for box in boxes:	
#         draw.rectangle(box, outline="red", width=3)

#     image.save(output_path)
#     print(f"Image with boxes saved as {output_path}")

# image path
image_path = "ishl.png"
image = Image.open(image_path)
image = image.convert('RGB')

# you can specify the revision tag if you don't want the timm dependency
processor = DetrImageProcessor.from_pretrained("facebook/detr-resnet-50", revision="no_timm")
model = DetrForObjectDetection.from_pretrained("facebook/detr-resnet-50", revision="no_timm")

inputs = processor(images=image, return_tensors="pt")
outputs = model(**inputs)

# convert outputs (bounding boxes and class logits) to COCO API
# let's only keep detections with score > 0.9
target_sizes = torch.tensor([image.size[::-1]])
results = processor.post_process_object_detection(outputs, target_sizes=target_sizes, threshold=0.9)[0]

for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
    box = [round(i, 2) for i in box.tolist()]
    print(
            f"Detected {model.config.id2label[label.item()]} with confidence "
            f"{round(score.item(), 3)} at location {box}"
    )

# # create list of boxes
# boxes = [box.tolist() for box in results["boxes"]]

# # draw boxes:
# draw_boxes_on_image(boxes, image=image, output_path="output_image_with_boxes.jpg")