import type { EMRSection } from "./types"

export async function getProcessedEMR(): Promise<EMRSection[]> {
  // In a real application, this function would:
  // 1. Fetch the original EMR from a database or file system
  // 2. Process it through an LLM to get suggested changes
  // 3. Structure the data with the changes

  // Mock Data
  return [
        {
            "title": "Chief Complaint",
            "content": [
                {
                    "original": "headache and neck stiffness",
                    "suggested": "Headache and neck stiffness",
                    "reason": "Capitalization for consistency with section titles."
                }
            ]
        },
        {
            "title": "Major Surgical or Invasive Procedure",
            "content": [
                {
                    "original": "central line placed, arterial line placed",
                    "suggested": "Central line placement, arterial line placement",
                    "reason": "Consistent noun form (placement) improves clarity."
                }
            ]
        },
        {
            "title": "History of Present Illness",
            "content": [
                "54 year old female with recent diagnosis of ulcerative colitis on 6-mercaptopurine, prednisone 40-60 mg daily, who presents with a new onset of headache and neck stiffness.",
                {
                    "original": "The patient is in distress, rigoring and has aphasia and only limited history is obtained.",
                    "suggested": "The patient is in distress, experiencing rigors, and has aphasia, so only a limited history is obtained.",
                    "reason": "Improved syntax for clarity and readability."
                },
                {
                    "original": "She reports that she was awaken 1AM the morning of [**2147-11-16*\"] with a headache which she describes as bandlike.",
                    "suggested": "She reports that she was awoken at 1 AM on the morning of November 16, 2147, with a headache which she describes as band-like.",
                    "reason": "Corrected grammatical errors and formatted date for readability."
                },
                {
                    "original": "she states that headaches are unusual for her.",
                    "suggested": "She states that headaches are unusual for her.",
                    "reason": "Capitalization for consistency."
                },
                {
                    "original": "She denies photo- or phonophobia, She did have neck stiffness.",
                    "suggested": "She denies photophobia or phonophobia. She did have neck stiffness.",
                    "reason": "Corrected punctuation for clarity."
                },
                {
                    "original": "on arrival to the £D at 5:33PM, she was afebrile with a temp of 96.5, however she later spiked with temp to 104.4 (rectal), HR 91, 8P 112/54, RR 24, 02 sat 100 %.",
                    "suggested": "On arrival to the ED at 5:33 PM, she was afebrile with a temperature of 96.5°F, however, she later spiked a temperature of 104.4°F (rectal), HR 91 bpm, BP 112/54 mmHg, RR 24 breaths/min, O2 sat 100%.",
                    "reason": "Corrected typographical errors and standardized medical abbreviations and units for clarity."
                },
                {
                    "original": "Head CT was done and relealved attenuation within the subcortical white matter of the right medial frontal lobe.",
                    "suggested": "Head CT was done and revealed attenuation within the subcortical white matter of the right medial frontal lobe.",
                    "reason": "Corrected spelling for clarity and accuracy."
                },
                {
                    "original": "LP was performed showing opening pressure 24 cm H20 WBC of 316, Protein 152, glucose 16.",
                    "suggested": "Lumbar puncture (LP) was performed showing an opening pressure of 24 cm H2O, WBC 316, protein 152 mg/dL, glucose 16 mg/dL.",
                    "reason": "Expanded abbreviations for clarity and added units of measurement."
                },
                "She was given vancomycin 1 gm IV, Ceftriaxone 2 gm IV, Acyclovir 10 mg IV, Ambesone 183 mg IV, Ampicillin 2 gm IV q 4 hours, Morphine 2-4 mg q 4-6 hours, Tylenol 1 gm, Decadron 10 mg IV.",
                "The patient was evaluated by Neuro in the ED.",
                {
                    "original": "Of note, the patient was recently diagnosed with uc and was started on 6MP and a prednisone taper along with steroid enemas for UC treatment.",
                    "suggested": "Notably, the patient was recently diagnosed with ulcerative colitis (UC) and was started on 6-mercaptopurine (6MP) and a prednisone taper along with steroid enemas for UC treatment.",
                    "reason": "Expanded abbreviations for clarity."
                },
                {
                    "original": "She was on Bactrim in past but stopped taking it for unclear reasons and unclear how long ago.|",
                    "suggested": "She was on Bactrim in the past but stopped taking it for unclear reasons and it's unclear how long ago.",
                    "reason": "Improved phrase clarity and removed extraneous character at the end."
                }
            ]
        },
        {
            "title": "Past Medical History",
            "content": [
                "Chronic back pain, MRI negative",
                {
                    "original": "osteopenia - fosamax d/c by PcP",
                    "suggested": "Osteopenia - Fosamax discontinued by PCP",
                    "reason": "Capitalization and expanded abbreviation for clarity."
                },
                "Leg pain/parasthesias",
                "History of hiatal hernia"
            ]
        },
        {
            "title": "Social History",
            "content": [
                {
                    "original": "No tob, Etoh. Patient lives alone in a 2 family home w/a friend. She is an administrative assistant",
                    "suggested": "No tobacco or ethanol use. Patient lives alone in a 2-family home with a friend. She is an administrative assistant.",
                    "reason": "Expanded abbreviations for clarity and corrected punctuation."
                }
            ]
        },
        {
            "title": "Family History",
            "content": [
                {
                    "original": "brother w/ ulcerative proctitis, mother w/ severe arthritis, father w/ h/o colon polyps and GERD",
                    "suggested": "Brother with ulcerative proctitis, mother with severe arthritis, father with history of colon polyps and GERD.",
                    "reason": "Expanded abbreviations for clarity and corrected punctuation."
                }
            ]
        },
        {
            "title": "Physical Exam",
            "content": [
                "Physical examination details are not provided in the text."
            ]
        }
    ]
}



