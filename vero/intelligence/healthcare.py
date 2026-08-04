"""
VERO Intelligence Library

Healthcare and Life Sciences Ontology

This module defines the master healthcare ontology used by VERO's
industry, technology, business-model, competitor, risk, and scoring
engines.

Version: 1.0
"""

from __future__ import annotations


HEALTHCARE: dict[str, object] = {
    "name": "Healthcare",

    "aliases": [
        "healthcare",
        "health care",
        "healthtech",
        "health tech",
        "digital health",
        "medical technology",
        "medical software",
        "health software",
        "clinical technology",
        "clinical software",
        "life sciences",
        "medtech",
        "medical innovation",
        "health services",
        "care delivery",
        "patient care",
        "health platform",
    ],

    "subindustries": {
        "Digital Health": [
            "digital health",
            "health app",
            "healthcare app",
            "mobile health",
            "mhealth",
            "digital care",
            "virtual care",
            "health platform",
            "patient platform",
            "digital health platform",
            "health engagement",
            "consumer health",
            "digital medicine",
            "connected health",
            "remote health",
            "health software",
        ],

        "Telemedicine": [
            "telemedicine",
            "telehealth",
            "virtual care",
            "virtual doctor",
            "online doctor",
            "video consultation",
            "remote consultation",
            "digital clinic",
            "virtual clinic",
            "online clinic",
            "remote diagnosis",
            "virtual healthcare",
            "virtual visit",
            "remote medical care",
            "online healthcare",
        ],

        "Primary Care": [
            "primary care",
            "family medicine",
            "general practice",
            "primary care clinic",
            "direct primary care",
            "concierge medicine",
            "community health",
            "preventive care",
            "routine care",
            "patient-centered care",
            "care coordination",
            "longitudinal care",
        ],

        "Specialty Care": [
            "specialty care",
            "specialist care",
            "specialty clinic",
            "cardiology",
            "dermatology",
            "neurology",
            "gastroenterology",
            "orthopedics",
            "rheumatology",
            "endocrinology",
            "urology",
            "oncology",
            "ophthalmology",
            "otolaryngology",
            "specialist network",
        ],

        "Mental Health": [
            "mental health",
            "behavioral health",
            "therapy",
            "online therapy",
            "digital therapy",
            "mental wellness",
            "psychiatry",
            "psychology",
            "counseling",
            "behavioral therapy",
            "mental health platform",
            "employee mental health",
            "stress management",
            "anxiety support",
            "depression support",
            "emotional wellness",
            "crisis support",
        ],

        "Women's Health": [
            "women's health",
            "womens health",
            "femtech",
            "female health",
            "reproductive health",
            "fertility",
            "pregnancy care",
            "maternal health",
            "menopause care",
            "menstrual health",
            "pelvic health",
            "prenatal care",
            "postpartum care",
            "gynecology",
            "obstetrics",
            "birth control",
            "family planning",
        ],

        "Men's Health": [
            "men's health",
            "mens health",
            "male health",
            "urology care",
            "testosterone care",
            "sexual health",
            "fertility care",
            "prostate health",
            "hair loss treatment",
            "men's wellness",
        ],

        "Pediatrics": [
            "pediatrics",
            "pediatric care",
            "children's health",
            "child health",
            "infant care",
            "adolescent health",
            "pediatric telehealth",
            "family health",
            "child development",
            "pediatric clinic",
        ],

        "Senior Care": [
            "senior care",
            "elder care",
            "elderly care",
            "aging care",
            "geriatric care",
            "aging in place",
            "senior living",
            "assisted living",
            "home care",
            "long-term care",
            "caregiver support",
            "memory care",
            "eldercare technology",
        ],

        "Home Health": [
            "home health",
            "home healthcare",
            "in-home care",
            "home nursing",
            "home medical care",
            "home care platform",
            "caregiver platform",
            "home monitoring",
            "house call",
            "mobile care",
            "care at home",
        ],

        "Remote Patient Monitoring": [
            "remote patient monitoring",
            "rpm",
            "patient monitoring",
            "remote monitoring",
            "continuous monitoring",
            "connected medical device",
            "wearable monitoring",
            "chronic care monitoring",
            "home monitoring",
            "vital signs monitoring",
            "remote diagnostics",
            "patient telemetry",
        ],

        "Chronic Care": [
            "chronic care",
            "chronic disease management",
            "diabetes management",
            "hypertension management",
            "heart disease management",
            "copd management",
            "asthma management",
            "chronic condition platform",
            "care management",
            "disease management",
            "population health",
            "long-term condition management",
        ],

        "Diabetes Care": [
            "diabetes care",
            "diabetes management",
            "blood glucose monitoring",
            "continuous glucose monitoring",
            "cgm",
            "insulin management",
            "diabetes coaching",
            "metabolic health",
            "glucose tracking",
            "diabetes platform",
        ],

        "Cardiovascular Health": [
            "cardiovascular health",
            "heart health",
            "cardiology",
            "cardiac care",
            "heart monitoring",
            "ecg monitoring",
            "ekg monitoring",
            "blood pressure monitoring",
            "stroke prevention",
            "cardiac diagnostics",
            "heart disease management",
        ],

        "Oncology": [
            "oncology",
            "cancer care",
            "cancer treatment",
            "cancer diagnostics",
            "precision oncology",
            "tumor detection",
            "cancer screening",
            "chemotherapy management",
            "radiation oncology",
            "oncology platform",
            "cancer research",
            "cancer therapeutics",
        ],

        "Neurology": [
            "neurology",
            "brain health",
            "neurological care",
            "neuroscience",
            "neurological diagnostics",
            "epilepsy monitoring",
            "parkinson's care",
            "alzheimers care",
            "multiple sclerosis",
            "brain imaging",
            "cognitive health",
        ],

        "Musculoskeletal Care": [
            "musculoskeletal care",
            "msk care",
            "physical therapy",
            "orthopedic care",
            "back pain",
            "joint pain",
            "rehabilitation",
            "remote physical therapy",
            "injury recovery",
            "sports medicine",
            "movement health",
            "pain management",
        ],

        "Rehabilitation": [
            "rehabilitation",
            "physical rehabilitation",
            "occupational therapy",
            "speech therapy",
            "physical therapy",
            "post-acute care",
            "recovery care",
            "remote rehabilitation",
            "rehab platform",
            "mobility recovery",
        ],

        "Pharmacy": [
            "pharmacy",
            "digital pharmacy",
            "online pharmacy",
            "mail-order pharmacy",
            "pharmacy platform",
            "pharmacy benefits",
            "prescription delivery",
            "medication management",
            "pharmacy automation",
            "specialty pharmacy",
            "retail pharmacy",
            "prescription fulfillment",
        ],

        "Medication Management": [
            "medication management",
            "medication adherence",
            "prescription management",
            "drug adherence",
            "pill reminder",
            "medication tracking",
            "medication reconciliation",
            "prescription monitoring",
            "medication safety",
            "drug interaction monitoring",
        ],

        "Medical Devices": [
            "medical device",
            "medical devices",
            "medtech",
            "connected medical device",
            "implantable device",
            "diagnostic device",
            "therapeutic device",
            "surgical device",
            "patient monitoring device",
            "wearable medical device",
            "medical hardware",
            "clinical device",
        ],

        "Wearables": [
            "health wearable",
            "medical wearable",
            "wearable health device",
            "fitness tracker",
            "smartwatch health",
            "biosensor",
            "biometric wearable",
            "continuous monitoring device",
            "wearable diagnostics",
            "wearable sensor",
        ],

        "Diagnostics": [
            "diagnostics",
            "medical diagnostics",
            "clinical diagnostics",
            "diagnostic testing",
            "early detection",
            "screening",
            "lab testing",
            "point-of-care testing",
            "diagnostic platform",
            "molecular diagnostics",
            "imaging diagnostics",
            "rapid testing",
        ],

        "Medical Imaging": [
            "medical imaging",
            "radiology",
            "diagnostic imaging",
            "x-ray",
            "mri",
            "ct scan",
            "ultrasound",
            "pet scan",
            "radiology software",
            "image analysis",
            "imaging platform",
            "imaging diagnostics",
            "radiology workflow",
        ],

        "Pathology": [
            "pathology",
            "digital pathology",
            "anatomic pathology",
            "clinical pathology",
            "pathology imaging",
            "slide analysis",
            "laboratory pathology",
            "histology",
            "pathology diagnostics",
            "pathology workflow",
        ],

        "Laboratory Technology": [
            "laboratory technology",
            "lab software",
            "laboratory information system",
            "lis",
            "lab automation",
            "clinical laboratory",
            "diagnostic laboratory",
            "laboratory workflow",
            "sample management",
            "specimen tracking",
            "lab operations",
            "laboratory analytics",
        ],

        "Genomics": [
            "genomics",
            "genetic testing",
            "dna sequencing",
            "genome sequencing",
            "whole genome sequencing",
            "wgs",
            "genetic analysis",
            "precision genomics",
            "clinical genomics",
            "consumer genetics",
            "genomic diagnostics",
            "genetic risk",
        ],

        "Precision Medicine": [
            "precision medicine",
            "personalized medicine",
            "individualized treatment",
            "biomarker-driven care",
            "targeted therapy",
            "precision health",
            "molecular profiling",
            "patient stratification",
            "genomic medicine",
            "personalized treatment",
        ],

        "Biotechnology": [
            "biotechnology",
            "biotech",
            "life sciences",
            "biological engineering",
            "synthetic biology",
            "molecular biology",
            "cell engineering",
            "gene engineering",
            "biological therapeutics",
            "biopharmaceutical",
            "biologic drug",
            "bioengineering",
        ],

        "Drug Discovery": [
            "drug discovery",
            "therapeutic discovery",
            "small molecule discovery",
            "biologic discovery",
            "target identification",
            "compound screening",
            "lead optimization",
            "drug development",
            "preclinical research",
            "molecular design",
            "drug candidate",
            "pharmaceutical research",
        ],

        "Clinical Trials": [
            "clinical trials",
            "clinical research",
            "trial management",
            "clinical trial software",
            "patient recruitment",
            "site management",
            "decentralized clinical trial",
            "virtual clinical trial",
            "clinical data management",
            "trial monitoring",
            "clinical operations",
            "research site",
        ],

        "Pharmaceuticals": [
            "pharmaceuticals",
            "pharma",
            "pharmaceutical company",
            "drug manufacturer",
            "medication development",
            "drug commercialization",
            "pharmaceutical research",
            "prescription drug",
            "biopharma",
            "specialty pharma",
        ],

        "Therapeutics": [
            "therapeutics",
            "drug therapy",
            "biologic therapy",
            "gene therapy",
            "cell therapy",
            "rna therapy",
            "small molecule therapy",
            "targeted therapy",
            "immunotherapy",
            "digital therapeutics",
            "therapeutic platform",
        ],

        "Gene Therapy": [
            "gene therapy",
            "genetic medicine",
            "gene editing",
            "crispr",
            "genome editing",
            "viral vector",
            "non-viral delivery",
            "genetic treatment",
            "gene replacement",
            "gene silencing",
        ],

        "Cell Therapy": [
            "cell therapy",
            "stem cell therapy",
            "car-t",
            "cellular medicine",
            "regenerative medicine",
            "cell manufacturing",
            "immune cell therapy",
            "cell engineering",
            "autologous therapy",
            "allogeneic therapy",
        ],

        "Synthetic Biology": [
            "synthetic biology",
            "synbio",
            "engineered biology",
            "biofoundry",
            "biological programming",
            "genetic circuits",
            "microbial engineering",
            "protein engineering",
            "metabolic engineering",
            "biomanufacturing",
        ],

        "Healthcare AI": [
            "healthcare ai",
            "medical ai",
            "clinical ai",
            "diagnostic ai",
            "medical imaging ai",
            "clinical decision support",
            "patient risk prediction",
            "medical scribe",
            "clinical documentation ai",
            "radiology ai",
            "pathology ai",
            "drug discovery ai",
            "hospital automation",
            "care navigation ai",
        ],

        "Clinical Decision Support": [
            "clinical decision support",
            "cdss",
            "decision support system",
            "clinical recommendations",
            "treatment recommendation",
            "diagnostic support",
            "care pathway support",
            "clinical risk scoring",
            "physician decision support",
            "evidence-based medicine",
        ],

        "Medical Scribes": [
            "medical scribe",
            "ai medical scribe",
            "clinical scribe",
            "ambient documentation",
            "ambient clinical intelligence",
            "automated clinical notes",
            "visit transcription",
            "physician documentation",
            "clinical note generation",
            "doctor note automation",
        ],

        "Electronic Health Records": [
            "electronic health record",
            "ehr",
            "electronic medical record",
            "emr",
            "patient record",
            "medical record system",
            "clinical record",
            "hospital information system",
            "health information system",
            "ehr platform",
            "emr software",
        ],

        "Healthcare Interoperability": [
            "healthcare interoperability",
            "health data exchange",
            "clinical data exchange",
            "health information exchange",
            "hie",
            "fhir",
            "hl7",
            "medical data integration",
            "ehr integration",
            "patient data exchange",
            "interoperable health records",
            "clinical api",
        ],

        "Healthcare Data": [
            "healthcare data",
            "clinical data",
            "patient data",
            "medical data",
            "health data platform",
            "healthcare analytics",
            "clinical analytics",
            "real-world data",
            "real-world evidence",
            "health data infrastructure",
            "medical dataset",
            "patient registry",
        ],

        "Population Health": [
            "population health",
            "population health management",
            "community health analytics",
            "risk stratification",
            "care gap detection",
            "health outcomes",
            "preventive health",
            "patient cohort analysis",
            "public health analytics",
            "population risk",
        ],

        "Care Navigation": [
            "care navigation",
            "patient navigation",
            "healthcare navigation",
            "provider search",
            "doctor search",
            "care matching",
            "care coordination",
            "referral management",
            "patient guidance",
            "health concierge",
            "benefits navigation",
        ],

        "Hospital Operations": [
            "hospital operations",
            "hospital management",
            "clinical operations",
            "bed management",
            "capacity management",
            "staff scheduling",
            "hospital workflow",
            "operating room management",
            "patient flow",
            "hospital logistics",
            "care operations",
        ],

        "Provider Operations": [
            "provider operations",
            "practice management",
            "medical practice software",
            "clinic management",
            "provider scheduling",
            "patient scheduling",
            "appointment management",
            "medical billing",
            "practice workflow",
            "provider productivity",
        ],

        "Revenue Cycle Management": [
            "revenue cycle management",
            "rcm",
            "medical billing",
            "claims processing",
            "claims submission",
            "claims denial management",
            "coding automation",
            "medical coding",
            "insurance reimbursement",
            "patient billing",
            "payment collection",
            "prior authorization",
        ],

        "Health Insurance": [
            "health insurance",
            "health plan",
            "payer",
            "payer technology",
            "insurance administration",
            "benefits administration",
            "claims adjudication",
            "member engagement",
            "health insurance platform",
            "health coverage",
            "plan management",
        ],

        "Benefits Navigation": [
            "benefits navigation",
            "employee benefits",
            "health benefits",
            "benefits platform",
            "insurance navigation",
            "care benefits",
            "employer health benefits",
            "benefits enrollment",
            "health plan navigation",
            "benefits management",
        ],

        "Employer Health": [
            "employer health",
            "employee health",
            "workplace health",
            "corporate wellness",
            "employee wellness",
            "occupational health",
            "workforce health",
            "employee benefits",
            "employer-sponsored healthcare",
            "employee care platform",
        ],

        "Public Health": [
            "public health",
            "community health",
            "epidemiology",
            "disease surveillance",
            "outbreak monitoring",
            "health policy",
            "public health analytics",
            "population surveillance",
            "infectious disease monitoring",
            "government health",
        ],
    },

    "technologies": [
        "Electronic Health Record",
        "Electronic Medical Record",
        "EHR",
        "EMR",
        "FHIR",
        "HL7",
        "HL7 v2",
        "DICOM",
        "SMART on FHIR",
        "Health Information Exchange",
        "HIE",
        "Clinical Data Repository",
        "Master Patient Index",
        "Patient Matching",
        "Medical Terminology",
        "SNOMED CT",
        "LOINC",
        "ICD-10",
        "CPT",
        "RxNorm",
        "NDC",
        "Clinical Decision Support",
        "Clinical Rules Engine",
        "Risk Stratification",
        "Care Gap Detection",
        "Patient Registry",
        "Population Health Analytics",
        "Clinical Analytics",
        "Healthcare Data Warehouse",
        "Healthcare Data Lake",
        "Real-World Data",
        "Real-World Evidence",
        "Medical Imaging",
        "Picture Archiving and Communication System",
        "PACS",
        "Radiology Information System",
        "RIS",
        "Digital Pathology",
        "Laboratory Information System",
        "LIS",
        "Laboratory Information Management System",
        "LIMS",
        "Medical OCR",
        "Natural Language Processing",
        "Clinical NLP",
        "Ambient Clinical Intelligence",
        "Medical Speech Recognition",
        "Medical Transcription",
        "Computer-Aided Diagnosis",
        "Diagnostic AI",
        "Medical Image Segmentation",
        "Tumor Detection",
        "Radiology AI",
        "Pathology AI",
        "Predictive Analytics",
        "Patient Risk Prediction",
        "Remote Patient Monitoring",
        "RPM",
        "Internet of Medical Things",
        "IoMT",
        "Connected Medical Device",
        "Medical Wearable",
        "Biosensor",
        "Continuous Glucose Monitor",
        "CGM",
        "Electrocardiogram",
        "ECG",
        "EKG",
        "Pulse Oximetry",
        "Blood Pressure Monitoring",
        "Telemedicine Platform",
        "Video Consultation",
        "Patient Portal",
        "Provider Portal",
        "Digital Front Door",
        "Patient Engagement Platform",
        "Appointment Scheduling",
        "Medical Billing System",
        "Claims Management System",
        "Revenue Cycle Management",
        "Medical Coding",
        "Computer-Assisted Coding",
        "Prior Authorization Automation",
        "Eligibility Verification",
        "Insurance Verification",
        "Claims Adjudication",
        "Payment Integrity",
        "Fraud Waste and Abuse Detection",
        "Practice Management System",
        "Provider Credentialing",
        "Provider Directory",
        "Care Management Platform",
        "Case Management",
        "Referral Management",
        "Care Coordination",
        "Medication Management",
        "E-Prescribing",
        "Electronic Prescribing",
        "Clinical Trial Management System",
        "CTMS",
        "Electronic Data Capture",
        "EDC",
        "Electronic Patient-Reported Outcomes",
        "ePRO",
        "eConsent",
        "Randomization and Trial Supply Management",
        "RTSM",
        "Decentralized Clinical Trials",
        "Digital Biomarkers",
        "Genomic Sequencing",
        "Next-Generation Sequencing",
        "NGS",
        "Whole Genome Sequencing",
        "Whole Exome Sequencing",
        "Bioinformatics",
        "Computational Biology",
        "Molecular Modeling",
        "Protein Modeling",
        "Structure-Based Drug Design",
        "High-Throughput Screening",
        "Laboratory Automation",
        "Robotic Lab",
        "Synthetic Biology Platform",
        "CRISPR",
        "Gene Editing",
        "Gene Sequencing",
        "Cell Therapy Manufacturing",
        "Bioprocessing",
        "Biomanufacturing",
        "Digital Therapeutics",
        "Software as a Medical Device",
        "SaMD",
        "Clinical Validation",
        "HIPAA",
        "HITECH",
        "GDPR Health Data",
        "SOC 2",
        "ISO 13485",
        "FDA 510(k)",
        "FDA De Novo",
        "FDA Premarket Approval",
        "Good Clinical Practice",
        "GCP",
        "Good Manufacturing Practice",
        "GMP",
    ],

    "products": [
        "Telemedicine Platform",
        "Virtual Clinic",
        "Primary Care Platform",
        "Mental Health Platform",
        "Digital Therapy Platform",
        "Women's Health Platform",
        "Fertility Platform",
        "Men's Health Platform",
        "Pediatric Care Platform",
        "Senior Care Platform",
        "Home Health Platform",
        "Remote Patient Monitoring Platform",
        "Chronic Care Platform",
        "Diabetes Management Platform",
        "Cardiac Monitoring Platform",
        "Cancer Care Platform",
        "Physical Therapy Platform",
        "Rehabilitation Platform",
        "Digital Pharmacy",
        "Prescription Delivery Platform",
        "Medication Management Platform",
        "Medical Device",
        "Medical Wearable",
        "Diagnostic Test",
        "Diagnostic Platform",
        "Medical Imaging Platform",
        "Radiology Platform",
        "Digital Pathology Platform",
        "Laboratory Platform",
        "Genetic Testing Platform",
        "Genomics Platform",
        "Precision Medicine Platform",
        "Drug Discovery Platform",
        "Clinical Trial Platform",
        "Clinical Research Platform",
        "Therapeutics Platform",
        "Gene Therapy Platform",
        "Cell Therapy Platform",
        "Synthetic Biology Platform",
        "Healthcare AI Platform",
        "Clinical Decision Support Platform",
        "Medical Scribe",
        "Electronic Health Record",
        "Electronic Medical Record",
        "Healthcare Data Platform",
        "Interoperability Platform",
        "Population Health Platform",
        "Care Navigation Platform",
        "Patient Engagement Platform",
        "Hospital Operations Platform",
        "Practice Management Platform",
        "Revenue Cycle Management Platform",
        "Medical Billing Platform",
        "Claims Management Platform",
        "Prior Authorization Platform",
        "Health Insurance Platform",
        "Benefits Navigation Platform",
        "Employer Health Platform",
        "Public Health Platform",
    ],

    "customers": [
        "Patients",
        "Consumers",
        "Caregivers",
        "Families",
        "Physicians",
        "Doctors",
        "Nurses",
        "Clinicians",
        "Therapists",
        "Pharmacists",
        "Hospitals",
        "Health Systems",
        "Medical Practices",
        "Clinics",
        "Primary Care Practices",
        "Specialty Practices",
        "Urgent Care Centers",
        "Ambulatory Surgery Centers",
        "Diagnostic Laboratories",
        "Imaging Centers",
        "Radiology Groups",
        "Pathology Labs",
        "Pharmacies",
        "Health Insurance Companies",
        "Health Plans",
        "Payers",
        "Employers",
        "Self-Insured Employers",
        "Government Agencies",
        "Public Health Departments",
        "Pharmaceutical Companies",
        "Biotechnology Companies",
        "Medical Device Companies",
        "Clinical Research Organizations",
        "CROs",
        "Research Institutions",
        "Universities",
        "Life Sciences Companies",
        "Healthcare Administrators",
        "Revenue Cycle Teams",
        "Clinical Operations Teams",
        "Care Management Teams",
        "Benefits Teams",
        "Human Resources Teams",
    ],

    "business_models": [
        "B2B",
        "B2C",
        "B2B2C",
        "Healthcare SaaS",
        "Clinical SaaS",
        "Enterprise SaaS",
        "Provider SaaS",
        "Payer SaaS",
        "Life Sciences SaaS",
        "Subscription",
        "Monthly Subscription",
        "Annual Subscription",
        "Enterprise Contract",
        "Per-Provider Pricing",
        "Per-Clinician Pricing",
        "Per-Patient Pricing",
        "Per-Member-Per-Month",
        "PMPM",
        "Per-Visit Pricing",
        "Per-Consultation Pricing",
        "Per-Test Pricing",
        "Per-Scan Pricing",
        "Per-Claim Pricing",
        "Per-Transaction Pricing",
        "Usage-Based Pricing",
        "Licensing",
        "Software Licensing",
        "Medical Device Sales",
        "Hardware Sales",
        "Device Subscription",
        "Consumables Revenue",
        "Diagnostic Testing Revenue",
        "Lab Service Revenue",
        "Insurance Reimbursement",
        "Fee-for-Service",
        "Value-Based Care",
        "Shared Savings",
        "Risk-Based Contract",
        "Capitation",
        "Care Management Fee",
        "Clinical Trial Revenue",
        "Research Contract",
        "Drug Licensing",
        "Therapeutic Licensing",
        "Milestone Payments",
        "Royalty Revenue",
        "Data Licensing",
        "Marketplace",
        "Referral Fee",
        "Provider Network Fee",
    ],

    "competitors": [
        "Epic Systems",
        "Oracle Health",
        "Cerner",
        "Athenahealth",
        "eClinicalWorks",
        "MEDITECH",
        "NextGen Healthcare",
        "Veradigm",
        "Teladoc Health",
        "Amwell",
        "Doctor on Demand",
        "MDLive",
        "Included Health",
        "Ro",
        "Hims & Hers",
        "One Medical",
        "Carbon Health",
        "Forward",
        "K Health",
        "Zocdoc",
        "Headspace",
        "Calm",
        "Talkspace",
        "BetterHelp",
        "Lyra Health",
        "Spring Health",
        "Modern Health",
        "Maven Clinic",
        "Tia",
        "Flo Health",
        "Ovia Health",
        "Kindbody",
        "Carrot Fertility",
        "Progyny",
        "Omada Health",
        "Livongo",
        "Virta Health",
        "Lark Health",
        "Noom",
        "DarioHealth",
        "Dexcom",
        "Abbott",
        "Medtronic",
        "Philips",
        "GE HealthCare",
        "Siemens Healthineers",
        "Boston Scientific",
        "Stryker",
        "Zimmer Biomet",
        "Intuitive Surgical",
        "iRhythm",
        "ResMed",
        "Butterfly Network",
        "AliveCor",
        "Viz.ai",
        "Aidoc",
        "Tempus",
        "PathAI",
        "Freenome",
        "Guardant Health",
        "Grail",
        "Natera",
        "Invitae",
        "23andMe",
        "Illumina",
        "Foundation Medicine",
        "Flatiron Health",
        "Komodo Health",
        "Truveta",
        "HealthVerity",
        "Datavant",
        "Particle Health",
        "Redox",
        "Zus Health",
        "Innovaccer",
        "Arcadia",
        "Cedar",
        "Waystar",
        "R1 RCM",
        "Change Healthcare",
        "Availity",
        "AKASA",
        "Notable",
        "Abridge",
        "Nabla",
        "Suki",
        "Nuance",
        "Doximity",
        "Veeva Systems",
        "Medidata",
        "IQVIA",
        "Parexel",
        "ICON",
        "Labcorp",
        "Quest Diagnostics",
        "Moderna",
        "BioNTech",
        "Ginkgo Bioworks",
        "Recursion",
        "Schrodinger",
        "Insitro",
        "Exscientia",
        "Benchling",
    ],

    "yc_tags": [
        "Healthcare",
        "Health Tech",
        "Digital Health",
        "Telehealth",
        "Mental Health",
        "Women's Health",
        "Medical Devices",
        "Diagnostics",
        "Biotechnology",
        "Drug Discovery",
        "Clinical Trials",
        "Pharmaceuticals",
        "Genomics",
        "Healthcare IT",
        "Electronic Health Records",
        "Healthcare AI",
        "Medical Imaging",
        "Insurance",
        "Care Delivery",
        "Marketplace",
        "B2B",
        "SaaS",
    ],

    "github_topics": [
        "healthcare",
        "healthtech",
        "digital-health",
        "medical-software",
        "telemedicine",
        "telehealth",
        "ehr",
        "emr",
        "fhir",
        "hl7",
        "dicom",
        "clinical-data",
        "medical-imaging",
        "radiology",
        "pathology",
        "bioinformatics",
        "genomics",
        "drug-discovery",
        "biotechnology",
        "clinical-trials",
        "patient-monitoring",
        "remote-patient-monitoring",
        "medical-ai",
        "healthcare-ai",
        "clinical-nlp",
        "medical-ocr",
        "medical-device",
        "digital-therapeutics",
        "health-data",
        "population-health",
        "care-management",
        "medical-billing",
        "revenue-cycle-management",
    ],

    "problems_solved": [
        "limited access to healthcare",
        "long appointment wait times",
        "high cost of care",
        "fragmented patient records",
        "poor care coordination",
        "clinician burnout",
        "administrative burden",
        "manual clinical documentation",
        "inefficient medical billing",
        "claims denial",
        "slow prior authorization",
        "patient no-shows",
        "medication nonadherence",
        "chronic disease burden",
        "lack of remote monitoring",
        "late disease detection",
        "diagnostic errors",
        "slow medical imaging review",
        "limited specialist access",
        "mental healthcare shortages",
        "poor maternal health outcomes",
        "limited elder care support",
        "inefficient clinical trials",
        "slow patient recruitment",
        "high drug development costs",
        "drug discovery failure",
        "fragmented healthcare data",
        "lack of interoperability",
        "poor patient engagement",
        "provider scheduling inefficiency",
        "hospital capacity constraints",
        "staffing shortages",
        "fraud waste and abuse",
        "insurance complexity",
        "benefits confusion",
        "health inequity",
        "low financial transparency",
    ],

    "signals": {
        "technical_depth": 0.83,
        "enterprise_bias": 0.84,
        "consumer_bias": 0.57,
        "developer_focus": 0.38,
        "network_effect": 0.48,
        "capital_intensity": 0.78,
        "regulatory_complexity": 0.96,
        "data_advantage": 0.91,
        "clinical_validation_importance": 0.98,
        "switching_cost": 0.87,
        "reimbursement_dependency": 0.79,
        "marketplace_potential": 0.44,
    },

    "risk_indicators": {
        "regulatory": [
            "fda approval required",
            "not fda cleared",
            "unapproved medical claim",
            "clinical regulation",
            "medical device regulation",
            "drug approval risk",
            "healthcare license required",
            "state medical licensing",
            "regulatory uncertainty",
            "clinical compliance risk",
        ],

        "clinical_validation": [
            "no clinical evidence",
            "limited clinical data",
            "small clinical study",
            "unvalidated outcome",
            "no peer-reviewed research",
            "poor sensitivity",
            "poor specificity",
            "false negative risk",
            "false positive risk",
            "unproven treatment",
        ],

        "patient_safety": [
            "patient harm",
            "incorrect diagnosis",
            "incorrect treatment recommendation",
            "unsafe medical device",
            "medication error",
            "care delay",
            "clinical error",
            "device malfunction",
            "adverse event",
        ],

        "privacy_and_security": [
            "protected health information",
            "phi",
            "patient data breach",
            "hipaa violation",
            "medical record exposure",
            "weak encryption",
            "poor access controls",
            "health data leak",
            "cybersecurity incident",
        ],

        "reimbursement": [
            "no reimbursement pathway",
            "uncertain reimbursement",
            "payer dependency",
            "insurance denial",
            "low reimbursement rate",
            "coding uncertainty",
            "coverage limitation",
            "fee-for-service dependency",
        ],

        "adoption": [
            "clinician resistance",
            "workflow disruption",
            "long hospital sales cycle",
            "difficult ehr integration",
            "low patient engagement",
            "poor provider adoption",
            "training burden",
            "complex implementation",
        ],

        "capital_intensity": [
            "expensive clinical trial",
            "high research cost",
            "manufacturing cost",
            "laboratory infrastructure",
            "hardware manufacturing",
            "long development cycle",
            "regulatory filing cost",
            "high burn rate",
        ],

        "data_quality": [
            "biased clinical data",
            "incomplete patient data",
            "poor data standardization",
            "limited training data",
            "single-site dataset",
            "missing demographic representation",
            "inconsistent clinical coding",
        ],
    },

    "positive_signals": {
        "clinical_validation": [
            "peer-reviewed study",
            "clinical trial completed",
            "validated clinical outcome",
            "statistically significant",
            "high sensitivity",
            "high specificity",
            "improved patient outcome",
            "clinical evidence",
            "multi-site study",
            "randomized controlled trial",
        ],

        "regulatory_readiness": [
            "fda cleared",
            "fda approved",
            "510(k) clearance",
            "de novo authorization",
            "ce marked",
            "hipaa compliant",
            "iso 13485",
            "good clinical practice",
            "good manufacturing practice",
            "regulatory strategy",
        ],

        "provider_adoption": [
            "hospital partnership",
            "health system partnership",
            "provider network",
            "physician adoption",
            "clinical workflow integration",
            "ehr integration",
            "enterprise deployment",
            "clinical champion",
            "care team usage",
        ],

        "payer_adoption": [
            "payer partnership",
            "insurance coverage",
            "reimbursement code",
            "employer contract",
            "value-based care contract",
            "shared savings",
            "risk-based agreement",
            "covered benefit",
        ],

        "data_advantage": [
            "proprietary clinical dataset",
            "longitudinal patient data",
            "real-world evidence",
            "multi-institutional data",
            "exclusive data partnership",
            "clinical feedback loop",
            "high-quality labeled data",
            "large patient registry",
        ],

        "workflow_depth": [
            "system of record",
            "mission critical",
            "embedded clinical workflow",
            "care coordination platform",
            "clinical decision support",
            "deep ehr integration",
            "high switching cost",
            "multi-year hospital contract",
        ],

        "outcomes": [
            "reduced hospital admissions",
            "reduced readmissions",
            "lower cost of care",
            "improved medication adherence",
            "faster diagnosis",
            "shorter wait time",
            "improved clinical outcome",
            "reduced clinician burden",
        ],

        "security_readiness": [
            "soc 2",
            "soc2",
            "hipaa",
            "hitust",
            "iso 27001",
            "encryption at rest",
            "encryption in transit",
            "role-based access control",
            "audit logs",
            "penetration testing",
        ],
    },
}


