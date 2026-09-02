"""
Generate a one-page PDF summary report for Steps 1-3 of the clinical pipeline.
"""
import os
import sys
import traceback
from fpdf import FPDF

OUTPUT_PATH = 'Pipeline_Summary_Report.pdf'

BLUE = (31, 78, 121)
DARK = (40, 40, 40)
GREEN = (39, 128, 78)
RED = (178, 34, 52)
GRAY = (110, 110, 110)
LIGHT_BG = (240, 244, 248)


class ReportPDF(FPDF):
    def header(self):
        self.set_fill_color(*BLUE)
        self.rect(0, 0, 210, 22, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Helvetica', 'B', 16)
        self.set_xy(10, 5)
        self.cell(0, 8, 'Clinical Readmission Pipeline - Executive Summary', new_x='LMARGIN', new_y='NEXT')
        self.set_font('Helvetica', '', 10)
        self.set_x(10)
        self.cell(0, 6, 'Steps 1-3: EDA -> Cleaning -> Feature Engineering  |  Target: Readmission_30d  |  2026-09-01', new_x='LMARGIN', new_y='NEXT')
        self.ln(4)
        self.set_text_color(*DARK)

    def section_title(self, title, color=BLUE):
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(*color)
        self.cell(0, 8, title, new_x='LMARGIN', new_y='NEXT')
        self.set_draw_color(*color)
        self.set_line_width(0.4)
        y = self.get_y()
        self.line(10, y, 200, y)
        self.ln(2)
        self.set_text_color(*DARK)

    def kv_row(self, label, value, value_color=DARK):
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(*DARK)
        self.set_x(10)
        self.cell(0, 5.5, label, new_x='LMARGIN', new_y='NEXT')
        if value:
            self.set_font('Helvetica', '', 9)
            self.set_text_color(*value_color)
            self.set_x(14)
            self.multi_cell(186, 5.5, value)

    def bullet(self, text, color=DARK):
        self.set_font('Helvetica', '', 9)
        self.set_text_color(*color)
        self.set_x(14)
        self.multi_cell(0, 5, f'- {text}')


def build_report():
    pdf = ReportPDF(format='A4', unit='mm')
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()

    # ---- Step 1 ----
    pdf.section_title('Step 1 - Data Collection & Exploration')
    pdf.kv_row('Records loaded:', '1,155,000 patients  |  41 raw features')
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_x(10)
    pdf.cell(0, 5.5, 'Target balance:', new_x='LMARGIN', new_y='NEXT')
    pdf.set_x(14)
    pdf.set_text_color(*GREEN)
    pdf.cell(90, 5.5, 'Not Readmitted: 84.98% (910,243)', new_x='RIGHT', new_y='TOP')
    pdf.set_text_color(*RED)
    pdf.cell(0, 5.5, 'Readmitted: 15.02% (160,918) - imbalanced', new_x='LMARGIN', new_y='NEXT')
    pdf.set_text_color(*DARK)
    pdf.kv_row('Key issues found:', 'Duplicate case-mismatched columns (Age/age, Gender/gender, Drug_Name/drug_name); '
                                    '100% null columns (Extra_Col_1/2); invalid values (Age up to 999, negative weights)')
    pdf.kv_row('Outputs generated:', 'step1_clinical_distributions.png, step1_correlation_matrix.png')
    pdf.ln(3)

    # ---- Step 2 ----
    pdf.section_title('Step 2 - Data Cleaning & Preprocessing')
    pdf.bullet('Column reduction: dropped 11 columns (nulls, duplicates, redundant) -> 41 to 30 columns')
    pdf.bullet('Row validation: removed 37,988 rows with invalid Age/Weight')
    pdf.bullet('Missing target rows: dropped 81,110 rows without a Readmission_30d label')
    pdf.bullet('Imputation: numeric columns filled with median, categorical with mode')
    pdf.bullet('Duplicates removed: 63,351 duplicate rows dropped')
    pdf.bullet('Outlier capping (IQR): Age, BMI, Dosage, Hemoglobin, Creatinine, ALT/AST enzymes')
    pdf.bullet('Encoding: label-encoded Gender; one-hot encoded Drug_Name and Route')
    pdf.ln(1)
    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.set_text_color(*BLUE)
    pdf.cell(0, 6, 'Final output: data_cleaned.csv -> 972,551 rows x 553 columns', new_x='LMARGIN', new_y='NEXT')
    pdf.set_text_color(*DARK)
    pdf.set_font('Helvetica', 'I', 8.5)
    pdf.set_text_color(*RED)
    pdf.multi_cell(0, 4.5, 'Data quality note: Gender retains messy raw values (MAL, FEMAL, O, N/A, etc.); '
                           'high-cardinality Drug_Name one-hot encoding inflated column count. '
                           'Recommend consolidating before modeling.')
    pdf.set_text_color(*DARK)
    pdf.ln(2)

    # ---- Step 3 ----
    pdf.section_title('Step 3 - Feature Engineering')
    pdf.set_font('Helvetica', '', 9)
    features = [
        ('kidney_stage', 'eGFR-based staging (Normal/Mild/Moderate/Severe)'),
        ('liver_risk', 'Flag if ALT or AST > 40'),
        ('polypharmacy', 'Flag if 5+ concurrent medications'),
        ('bmi_category', 'Underweight/Normal/Overweight/Obese'),
        ('age_group', 'Pediatric through Elderly bands'),
        ('elderly_high_dose', 'Age > 65 and above-median dosage'),
        ('de_ritis_ratio', 'AST/ALT ratio (liver disease indicator)'),
    ]
    for name, desc in features:
        pdf.set_x(14)
        pdf.set_font('Helvetica', 'B', 9)
        pdf.cell(38, 5, name, new_x='RIGHT', new_y='TOP')
        pdf.set_font('Helvetica', '', 9)
        pdf.cell(0, 5, desc, new_x='LMARGIN', new_y='NEXT')
    pdf.ln(1)
    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.set_text_color(*BLUE)
    pdf.cell(0, 6, 'Final output: data_engineered.csv -> 972,551 rows x 560 columns', new_x='LMARGIN', new_y='NEXT')
    pdf.set_text_color(*DARK)
    pdf.ln(2)

    # ---- Status table ----
    pdf.section_title('Pipeline Status', color=GREEN)
    col_w = [45, 30, 115]
    headers = ['Step', 'Status', 'Runtime Notes']
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_fill_color(*LIGHT_BG)
    for w, h in zip(col_w, headers):
        pdf.cell(w, 7, h, border=1, fill=True)
    pdf.ln()
    rows = [
        ('1. EDA', 'Complete', 'No errors'),
        ('2. Cleaning', 'Complete', 'Minor deprecation warnings only'),
        ('3. Feature Engineering', 'Complete', 'Performance warnings (fragmentation) only, no data loss'),
    ]
    pdf.set_font('Helvetica', '', 9)
    for step, status, notes in rows:
        pdf.cell(col_w[0], 7, step, border=1)
        pdf.set_text_color(*GREEN)
        pdf.cell(col_w[1], 7, status, border=1)
        pdf.set_text_color(*DARK)
        pdf.cell(col_w[2], 7, notes, border=1)
        pdf.ln()

    pdf.ln(4)
    pdf.set_font('Helvetica', 'BI', 10)
    pdf.set_text_color(*BLUE)
    pdf.cell(0, 6, 'Next Step: Step 4 - Model Training & Evaluation on data_engineered.csv', new_x='LMARGIN', new_y='NEXT')

    pdf.output(OUTPUT_PATH)
    print(f'Saved PDF report: {os.path.abspath(OUTPUT_PATH)}')


if __name__ == '__main__':
    try:
        build_report()
    except Exception as e:
        print(f'ERROR generating PDF: {e}')
        traceback.print_exc()
        sys.exit(1)
