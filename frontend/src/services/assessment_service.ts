import { SecurityAssessmentInput, SecurityAssessmentResult } from '@/types/assessment';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class AssessmentService {
  static async performAssessment(input: SecurityAssessmentInput): Promise<SecurityAssessmentResult> {
    try {
      const response = await fetch(`${API_URL}/api/v1/assess`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify(input),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: 'Unknown error' }));
        throw new Error(`Assessment failed: ${errorData.message || 'Unknown error'}`);
      }

      const result = await response.json();
      return result;
    } catch (error) {
      console.error('Error performing assessment:', error);
      throw error;
    }
  }
} 