def _deduplicate(values: list[str]) -> list[str]:
    """
    Return a case-insensitive, order-preserving list of unique strings.
    """

    seen: set[str] = set()
    result: list[str] = []

    for value in values:
        if not isinstance(value, str):
            raise TypeError(
                "Ontology list entries must be strings. "
                f"Received {type(value).__name__}: {value!r}"
            )

        cleaned = value.strip()
        normalized = cleaned.casefold()

        if cleaned and normalized not in seen:
            seen.add(normalized)
            result.append(cleaned)

    return result


def _deduplicate_nested_lists(
    mapping: dict[str, list[str]],
) -> dict[str, list[str]]:
    """
    Deduplicate every list stored in a string-to-list dictionary.
    """

    return {
        name: _deduplicate(values)
        for name, values in mapping.items()
    }


def _normalize_healthcare_ontology() -> None:
    """
    Remove duplicate values throughout the healthcare ontology.
    """

    list_fields = [
        "aliases",
        "technologies",
        "products",
        "customers",
        "business_models",
        "competitors",
        "yc_tags",
        "github_topics",
        "problems_solved",
    ]

    for field in list_fields:
        values = HEALTHCARE[field]

        if not isinstance(values, list):
            raise TypeError(
                f"HEALTHCARE[{field!r}] must be a list."
            )

        HEALTHCARE[field] = _deduplicate(values)

    nested_fields = [
        "subindustries",
        "risk_indicators",
        "positive_signals",
    ]

    for field in nested_fields:
        values = HEALTHCARE[field]

        if not isinstance(values, dict):
            raise TypeError(
                f"HEALTHCARE[{field!r}] must be a dictionary."
            )

        HEALTHCARE[field] = _deduplicate_nested_lists(values)


