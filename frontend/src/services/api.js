import axios from "axios";

const BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000/api/v1";

const api = axios.create({ baseURL: BASE_URL, timeout: 30000, headers: { "Content-Type": "application/json" } });

api.interceptors.response.use(
  (res) => res,
  (err) => {
    const message = err?.response?.data?.detail || err?.message || "An unexpected error occurred.";
    return Promise.reject(new Error(message));
  }
);

export const uploadResume = async (file) => {
  const form = new FormData();
  form.append("file", file);
  const res = await api.post("/upload-resume", form, { headers: { "Content-Type": "multipart/form-data" } });
  return res.data;
};

export const generateQuestions = async ({ resumeId, topic, difficulty, numQuestions = 5 }) => {
  const res = await api.post("/generate-questions", { resume_id: resumeId, topic, difficulty, num_questions: numQuestions });
  return res.data;
};

export const evaluateAnswer = async ({ questionId, sessionId, userAnswer }) => {
  const res = await api.post("/evaluate-answer", { question_id: questionId, session_id: sessionId, user_answer: userAnswer });
  return res.data;
};

export const getResults = async (sessionId) => {
  const res = await api.get(`/results/${sessionId}`);
  return res.data;
};

export default api;
