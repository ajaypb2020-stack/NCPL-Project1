"""
Generate a one-page BUSINESS-FOCUSED PDF report for Steps 1-3 of the clinical pipeline (v2 - post data-quality fixes).
"""
import os
import sys
import traceback
from fpdf import FPDF

OUTPUT_PATH = 'Pipeline_Business_Report_v2.pdf'

NAVY = (24, 58, 92)
TEAL = (18, 128, 122)
GOLD = (196, 143, 24)
DARK = (45, 45, 45)
GREEN = (39, 128, 78)
RED = (178, 34, 52)
LIGHT_BG = (238, 244, 248)
WHITE = (255, 255, 255)


class BizPDF(FPDF):
    def header(self):
        self.set_fill_color(*NAVY)
        self.rect(0, 0, 210, 26, 'F')
        self.set_text_color(*WHITE)
        self.set_font('Helvetica', 'B', 17)
        self.set_xy(10, 5)
        self.cell(0, 9, 'Patient Readmission Risk Initiative', new_x='LMARGIN', new_y='NEXT')
        self.set_font('Helvetica', '', 10.5)
        self.set_x(10)
        self.cell(0, 6, 'Business Summary  |  Data Readiness Update (v2)  |  2 September 2026', new_x='LMARGIN', new_y='NEXT')
        self.ln(6)
        self.set_text_color(*DARK)

    def band(self, title, color=NAVY):
        self.set_fill_color(*color)
        self.set_text_color(*WHITE)
        self.set_font('Helvetica', 'B', 11.5)
        self.cell(0, 7.5, f'  {title}', fill=True, new_x='LMARGIN', new_y='NEXT')
        self.set_text_color(*DARK)
        self.ln(1.5)

    def bullet(self, text, bold_lead=None):
        self.set_font('Helvetica', '', 9.3)
        self.set_x(13)
        if bold_lead:
            self.set_font('Helvetica', 'B', 9.3)
            self.write(4.6, f'- {bold_lead} ')
            self.set_font('Helvetica', '', 9.3)
            self.write(4.6, text)
            self.ln(5)
        else:
            self.multi_cell(184, 4.6, f'- {text}')


def build_report():
    pdf = BizPDF(format='A4', unit='mm')
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.add_page()

    # ---- Executive Summary ----
    pdf.band('Executive Summary')
    pdf.set_font('Helvetica', '', 9.3)
    pdf.set_x(13)
    pdf.multi_cell(184, 4.8,
        "Over 1.1 million patient records were processed to build a foundation for predicting 30-day "
        "hospital readmissions. After cleaning, standardizing, and enriching the data, we retained a "
        "high-quality analytical base of 971,920 patients ready for predictive modeling. Roughly 1 in 7 "
        "patients (15%) in this population was readmitted within 30 days. This update also resolves the "
        "two data-quality issues flagged previously - inconsistent gender entries and excessive drug-name "
        "variety - resulting in a leaner, more interpretable dataset (183 columns, down from 553).")
    pdf.ln(2)

    # ---- Key Business Metrics (scorecard) ----
    pdf.band('Key Numbers at a Glance', color=TEAL)
    metrics = [
        ('1,155,000', 'Patient records analyzed'),
        ('971,920', 'Clean, analysis-ready patient records'),
        ('15.0%', 'Patients readmitted within 30 days'),
        ('183', 'Final feature columns (was 553 pre-fix)'),
    ]
    col_w = 46
    pdf.set_x(13)
    y_start = pdf.get_y()
    for i, (num, label) in enumerate(metrics):
        x = 13 + i * col_w
        pdf.set_xy(x, y_start)
        pdf.set_fill_color(*LIGHT_BG)
        pdf.rect(x, y_start, col_w - 2, 20, 'F')
        pdf.set_xy(x, y_start + 2)
        pdf.set_font('Helvetica', 'B', 14)
        pdf.set_text_color(*NAVY)
        pdf.cell(col_w - 2, 8, num, align='C', new_x='LEFT', new_y='NEXT')
        pdf.set_xy(x, y_start + 11)
        pdf.set_font('Helvetica', '', 7.6)
        pdf.set_text_color(*DARK)
        pdf.multi_cell(col_w - 2, 3.4, label, align='C')
    pdf.set_y(y_start + 23)
    pdf.set_text_color(*DARK)

    # ---- What was done, in business terms ----
    pdf.band('What We Did (Steps 1-3)')
    pdf.bullet('reviewed 1.1M patient records, uncovering data entry errors (e.g., invalid ages), '
               'duplicate/inconsistent fields, and a significant imbalance between readmitted and non-readmitted patients.',
               bold_lead='Step 1 - Explored the raw data:')
    pdf.bullet('removed unusable and duplicate records, corrected invalid entries, filled in gaps using '
               'statistically sound methods, standardized gender into 4 clear categories (Male/Female/Other/Unknown), '
               'and grouped 50+ inconsistent drug-name variants into 22 therapeutic classes.',
               bold_lead='Step 2 - Cleaned & standardized the data:')
    pdf.bullet('added 7 clinically meaningful indicators - kidney function stage, liver risk, '
               'polypharmacy risk, BMI category, age group, elderly high-dose flag, and a liver-disease ratio - '
               'to make the data more predictive and clinically interpretable.',
               bold_lead='Step 3 - Engineered new risk signals:')
    pdf.ln(1)

    # ---- Business value / risk insights ----
    pdf.band('Why This Matters', color=GOLD)
    pdf.bullet('Every percentage-point reduction in 30-day readmissions translates directly into lower '
               'penalty exposure and improved patient outcomes.')
    pdf.bullet('New risk flags (polypharmacy, kidney/liver risk, elderly high-dose) give care teams early, '
               'explainable warning signs - not just a black-box score.')
    pdf.bullet('Grouping drugs into therapeutic classes (e.g., Statin, Antibiotic, Insulin) makes the model '
               'more interpretable to clinicians and less prone to overfitting on rare drug spellings.')
    pdf.bullet('A clean, standardized dataset of ~972K patients means predictive models trained next will be '
               'more accurate and trustworthy for clinical decision-making.')
    pdf.ln(1)

    # ---- Resolved data quality items ----
    pdf.band('Data Quality - Resolved This Update', color=GREEN)
    pdf.bullet('Gender field standardized to Male / Female / Other / Unknown, replacing 10+ inconsistent raw '
               'entries (e.g., "MAL", "0", "N/A"). Root-cause fix recommended at point of data capture.')
    pdf.bullet('Drug name variety (50+ spellings/typos) consolidated into 22 therapeutic classes (e.g., Statin, '
               'Antibiotic, Insulin), cutting dataset width from 553 to 183 columns for better model performance.')
    pdf.ln(2)

    # ---- Next steps ----
    pdf.set_fill_color(*NAVY)
    pdf.set_text_color(*WHITE)
    pdf.set_font('Helvetica', 'B', 10.5)
    pdf.set_x(13)
    pdf.cell(184, 8, '  Next Step: Build & validate the readmission prediction model (Step 4)', fill=True,
             new_x='LMARGIN', new_y='NEXT')

    pdf.output(OUTPUT_PATH)
    print(f'Saved PDF report: {os.path.abspath(OUTPUT_PATH)}')


if __name__ == '__main__':
    try:
        build_report()
    except Exception as e:
        print(f'ERROR generating PDF: {e}')
        traceback.print_exc()
        sys.exit(1)
