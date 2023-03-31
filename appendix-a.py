import argparse
import glob
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image as pilImage

# Set up command-line argument parsing
parser = argparse.ArgumentParser(description='Generate a PDF with UML diagrams.')
parser.add_argument('folder_path', help='The path to the folder containing the feature folders.')
args = parser.parse_args()

# Register the font
script_dir = os.path.dirname(os.path.abspath(__file__))
font_path = os.path.join(script_dir, 'fonts', 'Candara.ttf')
pdfmetrics.registerFont(TTFont('Candara', font_path))

# Set up styles and document
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='H1', fontSize=20, spaceAfter=12))
styles.add(ParagraphStyle(name='H2', fontSize=16, spaceAfter=8))
styles.add(ParagraphStyle(name='H3', fontSize=14, spaceBefore=6, spaceAfter=6))
styles.add(ParagraphStyle(name='Justify', fontName='Candara', fontSize=12, alignment=TA_JUSTIFY))
doc = SimpleDocTemplate("appendix.pdf", pagesize=A4)

# Add content
content = []

# Heading
heading = Paragraph("Appendix B: Analysis Models", styles['H1'])
content.append(heading)
content.append(Spacer(1, 12))

# Opening paragraph
opening_para = "In this appendix, we present the analysis models for the National Health Research Data Repository, offering a comprehensive representation of each system feature’s functionality, interactions, and components within the platform. These analysis models include class diagrams, component diagrams, state-transition diagrams, activity diagrams, sequence diagrams, and use case diagrams, which provide a comprehensive understanding of each feature's functionality and interactions within the system."
content.append(Paragraph(opening_para, styles['Justify']))
content.append(Spacer(1, 12))

# Iterate through feature folders
feature_folders = [f for f in os.listdir(args.folder_path) if os.path.isdir(os.path.join(args.folder_path, f))]
for feature_folder in sorted(feature_folders, key=lambda x: int(x.split()[2].split(':')[0])):
    feature_title = feature_folder.replace('_', ' ')
    content.append(Paragraph(feature_title, styles['H2']))
    
    diagrams = glob.glob(os.path.join(args.folder_path, feature_folder, "*.png"))
    
    for i, diagram_path in enumerate(sorted(diagrams), 1):
        # Add diagram title
        diagram_title = f"{i}. {os.path.splitext(os.path.basename(diagram_path))[0]}"
        title_paragraph = Paragraph(diagram_title, styles['H3'])

        # Add diagram image
        img = pilImage.open(diagram_path)
        img_width, img_height = img.size
        aspect_ratio = float(img_height) / float(img_width)

        # Calculate the width and height of the image while preserving the aspect ratio
        max_img_width = A4[0] - 40 * mm
        max_img_height = A4[1] - 100 * mm

        if img_height > max_img_height:
            img_height = max_img_height
            img_width = img_height / aspect_ratio

        if img_width > max_img_width:           
            img_width = max_img_width
            img_height = img_width * aspect_ratio

        # Create an Image object with the new dimensions
        img = Image(diagram_path, width=img_width, height=img_height)

        # Add a spacer between the feature heading and the first diagram
        if i == 1:
            content.append(Spacer(1, 12))

        # Check if the diagram's heading and the diagram fit on the same page, otherwise, print them on the next page
        keep_together = KeepTogether([title_paragraph, img])
        content.append(keep_together)

        # Add a spacer after each diagram
        content.append(Spacer(1, 12))

# Build the PDF document
doc.build(content)
