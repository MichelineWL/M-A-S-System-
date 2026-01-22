import axios from "axios";

const API_BASE_URL = "http://localhost:8000/api";

export interface ExecutionStep {
  step_number: number;
  description: string;
  reasoning: string;
}

export interface ExecutionPlan {
  query_understanding: string;
  thinking?: string;
  steps: ExecutionStep[];
  expected_output_type: string;
  requires_visualization: boolean;
  visualization_type?: string;
}

export interface PlotlyJson {
  data: any[];
  layout: any;
}

export interface Visualization {
  chart_type: string;
  plotly_json: PlotlyJson;
  title: string;
  description: string;
}

export interface ExecutionResult {
  success: boolean;
  answer: string;
  code_executed?: string;
  visualization?: Visualization;
  error?: string;
}

export interface QueryResponse {
  session_id: string;
  query: string;
  plan: ExecutionPlan;
  result: ExecutionResult;
  timestamp: string;
}

export interface UploadResponse {
  session_id: string;
  filename: string;
  data_schema: any;
  message: string;
}

export const api = {
  uploadFile: async (file: File): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append("file", file);

    const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  },

  query: async (
    sessionId: string,
    query: string,
    modelName?: string,
  ): Promise<QueryResponse> => {
    const response = await axios.post(`${API_BASE_URL}/query`, {
      session_id: sessionId,
      query: query,
      model_name: modelName || "gemini-2.0-flash",
    });
    return response.data;
  },

  getHistory: async (sessionId: string) => {
    const response = await axios.get(`${API_BASE_URL}/history/${sessionId}`);
    return response.data;
  },
};
