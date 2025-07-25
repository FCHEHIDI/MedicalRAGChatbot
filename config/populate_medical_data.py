"""
Medical Knowledge Base Ingestion Script
=====================================

This script populates the RAG system with comprehensive medical data
to provide evidence-based responses for medical questions.
"""

import requests
import json
from pathlib import Path

# Medical data to populate the RAG system
MEDICAL_KNOWLEDGE = [
    {
        "content": """
        Hypertension (High Blood Pressure):
        
        Definition: Blood pressure consistently above 140/90 mmHg
        
        Symptoms:
        - Often asymptomatic (silent killer)
        - Headaches (severe cases)
        - Shortness of breath
        - Chest pain
        - Visual changes
        - Fatigue
        
        Risk Factors:
        - Age (>65 years)
        - Family history
        - Obesity (BMI >30)
        - High sodium diet
        - Sedentary lifestyle
        - Smoking
        - Excessive alcohol consumption
        - Diabetes
        - Sleep apnea
        
        Complications:
        - Heart attack
        - Stroke
        - Heart failure
        - Kidney disease
        - Vision loss
        - Peripheral artery disease
        
        Management:
        - Lifestyle modifications (diet, exercise)
        - ACE inhibitors (lisinopril, enalapril)
        - ARBs (losartan, valsartan)
        - Diuretics (hydrochlorothiazide)
        - Beta-blockers (metoprolol, atenolol)
        - Calcium channel blockers (amlodipine)
        
        Target BP: <130/80 mmHg for most adults
        """,
        "filename": "hypertension_guidelines.md",
        "metadata": {"category": "cardiovascular", "condition": "hypertension", "source": "clinical_guidelines"}
    },
    {
        "content": """
        Type 2 Diabetes Mellitus:
        
        Definition: Chronic metabolic disorder characterized by insulin resistance and relative insulin deficiency
        
        Diagnostic Criteria:
        - Fasting glucose ≥126 mg/dL (7.0 mmol/L)
        - Random glucose ≥200 mg/dL (11.1 mmol/L) with symptoms
        - HbA1c ≥6.5% (48 mmol/mol)
        - 2-hour OGTT ≥200 mg/dL (11.1 mmol/L)
        
        Symptoms:
        - Polyuria (frequent urination)
        - Polydipsia (excessive thirst)
        - Polyphagia (increased hunger)
        - Unexplained weight loss
        - Fatigue
        - Blurred vision
        - Slow-healing wounds
        - Recurrent infections
        
        Risk Factors:
        - Age ≥45 years
        - BMI ≥25 kg/m²
        - Family history
        - Sedentary lifestyle
        - History of gestational diabetes
        - PCOS
        - Prediabetes
        
        Complications:
        - Diabetic retinopathy
        - Diabetic nephropathy
        - Diabetic neuropathy
        - Cardiovascular disease
        - Stroke
        - Diabetic ketoacidosis (rare in T2DM)
        
        Management:
        - Lifestyle modifications (diet, exercise)
        - Metformin (first-line)
        - Sulfonylureas (glyburide, glipizide)
        - SGLT-2 inhibitors (empagliflozin)
        - GLP-1 agonists (semaglutide)
        - Insulin (advanced cases)
        
        Target HbA1c: <7% for most adults
        """,
        "filename": "diabetes_type2_management.md",
        "metadata": {"category": "endocrine", "condition": "diabetes", "source": "ADA_guidelines"}
    },
    {
        "content": """
        Chest Pain Evaluation:
        
        Red Flags (Immediate attention required):
        - Crushing, squeezing chest pain
        - Pain radiating to arm, jaw, neck
        - Associated shortness of breath
        - Diaphoresis (sweating)
        - Nausea/vomiting
        - Lightheadedness
        - Pain lasting >15 minutes
        
        Differential Diagnosis:
        1. Acute Coronary Syndrome (ACS)
           - ST-elevation MI (STEMI)
           - Non-ST elevation MI (NSTEMI)
           - Unstable angina
        
        2. Other Cardiac Causes:
           - Stable angina
           - Pericarditis
           - Aortic dissection
           - Pulmonary embolism
        
        3. Non-cardiac Causes:
           - Gastroesophageal reflux
           - Musculoskeletal pain
           - Anxiety/panic disorder
           - Pneumonia
           - Pneumothorax
        
        Initial Assessment:
        - ECG within 10 minutes
        - Troponin levels
        - Chest X-ray
        - Complete blood count
        - Basic metabolic panel
        - D-dimer (if PE suspected)
        
        Management:
        - MONA protocol for ACS (Morphine, Oxygen, Nitroglycerin, Aspirin)
        - Antiplatelet therapy
        - Anticoagulation
        - Beta-blockers
        - ACE inhibitors
        - Statins
        
        Emergency: Call 911 for severe chest pain
        """,
        "filename": "chest_pain_evaluation.md",
        "metadata": {"category": "emergency", "condition": "chest_pain", "source": "AHA_guidelines"}
    },
    {
        "content": """
        Common Drug Interactions and Contraindications:
        
        Warfarin Interactions:
        - Antibiotics (increase INR)
        - NSAIDs (bleeding risk)
        - Alcohol (variable effect)
        - Green leafy vegetables (decrease effect)
        - Cranberry juice (increase effect)
        
        ACE Inhibitor Contraindications:
        - Pregnancy
        - Bilateral renal artery stenosis
        - Hyperkalemia (K+ >5.5)
        - Angioedema history
        
        Metformin Contraindications:
        - Kidney disease (eGFR <30)
        - Liver disease
        - Heart failure (NYHA Class III-IV)
        - Alcohol abuse
        - Contrast procedures (hold 48h)
        
        Statin Side Effects:
        - Myopathy (muscle pain)
        - Rhabdomyolysis (rare but serious)
        - Liver enzyme elevation
        - Diabetes risk (slight increase)
        
        Beta-blocker Contraindications:
        - Asthma/COPD (relative)
        - Heart block (2nd/3rd degree)
        - Severe heart failure
        - Bradycardia (<50 bpm)
        
        NSAID Warnings:
        - Cardiovascular risk
        - GI bleeding
        - Kidney dysfunction
        - Avoid with ACE inhibitors
        """,
        "filename": "drug_interactions.md",
        "metadata": {"category": "pharmacology", "condition": "drug_safety", "source": "FDA_guidelines"}
    }
]

