import os
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader

import secret
from gemini import generate_gemini_response
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph
from pypdf import PdfMerger
from emails import send_email
import re


# QM code: 35609e13ba03bc216f3106b680b368840c71746b074df7e32a9706f13d0e110a


def create_loan_pdf(guitar_model, email, name, clas, serial_num):
    canvas = Canvas("loan-sheet.pdf", pagesize=LETTER)
    canvas.setFont("Times-Roman", 18)

    image_path = "image.jpg"
    image_reader = ImageReader(image_path)
    image_width = image_reader.getSize()[0]
    image_height = image_reader.getSize()[1]

    # Line width and height (adjust these to your actual line dimensions)
    line_width = 7 * inch
    line_height = 1 * inch

    # Calculate scaling factors (maintain aspect ratio)
    horizontal_scaling_factor = line_width / image_width

    vertical_scaling_factor = line_height / image_height
    scaling_factor = min(horizontal_scaling_factor, vertical_scaling_factor)

    # Draw the scaled image
    canvas.drawInlineImage(
        image_path,
        1 * inch,  # X position
        9.4 * inch,  # Y position
        width=image_width * scaling_factor,
        height=image_height * scaling_factor,
    )

    canvas.setFont("Times-Roman", 13)

    cleaning_instructions = generate_gemini_response(
        f"Guitar model: {guitar_model}, cleaning instructions").result
    storage_instructions = generate_gemini_response(
        f"Guitar model: {guitar_model}, storage instructions").result

    paragraph_style = ParagraphStyle(
        name='Normal',
        fontName='Times-Roman',
        fontSize=13,
        leading=15,
        leftIndent=0,
        firstLineIndent=0,  # Ensure no first-line indentation
        spaceAfter=0,
        spaceBefore=0)

    underline_paragraph_style = ParagraphStyle(
        name='Underline',
        parent=paragraph_style,
        textDecoration='underline'
    )

    styles = getSampleStyleSheet()

    # Define the initial Y position
    y_position = 8.75 * inch

    canvas.drawString(2 * inch, 10 * inch, "St. Patrick's School")
    canvas.drawString(2 * inch, 9.6 * inch, "Loan Form")

    # ========LOAN ACKNOWLEDGEMENT=========
    intro_text = f"I, <u>{name.title()}</u>, of Class <u>{clas}</u>, have been granted the use of the following musical instrument:"
    intro_paragraph = Paragraph(intro_text, paragraph_style)
    width, height = intro_paragraph.wrap(line_width, line_height)
    intro_paragraph.drawOn(canvas, 1 * inch, y_position - height)
    y_position -= (height + 0.2 * inch
                   )  # Adjust the Y position for the next paragraph

    # ========LOANED MODELS=========
    bullet_text = f"• Instrument: <u>{guitar_model}</u>, Serial Number: <u>{serial_num}</u>"
    bullet_paragraph = Paragraph(bullet_text, underline_paragraph_style)
    width, height = bullet_paragraph.wrap(line_width, line_height)
    bullet_paragraph.drawOn(canvas, 1 * inch, y_position - height)
    y_position -= (height + 0.2 * inch
                   )  # Adjust the Y position for the next paragraph

    # ========CLEANING INSTRUCTIONS=========
    cleaning_paragraph = Paragraph(
        f"Cleaning Instructions: {cleaning_instructions}", paragraph_style)
    width, height = cleaning_paragraph.wrap(line_width, line_height)
    cleaning_paragraph.drawOn(canvas, 1 * inch, y_position - height)
    y_position -= (height + 0.2 * inch
                   )  # Adjust the Y position for the next paragraph

    # ========STORAGE INSTRUCTIONS=========
    storage_paragraph = Paragraph(
        f"Storage Instructions: {storage_instructions}", paragraph_style)
    width, height = storage_paragraph.wrap(line_width, line_height)
    storage_paragraph.drawOn(canvas, 1 * inch, y_position - height)
    y_position -= (height + 0.2 * inch
                   )  # Adjust the Y position for the next element

    # ========TECHNICAL JARGON=========
    tech_jargon_paragraph = Paragraph(
        "In submitting this form, I agree to be solely responsible for the care, maintenance and cleanliness of the above-mentioned instrument(s). In case of damage or loss, I am obliged to inform my teacher-in-charge, and to abide by the guidelines set out by the school with regards to this loan.",
        paragraph_style)
    width, height = tech_jargon_paragraph.wrap(line_width, line_height)
    tech_jargon_paragraph.drawOn(canvas, 1 * inch, y_position - height)
    y_position -= (height + 0.2 * inch
                   )  # Adjust the Y position for the next element

    tech_jargon_paragraph = Paragraph(
        "I will return the instrument(s) in a timely manner according to the instructions given by my school either at the time of this loan, or at a later stipulated date.",
        paragraph_style)
    width, height = tech_jargon_paragraph.wrap(line_width, line_height)
    tech_jargon_paragraph.drawOn(canvas, 1 * inch, y_position - height)
    y_position -= (height + 0.2 * inch
                   )  # Adjust the Y position for the next element

    # ========SIGNATURE SECTION=========
    canvas.setFont("Times-Roman", 13)
    line_y_position = y_position - 1 * inch  # Adjust the Y position for the lines

    # Draw the signature lines and labels
    canvas.line(1 * inch, line_y_position, 4 * inch,
                line_y_position)  # Line for student signature
    canvas.drawString(1 * inch, line_y_position - 0.2 * inch,
                      "Name and Signature of Student")

    canvas.line(5 * inch, line_y_position, 7.5 * inch,
                line_y_position)  # Line for date
    canvas.drawString(5 * inch, line_y_position - 0.2 * inch, "Date")

    line_y_position -= 1 * inch  # Adjust the Y position for the next set of lines

    canvas.drawString(1 * inch, line_y_position, "Endorsed by:")

    line_y_position -= 0.5 * inch  # Adjust the Y position for the next set of lines

    canvas.line(1 * inch, line_y_position, 4 * inch,
                line_y_position)  # Line for CCA teacher signature
    canvas.drawString(1 * inch, line_y_position - 0.2 * inch,
                      "Name and Signature of CCA Teacher")

    canvas.line(5 * inch, line_y_position, 7.5 * inch,
                line_y_position)  # Line for date
    canvas.drawString(5 * inch, line_y_position - 0.2 * inch, "Date")

    canvas.save()

    canvas = Canvas("loan-return-sheet.pdf", pagesize=LETTER)
    canvas.setFont("Times-Roman", 18)

    image_path = "image.jpg"
    image_reader = ImageReader(image_path)
    image_width = image_reader.getSize()[0]
    image_height = image_reader.getSize()[1]

    # Line width and height (adjust these to your actual line dimensions)
    line_width = 7 * inch
    line_height = 1 * inch

    # Calculate scaling factors (maintain aspect ratio)
    horizontal_scaling_factor = line_width / image_width
    vertical_scaling_factor = line_height / image_height
    scaling_factor = min(horizontal_scaling_factor, vertical_scaling_factor)

    # Draw the scaled image
    canvas.drawInlineImage(
        image_path,
        1 * inch,  # X position
        9.4 * inch,  # Y position
        width=image_width * scaling_factor,
        height=image_height * scaling_factor,
    )

    canvas.drawString(2 * inch, 10 * inch, "St. Patrick's School")
    canvas.drawString(2 * inch, 9.6 * inch, "Loan Return Form")

    canvas.setFont("Times-Roman", 13)

    paragraph_style = ParagraphStyle(
        name='Normal',
        fontName='Times-Roman',
        fontSize=13,
        leading=15,
        leftIndent=0,
        firstLineIndent=0,  # Ensure no first-line indentation
        spaceAfter=0,
        spaceBefore=0)

    underline_paragraph_style = ParagraphStyle(
        name='Underline',
        parent=paragraph_style,
        textDecoration='underline'
    )

    styles = getSampleStyleSheet()

    # Define the initial Y position
    y_position = 8.75 * inch

    # ========LOAN ACKNOWLEDGEMENT=========
    intro_text = f"The following instruments have been returned to the school in good condition with thorough cleaning of the instrument"
    intro_paragraph = Paragraph(intro_text, paragraph_style)
    width, height = intro_paragraph.wrap(line_width, line_height)
    intro_paragraph.drawOn(canvas, 1 * inch, y_position - height)
    y_position -= (height + 0.2 * inch
                   )  # Adjust the Y position for the next paragraph

    # ========LOANED MODELS=========
    bullet_text = f"• Instrument: {guitar_model}, Serial Number: {serial_num}"
    bullet_paragraph = Paragraph(bullet_text, underline_paragraph_style)
    width, height = bullet_paragraph.wrap(line_width, line_height)
    bullet_paragraph.drawOn(canvas, 1 * inch, y_position - height)
    y_position -= (height + 0.2 * inch
                   )  # Adjust the Y position for the next paragraph

    # ========SIGNATURE SECTION=========
    canvas.setFont("Times-Roman", 13)
    line_y_position = y_position - 1 * inch  # Adjust the Y position for the lines

    # Draw the signature lines and labels
    canvas.line(1 * inch, line_y_position, 4 * inch,
                line_y_position)  # Line for student signature
    canvas.drawString(1 * inch, line_y_position - 0.2 * inch,
                      f"Name and Signature of Student")

    canvas.line(5 * inch, line_y_position, 7.5 * inch,
                line_y_position)  # Line for date
    canvas.drawString(5 * inch, line_y_position - 0.2 * inch, "Date")

    line_y_position -= 1 * inch  # Adjust the Y position for the next set of lines

    canvas.drawString(1 * inch, line_y_position, "Endorsed by:")

    line_y_position -= 0.5 * inch  # Adjust the Y position for the next set of lines

    canvas.line(1 * inch, line_y_position, 4 * inch,
                line_y_position)  # Line for CCA teacher signature
    canvas.drawString(1 * inch, line_y_position - 0.2 * inch,
                      "Name and Signature of CCA Teacher")

    canvas.line(5 * inch, line_y_position, 7.5 * inch,
                line_y_position)  # Line for date
    canvas.drawString(5 * inch, line_y_position - 0.2 * inch, "Date")

    canvas.save()

    filesToMerge = ["loan-sheet.pdf", "loan-return-sheet.pdf"]

    merger = PdfMerger()

    for pdf in filesToMerge:
        merger.append(pdf)

    merger.write(f"LOAN_FORM_{clas.upper()}_{name.upper()}.pdf")

    os.remove("loan-sheet.pdf")
    os.remove("loan-return-sheet.pdf")

    send_email(f"Guitar Loan for {name.upper()}",
               f"Dear QMs/Teachers,\nThis is the loan applied for by {name.upper()} on guitar {guitar_model} {serial_num}. File is attached "
               "accordingly.\nThis is an automated email, please do not reply to this email.\nThank you.",
               [email], f"LOAN_FORM_{clas.upper()}_{name.upper()}.pdf")

    os.remove(f"LOAN_FORM_{clas.upper()}_{name.upper()}.pdf")


