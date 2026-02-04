from ultralytics import YOLO

def train_model():
    # Load a model
    model = YOLO("yolov8n.pt")  # load a pretrained model (recommended for training)

    # Train the model
    # data='data.yaml' should point to your dataset configuration file
    # epochs=100 is a standard starting point
    # imgsz=640 is standard image size
    results = model.train(data="data.yaml", epochs=100, imgsz=640, project="ktm_project", name="yolov8_ktm")
    
    # Evaluate performance
    metrics = model.val()
    
    # Export the model
    success = model.export(format="onnx")

if __name__ == '__main__':
    # Ensure you have a 'data.yaml' file pointing to your images before running!
    # Example data.yaml content:
    # path: ../datasets/ktm  # dataset root dir
    # train: images/train  # train images (relative to 'path') 
    # val: images/val  # val images (relative to 'path')
    # names:
    #   0: ktm_card
    
    print("Starting training... (Ensure data.yaml exists)")
    # train_model() # Uncomment to run when data is ready