def validate_healthcare_ontology() -> None:
    """
    Raise an error if the healthcare ontology has an invalid structure.
    """

    required_fields = {
        "name",
        "aliases",
        "subindustries",
        "technologies",
        "products",
        "customers",
        "business_models",
        "competitors",
        "yc_tags",
        "github_topics",
        "problems_solved",
        "signals",
        "risk_indicators",
        "positive_signals",
    }

    missing_fields = required_fields.difference(HEALTHCARE)

    if missing_fields:
        raise ValueError(
            "Healthcare ontology is missing required fields: "
            f"{sorted(missing_fields)}"
        )

    if HEALTHCARE["name"] != "Healthcare":
        raise ValueError(
            "HEALTHCARE['name'] must be 'Healthcare'."
        )

    if not isinstance(HEALTHCARE["aliases"], list):
        raise TypeError(
            "HEALTHCARE['aliases'] must be a list."
        )

    if not HEALTHCARE["aliases"]:
        raise ValueError(
            "The healthcare ontology must contain aliases."
        )

    if not isinstance(HEALTHCARE["subindustries"], dict):
        raise TypeError(
            "HEALTHCARE['subindustries'] must be a dictionary."
        )

    if not HEALTHCARE["subindustries"]:
        raise ValueError(
            "The healthcare ontology must contain subindustries."
        )

    for subindustry_name, terms in HEALTHCARE[
        "subindustries"
    ].items():
        if not isinstance(subindustry_name, str):
            raise TypeError(
                "Every healthcare subindustry name must be a string."
            )

        if not isinstance(terms, list):
            raise TypeError(
                f"Subindustry {subindustry_name!r} "
                "must contain a list."
            )

        if not terms:
            raise ValueError(
                f"Subindustry {subindustry_name!r} has no terms."
            )

    if not isinstance(HEALTHCARE["signals"], dict):
        raise TypeError(
            "HEALTHCARE['signals'] must be a dictionary."
        )

    for signal_name, signal_value in HEALTHCARE[
        "signals"
    ].items():
        if not isinstance(signal_name, str):
            raise TypeError(
                "Signal names must be strings."
            )

        if not isinstance(signal_value, (int, float)):
            raise TypeError(
                f"Signal {signal_name!r} must be numeric."
            )

        if not 0 <= signal_value <= 1:
            raise ValueError(
                f"Signal {signal_name!r} must be between 0 and 1."
            )

    for field in ("risk_indicators", "positive_signals"):
        groups = HEALTHCARE[field]

        if not isinstance(groups, dict):
            raise TypeError(
                f"HEALTHCARE[{field!r}] must be a dictionary."
            )

        for group_name, terms in groups.items():
            if not isinstance(group_name, str):
                raise TypeError(
                    f"Every key in HEALTHCARE[{field!r}] "
                    "must be a string."
                )

            if not isinstance(terms, list):
                raise TypeError(
                    f"HEALTHCARE[{field!r}]"
                    f"[{group_name!r}] must be a list."
                )


_normalize_healthcare_ontology()
validate_healthcare_ontology()