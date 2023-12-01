import PIL.Image
from torchvision import transforms
import torch.nn as nn
import torch
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Paragraph, PageTemplate, BaseDocTemplate, Frame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus.flowables import Spacer
from reportlab.platypus import PageBreak
import json

#Custom vars
image_path = '.\\temp\image.jpg'
IMAGE_SIZE = 224
file = '..\\model\\CustomNet.pth'
categories = ['Atelectasis',
'Effusion',
'Infiltration',
'Mass',
'No Finding',
'Nodule',
'Pneumonia',
'Pneumothorax']


class CustomNet(nn.Module):
    def __init__(self, num_classes=8, is_trained=False):
        super().__init__()
        self.ConvLayer1 = nn.Sequential(
            nn.Conv2d(3, 8, 3),
            nn.Conv2d(8, 16, 3),
            nn.MaxPool2d(2),
            nn.ReLU()
        )
        self.ConvLayer2 = nn.Sequential(
            nn.Conv2d(16, 32, 5),
            nn.Conv2d(32, 32, 3),
            nn.MaxPool2d(4),
            nn.ReLU()
        )
        self.ConvLayer3 = nn.Sequential(
            nn.Conv2d(32, 64, 3),
            nn.Conv2d(64, 64, 5),
            nn.MaxPool2d(2),
            nn.ReLU()
        )
        self.ConvLayer4 = nn.Sequential(
            nn.Conv2d(64, 128, 5),
            nn.Conv2d(128, 128, 3),
            nn.MaxPool2d(2),
            nn.ReLU()
        )
        self.Lin1 = nn.Sequential(nn.Linear(512, 8), nn.Sigmoid())

    def forward(self, x):
        x = self.ConvLayer1(x)
        x = self.ConvLayer2(x)
        x = self.ConvLayer3(x)
        x = self.ConvLayer4(x)
        x = x.view(x.size(0), -1)
        x = self.Lin1(x)
        return x

# function to process the image
def preprocess_image(image_path=image_path):
    
    if os.path.isfile(image_path) is False:
        return None
    
    custom_state_dict = torch.load(file, map_location=torch.device('cpu'))
    adjusted_state_dict = {}

    for key, value in custom_state_dict['model'].items():
        adjusted_key = key.replace("model.", "")  # Ajusta según sea necesario
        adjusted_state_dict[adjusted_key] = value
    
    loaded_model = CustomNet()
    loaded_model.load_state_dict(adjusted_state_dict)
    class_dict = {i + 1: category for i, category in enumerate(categories)}
    
    input_image = preprocess_test_image(image_path)

    with torch.no_grad():
        output = loaded_model(input_image)
    
    predictions = torch.sigmoid(output[0]).numpy()
    
    #threshold = 0.5
    
    response = {}    
    
    for i, prob in enumerate(predictions):
        class_name = class_dict[i + 1] 
        response[class_name] = float(prob)*100
        
    #os.remove(image_path)
    
    return response
  
  
def preprocess_test_image(image_path):
    image = PIL.Image.open(image_path).convert('RGB')
    transform = transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    return transform(image).unsqueeze(0)