def populate_rag_system():
    """Add medical knowledge to the RAG system"""
    base_url = "http://localhost:8000"
    
    print("🩺 Populating Medical RAG System...")
    print("=" * 50)
    
    for i, item in enumerate(MEDICAL_KNOWLEDGE, 1):
        try:
            response = requests.post(
                f"{base_url}/documents",
                json=item,
                timeout=30
            )
            if response.status_code == 200:
                print(f"✅ Added: {item['filename']}")
            else:
                print(f"❌ Failed: {item['filename']} - {response.text}")
        except Exception as e:
            print(f"❌ Error adding {item['filename']}: {e}")
    
    print("=" * 50)
    
    # Test the system
    print("🧪 Testing RAG System...")
    test_questions = [
        "What are the symptoms of hypertension?",
        "How is type 2 diabetes diagnosed?",
        "What should I do if I have chest pain?"
    ]
    
    for question in test_questions:
        try:
            response = requests.post(
                f"{base_url}/chat",
                json={"message": question},
                timeout=60
            )
            if response.status_code == 200:
                data = response.json()
                print(f"\n📝 Q: {question}")
                print(f"🤖 A: {data['response'][:200]}...")
                print(f"📚 Sources: {len(data.get('sources', []))}")
            else:
                print(f"❌ Test failed: {response.text}")
        except Exception as e:
            print(f"❌ Test error: {e}")

if __name__ == "__main__":
    populate_rag_system()
