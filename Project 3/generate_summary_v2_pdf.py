"""
Generate a one-page TECHNICAL summary PDF report for Steps 1-3 (v2 - post data-quality fixes).
"""
import os
import sys
import traceback
from fpdf import FPDF

OUTPUT_PATH = 'Pipeline_Summary_Report_v2.pdf'

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
        self.cell(0, 8, 'Clinical Readmission Pipeline - Executive Summary (v2)', new_x='LMARGIN', new_y='NEXT')
        self.set_font('Helvetica', '', 10)
        self.set_x(10)
        self.cell(0, 6, 'Steps 1-3: EDA -> Cleaning -> Feature Engineering  |  Target: Readmission_30d  |  2026-09-02', new_x='LMARGIN', new_y='NEXT')
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
        self.multi_cell(184, 5, f'- {text}')


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
                                    '100% null columns (Extra_Col_1/2); invalid values (Age up to 999, negative weights); '
                                    'inconsistent Gender entries; 50+ Drug_Name typo variants.')
    pdf.kv_row('Outputs generated:', 'step1_clinical_distributions.png, step1_correlation_matrix.png')
    pdf.ln(2)

    # ---- Step 2 ----
    pdf.section_title('Step 2 - Data Cleaning & Preprocessing (re-executed)')
    pdf.bullet('Column reduction: dropped 11 columns (nulls, duplicates, redundant) -> 41 to 30 columns')
    pdf.bullet('Row validation: removed 37,988 rows with invalid Age/Weight')
    pdf.bullet('Missing target rows: dropped 81,110 rows without a Readmission_30d label')
    pdf.bullet('Gender fix: standardized to 4 clean categories - Male 276,523 | Female 276,586 | '
               'Other 117,968 | Unknown 445,935 (previously 10+ inconsistent raw tokens)')
    pdf.bullet('Drug_Name fix: typos normalized (e.g., amoxicilin/amoxycillin -> amoxicillin) and grouped '
               'into 22 therapeutic classes (Antibiotic, Statin, ACE Inhibitor, Insulin, NSAID, etc.); '
               'raw Drug_Name dropped in favor of Drug_Class')
    pdf.bullet('Imputation: numeric columns filled with median, categorical with mode')
    pdf.bullet('Duplicates removed: 63,982 duplicate rows dropped')
    pdf.bullet('Outlier capping (IQR): Age, BMI, Dosage, Hemoglobin, Creatinine, ALT/AST enzymes')
    pdf.bullet('Encoding: label-encoded Gender; one-hot encoded Drug_Class and Route (was raw Drug_Name)')
    pdf.ln(1)
    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.set_text_color(*BLUE)
    pdf.cell(0, 6, 'Final output: data_cleaned_v2.csv -> 971,920 rows x 183 columns (was 553)', new_x='LMARGIN', new_y='NEXT')
    pdf.set_text_color(*DARK)
    pdf.set_font('Helvetica', 'I', 8.5)
    pdf.set_text_color(*GREEN)
    pdf.multi_cell(184, 4.5, 'Watch-outs resolved: Gender inconsistency and Drug_Name cardinality issues from the '
                             'prior report have both been fixed in this re-execution.')
    pdf.set_text_color(*DARK)
    pdf.ln(2)

    # ---- Step 3 ----
    pdf.section_title('Step 3 - Feature Engineering (re-executed)')
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
    pdf.cell(0, 6, 'Final output: data_engineered_v2.csv -> 971,920 rows x 190 columns (was 560)', new_x='LMARGIN', new_y='NEXT')
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
        ('2. Cleaning (v2)', 'Complete', 'Gender + Drug_Name fixes applied; minor deprecation warnings only'),
        ('3. Feature Eng. (v2)', 'Complete', 'Performance warnings (fragmentation) only, no data loss'),
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
    pdf.cell(0, 6, 'Next Step: Step 4 - Model Training & Evaluation on data_engineered_v2.csv', new_x='LMARGIN', new_y='NEXT')

    pdf.output(OUTPUT_PATH)
    print(f'Saved PDF report: {os.path.abspath(OUTPUT_PATH)}')


if __name__ == '__main__':
    try:
        build_report()
    except Exception as e:
        print(f'ERROR generating PDF: {e}')
        traceback.print_exc()
        sys.exit(1)
