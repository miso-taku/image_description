export type DetailLevel = "brief" | "standard" | "detailed";

export interface DescriptionResponse {
  description: string;
  detail: DetailLevel;
  model: string;
  request_id: string;
}

export interface ApiErrorBody {
  error: {
    code: string;
    message: string;
    request_id?: string | null;
  };
}