def create_loa_pdf(name, date, reason):
    canvas = Canvas(f"LEAVE_OF_ABSENCE_{name.upper()}.pdf", pagesize=LETTER)
    canvas.setFont("Times-Roman", 18)

    image_path = "image.jpg"
    image_reader = ImageReader(image_path)
    image_width = image_reader.getSize()[0]
    image_height = image_reader.getSize()[1]

    # Line width and height (adjust these to your actual line dimensions)
    line_width = 7 * inch
    line_height = 1 * inch

    # Calculate scaling factors (maintain aspect ratio)
    horizontal_scaling_factor = line_width / image_width
    vertical_scaling_factor = line_height / image_height
    scaling_factor = min(horizontal_scaling_factor, vertical_scaling_factor)

    # Draw the scaled image
    canvas.drawInlineImage(
        image_path,
        1 * inch,  # X position
        9.4 * inch,  # Y position
        width=image_width * scaling_factor,
        height=image_height * scaling_factor,
    )

    canvas.drawString(2 * inch, 10 * inch, "St. Patrick's School")
    canvas.drawString(2 * inch, 9.6 * inch, "Leave-Of-Absence Information")

    canvas.setFont("Times-Roman", 13)

    paragraph_style = ParagraphStyle(
        name='Normal',
        fontName='Times-Roman',
        fontSize=13,
        leading=15,
        leftIndent=0,
        firstLineIndent=0,  # Ensure no first-line indentation
        spaceAfter=0,
        spaceBefore=0)

    underline_paragraph_style = ParagraphStyle(
        name='Underline',
        parent=paragraph_style,
        textDecoration='underline'
    )

    styles = getSampleStyleSheet()

    # Define the initial Y position
    y_position = 8.75 * inch

    # ========LOAN ACKNOWLEDGEMENT=========
    intro_text = f"I, <u>{name.title()}</u>, am not coming for CCA on <u>{date}</u> due to <u>{reason}</u>."
    intro_paragraph = Paragraph(intro_text, paragraph_style)
    width, height = intro_paragraph.wrap(line_width, line_height)
    intro_paragraph.drawOn(canvas, 1 * inch, y_position - height)
    y_position -= (height + 0.2 * inch
                   )  # Adjust the Y position for the next paragraph
    canvas.save()

    body = f"Dear Teachers/Attendance Takers, this is to inform you that student {name.upper()} is not coming for CCA on {date} due to {reason}. This is an automated email, please do not reply to this email"

    send_email(f"Leave-Of-Absence for {name.upper()}", body,
               ["advait_contractor@outlook.sg"],
               f"LEAVE_OF_ABSENCE_{name.upper()}.pdf")

    os.remove(f"LEAVE_OF_ABSENCE_{name.upper()}.pdf")

def verify_email(email):
    # A bit of help from CHAT here
    # Regex pattern for emails:
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    # Checking if pattern is in email
    if re.match(email_regex, email):
        return True

    return False
