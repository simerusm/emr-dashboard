import type { EMRSection } from "./types"

export async function getProcessedEMR(): Promise<EMRSection[]> {
  // In a real application, this function would:
  // 1. Fetch the original EMR from a database or file system
  // 2. Process it through an LLM to get suggested changes
  // 3. Structure the data with the changes

  // Mock Data
  return [
    {
      title: "Patient Information",
      content: [
        "Name: John Doe\nDOB: 01/15/1980\nGender: Male\n",
        {
          original: "Weight: 180 lbs",
          suggested: "Weight: 82 kg",
          reason: "Converting to metric system for consistency",
        },
        "\nHeight: 5'11\"",
      ],
    },
    {
      title: "Chief Complaint",
      content: [
        "Patient presents with ",
        {
          original: "headache and fatigue",
          suggested: "severe migraine and extreme fatigue",
          reason: "More specific description based on patient's reported symptoms",
        },
        " lasting for the past 3 days.",
      ],
    },
    {
      title: "Medical History",
      content: [
        "No significant medical history.\n",
        {
          original: "Patient denies any allergies.",
          suggested: "Patient reports mild lactose intolerance.",
          reason: "Updated based on recent patient disclosure",
        },
      ],
    },
    {
      title: "Assessment and Plan",
      content: [
        "Diagnosis: ",
        {
          original: "Tension headache",
          suggested: "Chronic migraine",
          reason: "Updated based on symptom severity and duration",
        },
        "\n\nTreatment plan:\n1. ",
        {
          original: "Prescribe over-the-counter pain relievers",
          suggested: "Prescribe sumatriptan 50mg as needed for acute attacks",
          reason: "More appropriate medication for migraine treatment",
        },
        "\n2. Recommend lifestyle changes including stress reduction techniques and regular exercise\n3. Follow-up appointment in 2 weeks",
      ],
    },
  ]
}

