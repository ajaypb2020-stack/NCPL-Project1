"""Generate the final one-page business report for the clinical pipeline."""
import os
import sys
import traceback
from fpdf import FPDF

OUTPUT_PATH = 'Clinical_Readmission_Final_Business_Report.pdf'
NAVY = (24, 58, 92)
TEAL = (18, 128, 122)
GOLD = (196, 143, 24)
GREEN = (39, 128, 78)
RED = (178, 34, 52)
DARK = (45, 45, 45)
LIGHT = (238, 244, 248)
WHITE = (255, 255, 255)


class BusinessReport(FPDF):
    def header(self):
        self.set_fill_color(*NAVY)
        self.rect(0, 0, 210, 25, 'F')
        self.set_text_color(*WHITE)
        self.set_font('Helvetica', 'B', 16)
        self.set_xy(10, 4)
        self.cell(0, 8, 'Patient Readmission Risk Initiative', new_x='LMARGIN', new_y='NEXT')
        self.set_font('Helvetica', '', 9.5)
        self.set_x(10)
        self.cell(0, 5, 'Final Business Report | Steps 1-6 | 2 September 2026 | Target: 30-day readmission', new_x='LMARGIN', new_y='NEXT')
        self.ln(6)
        self.set_text_color(*DARK)

    def band(self, title, color=NAVY):
        self.set_fill_color(*color)
        self.set_text_color(*WHITE)
        self.set_font('Helvetica', 'B', 10.5)
        self.cell(0, 7, f'  {title}', fill=True, new_x='LMARGIN', new_y='NEXT')
        self.set_text_color(*DARK)
        self.ln(1.5)

    def bullet(self, lead, body):
        self.set_x(13)
        self.set_font('Helvetica', 'B', 8.7)
        self.write(4.4, f'- {lead} ')
        self.set_font('Helvetica', '', 8.7)
        self.write(4.4, body)
        self.ln(4.7)


def build_report():
    pdf = BusinessReport(format='A4', unit='mm')
    pdf.set_auto_page_break(auto=True, margin=9)
    pdf.add_page()

    pdf.band('Executive Decision Summary')
    pdf.set_font('Helvetica', '', 8.8)
    pdf.set_x(13)
    pdf.multi_cell(184, 4.4,
        'The clinical data pipeline processed 1.155 million patient records and produced a standardized, '
        'model-ready dataset of 971,920 labeled patients. Data quality improvements reduced the feature space '
        'from 553 to 183 columns by normalizing Gender and grouping inconsistent medication names into 22 '
        'therapeutic classes. Three predictive models were executed successfully, but all produced AUC scores '
        'near 0.50, so the current data should support further investigation rather than operational deployment.')
    pdf.ln(1.5)

    pdf.band('Business Scorecard', TEAL)
    metrics = [
        ('1.155M', 'records analyzed'),
        ('971,920', 'labeled clean records'),
        ('15.0%', '30-day readmission rate'),
        ('183', 'final model features'),
    ]
    x0, y0, width = 13, pdf.get_y(), 46
    for index, (number, label) in enumerate(metrics):
        x = x0 + index * width
        pdf.set_fill_color(*LIGHT)
        pdf.rect(x, y0, width - 2, 18, 'F')
        pdf.set_xy(x, y0 + 1.5)
        pdf.set_font('Helvetica', 'B', 13)
        pdf.set_text_color(*NAVY)
        pdf.cell(width - 2, 7, number, align='C', new_x='LEFT', new_y='NEXT')
        pdf.set_xy(x, y0 + 10)
        pdf.set_font('Helvetica', '', 7.3)
        pdf.set_text_color(*DARK)
        pdf.multi_cell(width - 2, 3, label, align='C')
    pdf.set_y(y0 + 21)

    pdf.band('What Was Delivered')
    pdf.bullet('Step 1 - EDA:', 'identified missingness, invalid values, duplicate fields, two fully null columns, and class imbalance (84.98% not readmitted vs 15.02% readmitted). Generated distribution and correlation visuals.')
    pdf.bullet('Step 2 - Cleaning:', 'removed 37,988 invalid Age/Weight rows, 81,110 unlabeled rows, and 63,982 duplicates; median/mode imputation and IQR outlier capping were applied.')
    pdf.bullet('Data quality fix:', 'standardized Gender to Male/Female/Other/Unknown and corrected 50+ medication spellings into 22 therapeutic classes. Output: data_cleaned_v2.csv, 971,920 x 183.')
    pdf.bullet('Step 3 - Features:', 'created kidney stage, liver risk, polypharmacy, BMI category, age group, elderly high-dose, and AST/ALT ratio indicators. Output: data_engineered_v2.csv, 971,920 x 190.')
    pdf.ln(1)

    pdf.band('Model Results: Readmission Prediction', GOLD)
    headers = ['Model', 'Accuracy', 'AUC-ROC', 'Readmitted Recall', 'Readmitted F1']
    widths = [45, 28, 28, 42, 37]
    pdf.set_font('Helvetica', 'B', 8.2)
    pdf.set_fill_color(*LIGHT)
    for width_value, header in zip(widths, headers):
        pdf.cell(width_value, 6, header, border=1, fill=True, align='C')
    pdf.ln()
    pdf.set_font('Helvetica', '', 8.3)
    model_rows = [
        ('Decision Tree', '0.3007', '0.5021', '0.79', '0.25'),
        ('Random Forest', '0.5699', '0.5105', '0.42', '0.23'),
        ('XGBoost', '0.5317', '0.5057', '0.46', '0.23'),
    ]
    for row in model_rows:
        for width_value, value in zip(widths, row):
            pdf.cell(width_value, 6, value, border=1, align='C')
        pdf.ln()
    pdf.ln(1)
    pdf.set_font('Helvetica', 'I', 8.3)
    pdf.set_text_color(*RED)
    pdf.multi_cell(184, 4, 'Business interpretation: AUC values are close to random-chance performance (0.50). The models are not ready for clinical decisions, financial forecasting, or automated intervention without improving the underlying signal and validating against an independent dataset.')
    pdf.set_text_color(*DARK)
    pdf.ln(1)

    pdf.band('Business Value and Recommended Actions', GREEN)
    pdf.bullet('Value created:', 'a repeatable data foundation, explainable clinical risk indicators, cleaner medication taxonomy, and validated model artifacts for controlled experimentation.')
    pdf.bullet('Immediate action:', 'investigate target quality, feature/target relationships, temporal leakage, label definition, and whether the source data contains enough predictive signal.')
    pdf.bullet('Before deployment:', 'benchmark against a majority-class baseline, use temporal or external validation, review precision-recall tradeoffs, and obtain clinical governance approval.')
    pdf.bullet('Artifacts:', 'decision_tree_model.pkl, random_forest_model_v2.pkl, xgboost_best_model_v2.pkl, feature-importance plots, EDA visuals, and two-page-ready summary reports are available in outputs/.')

    pdf.set_fill_color(*NAVY)
    pdf.set_text_color(*WHITE)
    pdf.set_font('Helvetica', 'B', 9.7)
    pdf.set_x(13)
    pdf.cell(184, 7.5, '  Recommendation: proceed to model diagnostics and data-source improvement before production use.', fill=True, new_x='LMARGIN', new_y='NEXT')

    pdf.output(OUTPUT_PATH)
    print(f'Saved final PDF: {os.path.abspath(OUTPUT_PATH)}')


if __name__ == '__main__':
    try:
        build_report()
    except Exception as error:
        print(f'ERROR generating final report: {error}')
        traceback.print_exc()
        sys.exit(1)
