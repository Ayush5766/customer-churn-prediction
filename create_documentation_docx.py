"""
Script to generate the comprehensive Word (.docx) Documentation & Interview Guide
for the Customer Churn Prediction project.
"""

from pathlib import Path
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    """Set background color of a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Set padding inside a table cell in dxa (1 pt = 20 dxa)."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)

def create_document():
    doc = Document()

    # Page Margins: 1 inch on all sides
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Styles & Colors
    # Primary: Deep Indigo (#1e1b4b), Accent: Violet (#6366f1), Secondary: Slate (#475569)
    COLOR_PRIMARY = RGBColor(30, 27, 75)
    COLOR_ACCENT = RGBColor(99, 102, 241)
    COLOR_TEXT = RGBColor(15, 23, 42)
    COLOR_MUTED = RGBColor(100, 116, 139)

    # Normal Style configuration
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = COLOR_TEXT
    normal_style.paragraph_format.line_spacing = 1.15
    normal_style.paragraph_format.space_after = Pt(6)

    # ---------------------------------------------------------------------------
    # Title & Header
    # ---------------------------------------------------------------------------
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(0)
    title_p.paragraph_format.space_after = Pt(4)
    run_title = title_p.add_run("Customer Churn Prediction: ML Model & REST API")
    run_title.font.name = 'Calibri'
    run_title.font.size = Pt(24)
    run_title.font.bold = True
    run_title.font.color.rgb = COLOR_PRIMARY

    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.space_after = Pt(18)
    run_sub = sub_p.add_run("Complete Technical Documentation, Architecture Guide & Interview Preparation Manual")
    run_sub.font.name = 'Calibri'
    run_sub.font.size = Pt(13)
    run_sub.font.color.rgb = COLOR_ACCENT
    run_sub.font.italic = True

    # Meta card / Callout
    meta_table = doc.add_table(rows=1, cols=1)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_cell = meta_table.cell(0, 0)
    meta_cell.width = Inches(6.5)
    set_cell_background(meta_cell, "F1F5F9")
    set_cell_margins(meta_cell, top=140, bottom=140, left=180, right=180)
    
    mp = meta_cell.paragraphs[0]
    mp.paragraph_format.space_after = Pt(0)
    mp.add_run("Author: ").bold = True
    mp.add_run("Kumar Ayush  |  ")
    mp.add_run("Project: ").bold = True
    mp.add_run("ChurnGuard  |  ")
    mp.add_run("Stack: ").bold = True
    mp.add_run("Python 3.10+, Scikit-learn, FastAPI, Vanilla Web (HTML5/CSS3/ES6)\n")
    mp.add_run("Target Audience: ").bold = True
    mp.add_run("Software Engineers, ML Engineers, Technical Recruiters & Hiring Managers")
    
    doc.add_paragraph() # Spacer

    # ---------------------------------------------------------------------------
    # Section 1: Executive Summary & Real-World Problem Solved
    # ---------------------------------------------------------------------------
    h1 = doc.add_heading(level=1)
    r1 = h1.add_run("1. Executive Summary & Real-World Problem Solved")
    r1.font.color.rgb = COLOR_PRIMARY

    doc.add_paragraph(
        "In modern subscription-based industries—such as telecommunications, SaaS platforms, and digital banking—"
        "customer retention is the single most vital metric dictating sustainable profitability. "
        "Industry data shows that acquiring a new customer costs 5 to 7 times more than retaining an existing one. "
        "When customers cancel service (known as 'churn'), companies suffer both direct revenue loss and customer acquisition waste."
    )

    doc.add_paragraph(
        "Traditional retention tactics are reactive: companies attempt to save customers only after they call customer support to cancel. "
        "At that point, cancellation is often inevitable. ChurnGuard solves this by moving retention from a reactive emergency "
        "to a proactive, automated retention intelligence workflow."
    )

    p_sol = doc.add_paragraph()
    p_sol.add_run("How This Project Solves the Problem:").bold = True
    
    sol_items = [
        ("Early Warning Detection", "Predicts churn probability in milliseconds when customer accounts show subtle warning signals (e.g. month-to-month contracts, lack of technical support, or payment friction)."),
        ("Preventing Discount Waste", "Identifies truly high-risk customers rather than blindly discounting everyone, saving marketing and retention budgets."),
        ("Actionable Playbooks", "Instantly recommends deterministic, localized business actions (such as plan locks, ₹500 bill credits, or onboarding outreach) tailored to that specific customer's profile."),
        ("Decoupled Integration", "Provides a production REST API that seamlessly integrates into enterprise CRMs (like Salesforce) or scheduled database batch pipelines.")
    ]
    for title, desc in sol_items:
        p = doc.add_paragraph(style='List Bullet')
        r_b = p.add_run(f"{title}: ")
        r_b.bold = True
        p.add_run(desc)

    doc.add_paragraph() # Spacer

    # ---------------------------------------------------------------------------
    # Section 2: Tools & Technologies Used (Part-by-Part & Step-by-Step)
    # ---------------------------------------------------------------------------
    h2 = doc.add_heading(level=1)
    r2 = h2.add_run("2. Tools & Technologies Used (Part-by-Part)")
    r2.font.color.rgb = COLOR_PRIMARY

    doc.add_paragraph(
        "Every tool in this project was selected deliberately to maintain a lightweight, production-grade microservice "
        "without external framework bloat or unnecessary dependencies."
    )

    tech_table = doc.add_table(rows=1, cols=3)
    tech_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr_cells = tech_table.rows[0].cells
    hdr_cells[0].text = "Technology / Library"
    hdr_cells[1].text = "Role in Project"
    hdr_cells[2].text = "Why It Was Chosen Over Alternatives"
    for c in hdr_cells:
        set_cell_background(c, "1E1B4B")
        c.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        c.paragraphs[0].runs[0].font.bold = True
        set_cell_margins(c, 120, 120, 140, 140)

    tech_rows = [
        ("Python 3.10+", "Core Language", "Industry standard for ML and modern async web frameworks. Offers strong typing support and excellent performance."),
        ("Pandas", "Data Cleaning & Wrangling", "Efficient dataframe handling; used to convert TotalCharges, drop null rows, encode targets, and structure inputs for inference."),
        ("Scikit-learn", "Machine Learning Pipeline", "Provides ColumnTransformer and Pipeline to bundle scaling, one-hot encoding, and Random Forest into an immutable production artifact."),
        ("FastAPI", "REST API & Static Web Server", "High-performance ASGI framework; natively integrates Pydantic validation, automatically generates OpenAPI Swagger docs, and serves frontend files."),
        ("Pydantic", "Input Validation & Data Contracts", "Enforces strict type checks, boundary bounds (ge=0, le=100), and custom Literal validation. Automatically rejects malformed inputs with 422 errors."),
        ("Uvicorn", "Lightning-Fast ASGI Server", "Handles concurrent asynchronous requests with minimal memory overhead, powering both API endpoints and the dashboard."),
        ("Joblib", "Model Serialization", "Optimized serialization format for scikit-learn estimators and pipelines containing large NumPy arrays."),
        ("Pytest + HTTPX", "Automated Integration Testing", "TestClient allows automated end-to-end testing of FastAPI lifespan, HTML delivery, valid predictions, and edge-case 422 rejections."),
        ("Vanilla Web (HTML5/CSS3/ES6)", "Modern Frontend Dashboard", "Zero npm, zero React bloat, zero build steps. Fast 60fps SVG gauge animations, responsive down to 360px mobile width, and native fetch API.")
    ]

    for tech, role, rationale in tech_rows:
        row_cells = tech_table.add_row().cells
        row_cells[0].text = tech
        row_cells[1].text = role
        row_cells[2].text = rationale
        for idx, c in enumerate(row_cells):
            set_cell_margins(c, 100, 100, 120, 120)
            if idx == 0:
                c.paragraphs[0].runs[0].font.bold = True

    doc.add_paragraph() # Spacer

    # ---------------------------------------------------------------------------
    # Section 3: Machine Learning Model & Evaluation (Real Results)
    # ---------------------------------------------------------------------------
    h3 = doc.add_heading(level=1)
    r3 = h3.add_run("3. Machine Learning Architecture & Real Results")
    r3.font.color.rgb = COLOR_PRIMARY

    doc.add_paragraph(
        "The model is trained on the public IBM Telco Customer Churn dataset (7,043 raw records). "
        "During data preparation, 11 records containing blank strings in TotalCharges were removed, "
        "leaving 7,032 validated customer records. Target column 'Churn' has a 26.6% churn rate (imbalanced classification)."
    )

    doc.add_paragraph(
        "To prevent data leakage, preprocessing is embedded into a scikit-learn ColumnTransformer:\n"
        "• Numerical features (tenure, MonthlyCharges, TotalCharges) are standardized using StandardScaler.\n"
        "• Categorical features (Contract, InternetService, PaymentMethod, PaperlessBilling, TechSupport, OnlineSecurity) "
        "are encoded using OneHotEncoder(handle_unknown='ignore')."
    )

    doc.add_paragraph("Real Model Comparison (Evaluated on 1,407 Stratified Test Customers):").bold = True

    eval_table = doc.add_table(rows=1, cols=4)
    eval_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    ehdrs = eval_table.rows[0].cells
    ehdrs[0].text = "Metric"
    ehdrs[1].text = "Logistic Regression"
    ehdrs[2].text = "Random Forest (Production)"
    ehdrs[3].text = "Why Random Forest Was Chosen"
    for c in ehdrs:
        set_cell_background(c, "1E1B4B")
        c.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        c.paragraphs[0].runs[0].font.bold = True
        set_cell_margins(c, 120, 120, 140, 140)

    eval_rows = [
        ("Accuracy", "72.71%", "76.90%", "Random Forest is +4.19% more accurate overall across the test cohort."),
        ("Precision", "49.19%", "55.66%", "+6.47% higher precision: avoids 120 false alarms (312 vs 192), saving discount budget."),
        ("Recall", "80.75%", "64.44%", "Logistic Regression caught more total churners but generated unacceptable false positives."),
        ("F1-Score", "0.6113", "0.5973", "Strong harmonic balance between precision and sensitivity across both algorithms."),
        ("ROC-AUC", "0.8360", "0.8086", "Both models demonstrate strong discriminatory capability (>0.80) across decision thresholds.")
    ]

    for m, lr, rf, comm in eval_rows:
        row = eval_table.add_row().cells
        row[0].text = m
        row[1].text = lr
        row[2].text = rf
        row[3].text = comm
        for idx, c in enumerate(row):
            set_cell_margins(c, 100, 100, 120, 120)
            if idx in [0, 2]:
                c.paragraphs[0].runs[0].font.bold = True

    doc.add_paragraph()
    doc.add_paragraph("Top Feature Drivers of Churn (Random Forest Importance Weights):").bold = True
    drivers = [
        ("Total spend to date (₹)", "22.87%", "Long-term investment and total expenditure reflect customer commitment."),
        ("Monthly charges (₹)", "21.71%", "Higher bill amounts create price friction, leading customers to shop for alternatives."),
        ("Time as customer (months)", "17.98%", "The newest customers (0-6 months) have the highest vulnerability to churn."),
        ("Month-to-month contract", "9.14%", "No commitment means friction-free cancellation whenever an issue arises."),
        ("No online security", "3.66%", "Subscribers without protection suites experience higher dissatisfaction."),
        ("Two-year contract", "3.61%", "Strongest anchor of retention; customers committed for 24 months rarely leave."),
        ("No technical support", "3.05%", "Unresolved connectivity problems accelerate cancellation decisions."),
        ("Fiber optic internet", "2.85%", "Fiber customers pay more; if speeds fluctuate, perceived value drops quickly.")
    ]
    for feat, imp, expl in drivers:
        p = doc.add_paragraph(style='List Bullet')
        r_f = p.add_run(f"{feat} ({imp}): ")
        r_f.bold = True
        p.add_run(expl)

    doc.add_paragraph() # Spacer

    # ---------------------------------------------------------------------------
    # Section 4: Do's and Don'ts for Technical Interviews
    # ---------------------------------------------------------------------------
    h4 = doc.add_heading(level=1)
    r4 = h4.add_run("4. Do's and Don'ts for Technical Interviews")
    r4.font.color.rgb = COLOR_PRIMARY

    doc.add_paragraph(
        "When explaining this project to interviewers, keep these critical guidelines in mind to establish credibility and seniority:"
    )

    dd_table = doc.add_table(rows=1, cols=2)
    dd_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    dd_hdrs = dd_table.rows[0].cells
    dd_hdrs[0].text = "DO (Best Practices to Highlight)"
    dd_hdrs[1].text = "DON'T (Common Fresher Traps to Avoid)"
    set_cell_background(dd_hdrs[0], "065F46") # Emerald
    set_cell_background(dd_hdrs[1], "991B1B") # Red
    for c in dd_hdrs:
        c.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        c.paragraphs[0].runs[0].font.bold = True
        set_cell_margins(c, 120, 120, 140, 140)

    dos_and_donts = [
        (
            "Explain WHY you selected Random Forest (higher precision prevents wasting expensive discounts on loyal customers).",
            "Say 'Accuracy was my main metric'. On an imbalanced dataset, accuracy alone is deceptive—always talk about Precision, Recall, and ROC-AUC."
        ),
        (
            "Emphasize that the scikit-learn Pipeline contains the ColumnTransformer inside it, eliminating data leakage and allowing raw JSON to be sent directly to the model.",
            "Say you scaled or one-hot encoded the whole dataset in Pandas before train_test_split (that causes data leakage, a major interview red flag)."
        ),
        (
            "State clearly that retention tips are rule-based business logic informed by feature importance, not raw model weights.",
            "Claim that the ML model 'invented' or generated the text tips by itself—interviewers know classifiers output probabilities, not English sentences."
        ),
        (
            "Frame this as an end-to-end microservice with Pydantic validation, health checks, and automated integration tests.",
            "Describe the project as 'just a Jupyter notebook with a machine learning model'."
        ),
        (
            "Acknowledge trade-offs: Logistic Regression had higher recall (80.7% vs 64.4%), but Random Forest cut false positives by 38.5%.",
            "Pretend your model is 100% perfect. Real engineers discuss trade-offs and threshold tuning."
        )
    ]

    for do_text, dont_text in dos_and_donts:
        row = dd_table.add_row().cells
        row[0].text = "✓ " + do_text
        row[1].text = "✗ " + dont_text
        set_cell_background(row[0], "F0FDF4") # Light green
        set_cell_background(row[1], "FEF2F2") # Light red
        for c in row:
            set_cell_margins(c, 100, 100, 120, 120)

    doc.add_paragraph() # Spacer

    # ---------------------------------------------------------------------------
    # Section 5: Future Implementations & Enterprise Scaling
    # ---------------------------------------------------------------------------
    h5 = doc.add_heading(level=1)
    r5 = h5.add_run("5. Future Implementations & Enterprise Scaling")
    r5.font.color.rgb = COLOR_PRIMARY

    doc.add_paragraph(
        "When an interviewer asks, 'If you had another month to work on this, how would you improve it?', "
        "share these concrete production enhancements:"
    )

    future_items = [
        ("Uplift Modeling (Causal Inference)", "Move from predicting churn to predicting 'uplift' (incremental impact). Uplift modeling identifies 'Persuadables'—customers who only stay if they receive an offer—avoiding wasted discounts on 'Sure Things' (who stay anyway) or 'Lost Causes' (who leave regardless)."),
        ("Explainable AI (SHAP / TreeSHAP)", "Integrate the shap library into the /predict endpoint to calculate exact local feature attributions for every individual inference call, explaining the exact positive and negative force of each feature on that specific user's bill."),
        ("Batch Pipeline & Database Ingestion", "Connect FastAPI to an enterprise data warehouse (Snowflake / PostgreSQL). Implement a Celery / Redis background worker that scores 100,000 customers in nightly batch jobs and alerts account managers on high-risk accounts."),
        ("Automated Retraining & Drift Monitoring", "Implement Evidently AI or MLflow to monitor data drift (e.g., changes in customer spending habits or new plan offerings) and trigger automated re-training pipelines."),
        ("Containerization & Cloud Deployment", "Package the FastAPI application in a multi-stage Docker container and deploy via AWS ECS (Fargate) or Google Cloud Run behind an Application Load Balancer with HTTPS.")
    ]

    for title, desc in future_items:
        p = doc.add_paragraph(style='List Bullet')
        r_t = p.add_run(f"{title}: ")
        r_t.bold = True
        p.add_run(desc)

    doc.add_paragraph() # Spacer

    # ---------------------------------------------------------------------------
    # Section 6: Top 10 Technical Interview Questions & Model Answers
    # ---------------------------------------------------------------------------
    h6 = doc.add_heading(level=1)
    r6 = h6.add_run("6. Top 10 Technical Interview Questions & Model Answers")
    r6.font.color.rgb = COLOR_PRIMARY

    qas = [
        (
            "Q1: Can you walk me through the high-level architecture of this application?",
            "ChurnGuard is a decoupled, production-grade microservice. The core is a scikit-learn Pipeline containing a ColumnTransformer (StandardScaler + OneHotEncoder) and a 200-tree Random Forest classifier. This pipeline is serialized with Joblib and served via a FastAPI REST API running on Uvicorn. The API features Pydantic request validation, a deterministic retention rule engine, and static file serving for a responsive, zero-framework HTML5/CSS3/ES6 web dashboard."
        ),
        (
            "Q2: Why did you embed preprocessing inside the pipeline instead of handling it beforehand in Pandas?",
            "Embedding StandardScaler and OneHotEncoder directly inside the Pipeline guarantees zero data leakage between training and test sets. In production, it ensures the API can receive raw JSON payloads (e.g. text contracts, unscaled tenure) and transform them automatically without having to duplicate transformation logic in the web application."
        ),
        (
            "Q3: How did you handle missing values in the Telco dataset?",
            "In the raw dataset, TotalCharges contained 11 blank space strings (' ') for brand-new customers with tenure equal to 0. We used pd.to_numeric with errors='coerce' to turn blanks into NaNs, then cleanly dropped those 11 rows. Dropping customerID was also essential because unique identifier strings possess zero generalizable predictive value."
        ),
        (
            "Q4: What was your strategy for class imbalance?",
            "The dataset has an imbalanced 26.6% churn rate. We used stratify=y in train_test_split to maintain identical target proportions in both the 80% train and 20% test partitions. Additionally, we set class_weight='balanced' in both Logistic Regression and Random Forest to apply higher loss penalties for misclassifying the minority churn class."
        ),
        (
            "Q5: Why did you pick Random Forest over Logistic Regression despite Logistic Regression having higher Recall?",
            "Logistic Regression achieved 80.75% recall but only 49.19% precision, generating 312 false alarms. In a telecom enterprise, false alarms waste valuable retention discounts on customers who were never leaving. Random Forest achieved 76.90% accuracy and 55.66% precision, reducing false alarms by 38.5% (192 false positives) while still detecting 64.44% of true churners."
        ),
        (
            "Q6: How does FastAPI validate incoming customer data?",
            "We defined a Pydantic schema called CustomerData. It enforces type constraints, boundary rules (tenure between 0 and 100, charges >= 0), and strict Literal types for categories (e.g. Contract must be 'Month-to-month', 'One year', or 'Two year'). If an invalid value is received, FastAPI intercepts it immediately and returns an HTTP 422 Unprocessable Entity error before it reaches the model."
        ),
        (
            "Q7: Why did you build the front end in plain HTML, CSS, and Vanilla JavaScript instead of React?",
            "For an interactive microservice, plain HTML5, CSS3, and ES6 eliminated node_modules, build pipelines, and separate frontend hosting. The entire application—API, model inference, and UI—is served from a single FastAPI process via Uvicorn. The UI uses native modern APIs: fetch() for async HTTP calls and requestAnimationFrame for 60fps gauge animations."
        ),
        (
            "Q8: How does the model load into FastAPI without slowing down individual user requests?",
            "We use FastAPI's lifespan context manager. The 36MB serialized model pipeline is loaded into server memory once when Uvicorn boots up. When a POST /predict request arrives, inference executes in-memory in under 10 milliseconds, enabling high concurrency without repeated disk I/O."
        ),
        (
            "Q9: What are the top 3 drivers of customer churn in your findings?",
            "Our feature importance analysis revealed: 1) Total spend to date (22.87%), 2) Monthly charges (21.71%), and 3) Time as customer (17.98%). This confirms that price sensitivity and the critical early tenure window (first 6 months) are the dominant factors influencing subscriber attrition."
        ),
        (
            "Q10: How would you deploy this project to AWS or Google Cloud in production?",
            "I would package the application using a multi-stage Dockerfile containing Python, requirements.txt, models, and static assets. The container would be pushed to Amazon ECR and run on AWS ECS Fargate or Google Cloud Run behind an Application Load Balancer with auto-scaling based on CPU and request latency."
        )
    ]

    for q, a in qas:
        p_q = doc.add_paragraph()
        p_q.paragraph_format.space_before = Pt(8)
        p_q.paragraph_format.space_after = Pt(2)
        r_q = p_q.add_run(q)
        r_q.bold = True
        r_q.font.color.rgb = COLOR_PRIMARY

        p_a = doc.add_paragraph()
        p_a.paragraph_format.space_after = Pt(6)
        p_a.add_run(a)

    # ---------------------------------------------------------------------------
    # Save the document
    # ---------------------------------------------------------------------------
    out_dir = Path(__file__).resolve().parent
    out_file = out_dir / "Customer_Churn_Prediction_Interview_Guide_and_Documentation.docx"
    doc.save(out_file)
    print(f"Documentation Word file created successfully at: {out_file}")

if __name__ == "__main__":
    create_document()
