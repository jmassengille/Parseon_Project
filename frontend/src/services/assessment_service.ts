import { AssessmentFormData, AssessmentResult } from '@/types/assessment';

export class AssessmentService {
  private static API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  static async performAssessment(input: AssessmentFormData): Promise<AssessmentResult> {
    try {
      const response = await fetch(`${this.API_URL}/api/v1/assess`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(input),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to perform assessment');
      }

      return await response.json();
    } catch (error) {
      console.error('Error performing assessment:', error);
      throw error;
    }
  }
} 