def create_pdf(uname = None, uage= None, ubirth= None,  uaddress= None, uheight= None, uweight= None, udisease= None):
    # Hardcoded patient information
    patient_info = {
        "Name": uname,
        "Age": uage,
        "Date of Birth": ubirth,
        # "Phone Number": "(111)222-5649",
        # "Email": "john.doe@outlook.com",
        "Address": uaddress,
        # "Emergency Contact Person": "Kim Joe",
        # "Emergency Contact Number": "(222)555-5698",
        "Height (cm)": uheight,
        "Weight (kg)": uweight,
    }

    # Calculate BMI
    height = float(patient_info["Height (cm)"])
    weight = float(patient_info["Weight (kg)"])
    bmi = round(weight / ((height / 100) ** 2), 2)
    patient_info["BMI"] = str(bmi)

    # Hardcoded report findings
    has_disease = True  # Change this to True/False as needed
    disease_name = udisease
    
    disease_details, preventive_measures =  find_disease_info(udisease)

    # Create a PDF document
    pdf_filename = ".\\temp\\medical_xray_report.pdf"
    doc = SimpleDocTemplate(pdf_filename, pagesize=letter)

    # Define a custom frame with margins for the content area
    frame = Frame(
        inch, inch, letter[0] - inch, letter[1] - inch,
        leftPadding=20, rightPadding=20, topPadding=30, bottomPadding=20
    )

    # Create a page template with header and footer
    def add_header_footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 9)
        
        # Header
        header_text = "Chest Expertise Medical Report"
        canvas.drawCentredString(letter[0] / 2, letter[1] - 18, header_text)

        # Footer
        page_num = canvas.getPageNumber()
        footer_text = f"Page {page_num}"
        canvas.drawString(inch, inch - 18, footer_text)

        canvas.restoreState()

    # Create a page template with header and footer
    page_template = PageTemplate(id="custom", frames=[frame], onPage=add_header_footer)

    doc.addPageTemplates([page_template])

    # Create a PDF document
    elements = []

    # Title
    title_style = ParagraphStyle(name='TitleStyle', fontSize=24, alignment=1, fontName='Helvetica-Bold', leading=28)
    subtitle_style = ParagraphStyle(name='SubtitleStyle', fontSize=14, fontName='Helvetica', alignment=1)
    elements.append(Paragraph("Chest Expertise X-Ray Medical Report", title_style))
    elements.append(Paragraph("Your expert for your thoracic health", subtitle_style))

    # Add space after the subtitle
    elements.append(Spacer(1, 0.2 * inch))

    # Patient Information Title (center-aligned)
    elements.append(Paragraph("Patient Information", ParagraphStyle(name='PatientInfoStyle', fontSize=14, fontName='Helvetica-Bold', leading=16, alignment=1)))

    # Patient Information Table
    table_data_style = ParagraphStyle(name='TableDataStyle', fontSize=10, fontName='Helvetica', leading=12)
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
    ])
    patient_data = []
    for key, value in patient_info.items():
        if key == "Name":
            value = f'<font color=black>{value}</font>'
        patient_data.append([Paragraph(key, table_data_style), Paragraph(value, table_data_style)])
    patient_table = Table(patient_data, colWidths=[2 * inch, 2.5 * inch])
    patient_table.setStyle(table_style)

    # Position the table on the left
    table_wrapper = Table([[patient_table]], colWidths=[4 * inch])
    elements.append(table_wrapper)

    # Add space after the patient information
    elements.append(Spacer(1, 0.2 * inch))

    # Add the table heading
    elements.append(Paragraph("Front Chest X-ray", title_style))

    # X-ray Image
    image = Image(".\\temp\\image.jpg", width=4 * inch, height=3 * inch)
    elements.append(image)
    elements.append(Spacer(1, 0.3 * inch))

    # Report Findings
    elements.append(Paragraph("Report Findings", title_style))
    if udisease.lower() != 'no finding':
        elements.append(Paragraph(f"<br/>{patient_info['Name']} is diagnosed with {disease_name}.", table_data_style))
        elements.append(Paragraph(f"<br/>Details: {disease_details}", table_data_style))
        elements.append(Paragraph(f"<br/>Preventive Measures: {preventive_measures}", table_data_style))
    else:
        elements.append(Paragraph(f"<br/>No disease was found for {patient_info['Name']}", table_data_style))

    # Build the PDF document
    doc.build(elements)
        
    return 'created'

def find_disease_info(disease_name):
    with open('.\\db\\diseases.json') as fp:
        diseases_data = json.load(fp)
    
    disease_info = diseases_data.get(disease_name.lower())
    
    if disease_info:
        return disease_info['disease_details'], disease_info['preventive_measures']
    else:
        return '', ''
